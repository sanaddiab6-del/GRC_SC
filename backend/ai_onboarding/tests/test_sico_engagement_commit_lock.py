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


if __name__ == "__main__":
    unittest.main(verbosity=2)