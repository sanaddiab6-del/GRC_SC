import unittest
from types import SimpleNamespace
from unittest.mock import patch
from uuid import uuid4

from ai_onboarding.sico_case_setup_adapter import (
    SicoCaseSetupPreparationError,
    prepare_ai_case_setup,
)


class SicoCaseSetupAdapterTests(unittest.TestCase):

    def setUp(self):
        self.request = SimpleNamespace(
            user=SimpleNamespace(
                pk=uuid4(),
                is_authenticated=True,
            )
        )
        self.engagement_id = uuid4()
        self.payload = {
            "dry_run": True,
            "folder_domain_decision": {
                "action": "reuse",
                "human_approved": False,
            },
        }

    def prepare(self, payload=None, batch_key="case_setup_01"):
        return prepare_ai_case_setup(
            self.request,
            self.engagement_id,
            batch_key=batch_key,
            proposed_payload=self.payload if payload is None else payload,
        )

    @patch(
        "ai_onboarding.sico_case_setup_adapter.execute_stage"
    )
    def test_calls_existing_coordinator_in_dry_run_only(self, execute):
        execute.return_value = {
            "mode": "dry_run",
            "replay": False,
        }

        original = dict(self.payload)
        result = self.prepare()

        self.assertEqual(result["mode"], "dry_run")
        self.assertEqual(self.payload, original)
        execute.assert_called_once()

        kwargs = execute.call_args.kwargs
        self.assertEqual(kwargs["stage"], "case_setup")
        self.assertEqual(kwargs["mode"], "dry_run")
        self.assertIs(kwargs["explicitly_approved"], False)

    @patch(
        "ai_onboarding.sico_case_setup_adapter.execute_stage"
    )
    def test_rejects_commit_payload(self, execute):
        with self.assertRaises(SicoCaseSetupPreparationError):
            self.prepare({"dry_run": False})
        execute.assert_not_called()

    @patch(
        "ai_onboarding.sico_case_setup_adapter.execute_stage"
    )
    def test_rejects_nested_ai_approval(self, execute):
        payload = {
            "dry_run": True,
            "folder_domain_decision": {
                "action": "reuse",
                "human_approved": True,
            },
        }
        with self.assertRaises(SicoCaseSetupPreparationError):
            self.prepare(payload)
        execute.assert_not_called()

    @patch(
        "ai_onboarding.sico_case_setup_adapter.execute_stage"
    )
    def test_rejects_unauthenticated_user(self, execute):
        self.request.user.is_authenticated = False
        with self.assertRaises(SicoCaseSetupPreparationError):
            self.prepare()
        execute.assert_not_called()

    @patch(
        "ai_onboarding.sico_case_setup_adapter.execute_stage"
    )
    def test_rejects_invalid_batch_key(self, execute):
        with self.assertRaises(SicoCaseSetupPreparationError):
            self.prepare(batch_key="../unsafe")
        execute.assert_not_called()

    @patch(
        "ai_onboarding.sico_case_setup_adapter.execute_stage"
    )
    def test_does_not_swallow_coordinator_denial(self, execute):
        execute.side_effect = PermissionError("Folder access denied")
        with self.assertRaises(PermissionError):
            self.prepare()


if __name__ == "__main__":
    unittest.main(verbosity=2)