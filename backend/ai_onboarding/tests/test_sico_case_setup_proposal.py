import unittest
from types import SimpleNamespace
from unittest.mock import patch
from uuid import uuid4

from ai_onboarding.sico_case_setup_proposal import (
    SicoProposalError,
    build_case_setup_proposal,
    prepare_case_setup_from_engagement,
)
from ai_onboarding.case_setup_serializers import AiCaseSetupInputSerializer


class SicoCaseSetupProposalTests(unittest.TestCase):

    def setUp(self):
        self.folder = SimpleNamespace(
            pk=uuid4(),
            name="Example Test Organization",
        )
        self.framework = SimpleNamespace(
            pk=uuid4(),
            name="NCA ECC",
        )
        self.engagement = SimpleNamespace(
            pk=uuid4(),
            folder_id=self.folder.pk,
            framework_id=self.framework.pk,
            compliance_assessment_id=None,
            objective="Assess information security controls and risks",
        )

    def build(self):
        return build_case_setup_proposal(
            self.engagement,
            self.folder,
            self.framework,
        )

    def test_new_case_proposal_passes_real_serializer(self):
        proposal = self.build()
        payload = proposal["proposed_payload"]
        serializer = AiCaseSetupInputSerializer(data=payload)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(
            payload["perimeter_decision"]["action"], "create"
        )
        self.assertEqual(
            payload["compliance_assessment_decision"]["action"],
            "create",
        )

    def test_existing_assessment_is_reused(self):
        existing_id = uuid4()
        self.engagement.compliance_assessment_id = existing_id
        payload = self.build()["proposed_payload"]
        self.assertEqual(
            payload["compliance_assessment_decision"]["action"],
            "reuse",
        )
        self.assertEqual(
            payload["compliance_assessment_decision"][
                "selected_existing_id"
            ],
            str(existing_id),
        )
        self.assertEqual(
            payload["perimeter_decision"]["action"], "skip"
        )

    def test_no_ai_approval_and_stable_source_hash(self):
        first = self.build()["proposed_payload"]
        second = self.build()["proposed_payload"]
        self.assertTrue(first["dry_run"])
        self.assertFalse(first["approved_by_user"])
        self.assertFalse(
            first["framework_resolution"]["user_confirmed"]
        )
        for key in (
            "folder_domain_decision",
            "perimeter_decision",
            "compliance_assessment_decision",
            "risk_assessment_decision",
        ):
            self.assertFalse(first[key]["human_approved"])
        self.assertEqual(
            first["source_step1_draft_hash"],
            second["source_step1_draft_hash"],
        )

    def test_missing_framework_fails_closed(self):
        self.engagement.framework_id = None
        with self.assertRaises(SicoProposalError):
            self.build()

    def test_wrong_folder_fails_closed(self):
        self.engagement.folder_id = uuid4()
        with self.assertRaises(SicoProposalError):
            self.build()

    @patch(
        "ai_onboarding.sico_case_setup_proposal.prepare_ai_case_setup"
    )
    @patch(
        "ai_onboarding.sico_case_setup_proposal.RoleAssignment.is_object_readable",
        return_value=True,
    )
    @patch(
        "ai_onboarding.sico_case_setup_proposal.Framework.objects.filter"
    )
    @patch(
        "ai_onboarding.sico_case_setup_proposal.Folder.objects.filter"
    )
    @patch(
        "ai_onboarding.sico_case_setup_proposal.authorized_engagement"
    )
    def test_uses_existing_dry_run_adapter(
        self, authorized, folder_filter, framework_filter,
        readable, adapter,
    ):
        authorized.return_value = self.engagement
        folder_filter.return_value.first.return_value = self.folder
        framework_filter.return_value.first.return_value = self.framework
        adapter.return_value = {"mode": "dry_run"}

        request = SimpleNamespace(
            user=SimpleNamespace(
                pk=uuid4(), is_authenticated=True
            )
        )

        result = prepare_case_setup_from_engagement(
            request,
            self.engagement.pk,
            batch_key="auto_case_setup",
        )

        self.assertEqual(
            result["preparation"]["mode"], "dry_run"
        )
        self.assertFalse(result["execution_performed"])
        adapter.assert_called_once()
        self.assertIs(
            adapter.call_args.kwargs["proposed_payload"]["dry_run"],
            True,
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)