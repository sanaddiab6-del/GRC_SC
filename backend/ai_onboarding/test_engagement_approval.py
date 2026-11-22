from contextlib import nullcontext
from types import SimpleNamespace
from unittest.mock import Mock, patch
from uuid import uuid4

from django.http import Http404
from django.test import SimpleTestCase
from rest_framework.test import APIRequestFactory, force_authenticate

from ai_onboarding.engagement_approval_views import AiEngagementApprovalView
from ai_onboarding.engagement_rules import STAGES_BY_NAME
from ai_onboarding.engagement_service import EngagementBlocked, execute_stage


class EngagementApprovalTests(SimpleTestCase):
    def setUp(self):
        self.user = SimpleNamespace(pk="test-user", is_authenticated=True)
        self.stage = next(iter(STAGES_BY_NAME))
        self.engagement_id = uuid4()
        self.receipt = Mock()
        self.receipt.prepared_digest = "a" * 64
        self.receipt.prepared_result = {"status": "prepared"}
        self.receipt.approved_by_id = ""

    def post(self, digest=None, reviewed=True):
        request = APIRequestFactory().post(
            "/approval/",
            {
                "stage": self.stage,
                "batch_key": "test-batch",
                "prepared_digest": digest or ("a" * 64),
                "confirm_reviewed": reviewed,
            },
            format="json",
        )
        force_authenticate(request, user=self.user)
        return request

    def test_valid_review_records_approver(self):
        with (
            patch(
                "ai_onboarding.engagement_approval_views.get_prepared_receipt",
                return_value=self.receipt,
            ),
            patch(
                "ai_onboarding.engagement_approval_views.transaction.atomic",
                return_value=nullcontext(),
            ),
        ):
            response = AiEngagementApprovalView.as_view()(
                self.post(), engagement_id=self.engagement_id
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.receipt.approved_by_id, "test-user")
        self.receipt.save.assert_called_once()

    def test_modified_digest_is_rejected(self):
        with (
            patch(
                "ai_onboarding.engagement_approval_views.get_prepared_receipt",
                return_value=self.receipt,
            ),
            patch(
                "ai_onboarding.engagement_approval_views.transaction.atomic",
                return_value=nullcontext(),
            ),
        ):
            response = AiEngagementApprovalView.as_view()(
                self.post(digest="b" * 64),
                engagement_id=self.engagement_id,
            )

        self.assertEqual(response.status_code, 409)
        self.receipt.save.assert_not_called()

    def test_unconfirmed_review_is_rejected(self):
        response = AiEngagementApprovalView.as_view()(
            self.post(reviewed=False),
            engagement_id=self.engagement_id,
        )
        self.assertEqual(response.status_code, 400)

    def test_inaccessible_engagement_is_rejected(self):
        request = APIRequestFactory().get(
            "/approval/",
            {"stage": self.stage, "batch_key": "test-batch"},
        )
        force_authenticate(request, user=self.user)

        with patch(
            "ai_onboarding.engagement_approval_views.get_prepared_receipt",
            side_effect=Http404,
        ):
            response = AiEngagementApprovalView.as_view()(
                request, engagement_id=self.engagement_id
            )

        self.assertEqual(response.status_code, 404)

    def test_grc_commit_remains_disabled(self):
        with self.assertRaises(EngagementBlocked) as captured:
            execute_stage(
                SimpleNamespace(user=self.user),
                self.engagement_id,
                stage=self.stage,
                batch_key="test-batch",
                mode="commit",
                payload={"dry_run": False},
                explicitly_approved=True,
            )
        self.assertEqual(captured.exception.http_status, 403)
