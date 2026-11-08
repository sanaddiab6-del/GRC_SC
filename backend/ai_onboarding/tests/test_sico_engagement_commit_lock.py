"""Fail-closed SICO engagement commit API tests.

These tests do not connect to a database.
"""

import unittest
from types import SimpleNamespace
from unittest.mock import patch
from uuid import uuid4

from rest_framework.test import APIRequestFactory, force_authenticate

from ai_onboarding.engagement_views import AiEngagementOperationView


class SicoEngagementCommitLockTests(unittest.TestCase):

    def setUp(self):
        self.factory = APIRequestFactory()
        self.engagement_id = uuid4()
        self.user = SimpleNamespace(
            pk=uuid4(),
            is_authenticated=True,
        )

    def post(self, *, mode, approval):
        request = self.factory.post(
            "/test/engagement/operation/",
            {
                "stage": "case_setup",
                "batch_key": "security_lock_01",
                "mode": mode,
                "explicitly_approved": approval,
                "operation_payload": {
                    "dry_run": mode == "dry_run",
                    "approved_by_user": approval,
                },
            },
            format="json",
        )
        force_authenticate(request, user=self.user)
        return AiEngagementOperationView.as_view()(
            request,
            engagement_id=self.engagement_id,
        )

    @patch(
        "ai_onboarding.engagement_views.execute_stage"
    )
    def test_commit_with_approval_flags_is_denied(self, execute):
        response = self.post(mode="commit", approval=True)

        self.assertEqual(response.status_code, 403)
        execute.assert_not_called()

    @patch(
        "ai_onboarding.engagement_views.execute_stage"
    )
    def test_commit_without_approval_is_denied(self, execute):
        response = self.post(mode="commit", approval=False)

        self.assertIn(response.status_code, (400, 403))
        execute.assert_not_called()

    @patch(
        "ai_onboarding.engagement_views.execute_stage"
    )
    def test_dry_run_still_routes_to_coordinator(self, execute):
        execute.return_value = {
            "mode": "dry_run",
            "stage": "case_setup",
            "replay": False,
        }

        response = self.post(mode="dry_run", approval=False)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["mode"], "dry_run")
        execute.assert_called_once()

        self.assertEqual(
            execute.call_args.kwargs["mode"],
            "dry_run",
        )
        self.assertIs(
            execute.call_args.kwargs["explicitly_approved"],
            False,
        )


class SicoCoordinatorCommitLockTests(unittest.TestCase):
    """Direct coordinator calls must not bypass the API security lock."""

    def make_request(self):
        return SimpleNamespace(
            user=SimpleNamespace(
                pk=uuid4(),
                is_authenticated=True,
            )
        )

    @patch("ai_onboarding.engagement_service._validate_payload")
    def test_direct_commit_with_approval_flags_is_blocked(self, validator):
        from ai_onboarding.engagement_service import (
            EngagementBlocked,
            execute_stage,
        )

        with self.assertRaises(EngagementBlocked) as caught:
            execute_stage(
                self.make_request(),
                uuid4(),
                stage="case_setup",
                batch_key="direct_approval_bypass",
                mode="commit",
                payload={
                    "dry_run": False,
                    "approved_by_user": True,
                    "human_approved": True,
                },
                explicitly_approved=True,
            )

        self.assertEqual(caught.exception.http_status, 403)
        validator.assert_not_called()

    @patch("ai_onboarding.engagement_service._validate_payload")
    def test_direct_commit_without_approval_is_blocked(self, validator):
        from ai_onboarding.engagement_service import (
            EngagementBlocked,
            execute_stage,
        )

        with self.assertRaises(EngagementBlocked) as caught:
            execute_stage(
                self.make_request(),
                uuid4(),
                stage="case_setup",
                batch_key="direct_commit_without_approval",
                mode="commit",
                payload={"dry_run": False},
                explicitly_approved=False,
            )

        self.assertEqual(caught.exception.http_status, 403)
        validator.assert_not_called()

    @patch(
        "ai_onboarding.engagement_service._validate_payload",
        side_effect=RuntimeError("dry-run validation reached"),
    )
    def test_direct_dry_run_still_reaches_validation(self, validator):
        from ai_onboarding.engagement_service import execute_stage

        with self.assertRaisesRegex(
            RuntimeError,
            "dry-run validation reached",
        ):
            execute_stage(
                self.make_request(),
                uuid4(),
                stage="case_setup",
                batch_key="direct_dry_run",
                mode="dry_run",
                payload={"dry_run": True},
                explicitly_approved=False,
            )

        validator.assert_called_once()

if __name__ == "__main__":
    unittest.main(verbosity=2)