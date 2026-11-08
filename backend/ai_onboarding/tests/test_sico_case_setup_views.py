import unittest
from types import SimpleNamespace
from unittest.mock import patch
from uuid import uuid4

from django.http import Http404
from rest_framework.test import (
    APIRequestFactory,
    force_authenticate,
)

from ai_onboarding.sico_case_setup_views import (
    SicoCaseSetupPrepareView,
)


class SicoCaseSetupViewTests(unittest.TestCase):

    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = SimpleNamespace(
            pk=uuid4(),
            is_authenticated=True,
        )
        self.engagement_id = uuid4()
        self.url = "/api/ai/workforce/engagements/"
        self.url += str(self.engagement_id)
        self.url += "/case-setup/prepare/"
        self.payload = {
            "batch_key": "case_setup_01",
            "proposed_payload": {
                "dry_run": True,
                "folder_domain_decision": {
                    "action": "reuse",
                    "human_approved": False,
                },
            },
        }

    def post(self, data=None, authenticated=True):
        request = self.factory.post(
            self.url,
            self.payload if data is None else data,
            format="json",
        )
        if authenticated:
            force_authenticate(request, user=self.user)
        return SicoCaseSetupPrepareView.as_view()(
            request,
            engagement_id=self.engagement_id,
        )

    @patch(
        "ai_onboarding.sico_case_setup_views.prepare_ai_case_setup"
    )
    def test_authenticated_dry_run_uses_adapter(self, adapter):
        adapter.return_value = {
            "mode": "dry_run",
            "replay": False,
        }

        response = self.post()

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.data["execution_performed"])
        self.assertFalse(response.data["writes_to_grc_records"])
        self.assertTrue(response.data["requires_human_review"])
        adapter.assert_called_once()

    @patch(
        "ai_onboarding.sico_case_setup_views.prepare_ai_case_setup"
    )
    def test_anonymous_user_cannot_prepare(self, adapter):
        response = self.post(authenticated=False)

        self.assertIn(response.status_code, (401, 403))
        adapter.assert_not_called()

    @patch(
        "ai_onboarding.sico_case_setup_views.prepare_ai_case_setup"
    )
    def test_commit_flag_not_accepted(self, adapter):
        data = {
            **self.payload,
            "explicitly_approved": True,
        }
        response = self.post(data)

        self.assertEqual(response.status_code, 400)
        adapter.assert_not_called()

    @patch(
        "ai_onboarding.sico_case_setup_views.prepare_ai_case_setup"
    )
    def test_unknown_engagement_is_not_disclosed(self, adapter):
        adapter.side_effect = Http404(
            "Engagement not accessible."
        )

        response = self.post()

        self.assertEqual(response.status_code, 404)

    @patch(
        "ai_onboarding.sico_case_setup_views.prepare_ai_case_setup"
    )
    def test_adapter_denial_returns_bad_request(self, adapter):
        from ai_onboarding.sico_case_setup_adapter import (
            SicoCaseSetupPreparationError,
        )

        adapter.side_effect = SicoCaseSetupPreparationError(
            "AI-generated proposals cannot contain approval."
        )

        response = self.post()

        self.assertEqual(response.status_code, 400)


if __name__ == "__main__":
    unittest.main(verbosity=2)