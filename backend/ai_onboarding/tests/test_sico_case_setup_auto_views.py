import unittest
from types import SimpleNamespace
from unittest.mock import patch
from uuid import uuid4

from django.http import Http404
from django.urls import reverse
from rest_framework.test import APIRequestFactory, force_authenticate

from ai_onboarding.sico_case_setup_views import (
    SicoCaseSetupAutoPrepareView,
)
from ai_onboarding.sico_case_setup_proposal import SicoProposalError


class SicoAutoPrepareViewTests(unittest.TestCase):

    def setUp(self):
        self.factory = APIRequestFactory()
        self.engagement_id = uuid4()
        self.user = SimpleNamespace(
            pk=uuid4(),
            is_authenticated=True,
        )
        self.path = "/test/auto-prepare/"
        self.payload = {"batch_key": "auto_case_01"}

    def post(self, data=None, authenticated=True):
        request = self.factory.post(
            self.path,
            self.payload if data is None else data,
            format="json",
        )
        if authenticated:
            force_authenticate(request, user=self.user)
        return SicoCaseSetupAutoPrepareView.as_view()(
            request,
            engagement_id=self.engagement_id,
        )

    @patch(
        "ai_onboarding.sico_case_setup_views.prepare_case_setup_from_engagement"
    )
    def test_authenticated_request_calls_builder(self, builder):
        builder.return_value = {
            "execution_performed": False,
            "writes_to_grc_records": False,
            "requires_human_review": True,
            "preparation": {"mode": "dry_run"},
        }

        response = self.post()

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.data["execution_performed"])
        self.assertFalse(response.data["writes_to_grc_records"])
        self.assertTrue(response.data["requires_human_review"])
        builder.assert_called_once()
        self.assertEqual(
            builder.call_args.kwargs["batch_key"],
            "auto_case_01",
        )

    @patch(
        "ai_onboarding.sico_case_setup_views.prepare_case_setup_from_engagement"
    )
    def test_anonymous_user_is_blocked(self, builder):
        response = self.post(authenticated=False)
        self.assertIn(response.status_code, (401, 403))
        builder.assert_not_called()

    @patch(
        "ai_onboarding.sico_case_setup_views.prepare_case_setup_from_engagement"
    )
    def test_cannot_submit_ids_or_approval(self, builder):
        response = self.post({
            "batch_key": "auto_case_01",
            "explicitly_approved": True,
            "framework_id": str(uuid4()),
        })
        self.assertEqual(response.status_code, 400)
        builder.assert_not_called()

    @patch(
        "ai_onboarding.sico_case_setup_views.prepare_case_setup_from_engagement"
    )
    def test_inaccessible_engagement_returns_404(self, builder):
        builder.side_effect = Http404("Not accessible")
        response = self.post()
        self.assertEqual(response.status_code, 404)

    @patch(
        "ai_onboarding.sico_case_setup_views.prepare_case_setup_from_engagement"
    )
    def test_missing_framework_returns_400(self, builder):
        builder.side_effect = SicoProposalError(
            "Select an authorized framework."
        )
        response = self.post()
        self.assertEqual(response.status_code, 400)

    def test_route_is_registered(self):
        route = reverse(
            "sico-engagement-case-setup-auto-prepare",
            kwargs={"engagement_id": self.engagement_id},
        )
        self.assertIn(
            "/case-setup/auto-prepare/",
            route,
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)