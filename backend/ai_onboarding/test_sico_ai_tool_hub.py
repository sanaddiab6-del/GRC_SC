"""Source-only safety checks for the generic multi-stage SICO tool hub.

Django tests are intentionally mocked: they do not require live GRC DB data.
End-to-end module permission, tenancy, and transaction tests are still required
before any write flag is enabled.
"""
from __future__ import annotations

from contextlib import nullcontext
from types import SimpleNamespace
from unittest.mock import Mock, patch
from uuid import uuid4

from django.test import SimpleTestCase, override_settings
from rest_framework.test import APIRequestFactory, force_authenticate

from .engagement_rules import STAGES
from .sico_ai_tool_hub_views import (
    SicoAiToolCatalogView, SicoAiToolCommitView, SicoAiToolPrepareView,
    _approved_operation_payload, _enabled_for_commit,
)


class SicoAiToolHubTests(SimpleTestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = SimpleNamespace(pk=uuid4(), is_authenticated=True)
        self.engagement = str(uuid4())
        self.folder = str(uuid4())

    def _post(self, view, path, data):
        request = self.factory.post(path, data, format='json')
        force_authenticate(request, user=self.user)
        return view.as_view()(request)

    @override_settings(SICO_ENGAGEMENT_COMMITS_ENABLED=False,
                       SICO_AI_EXECUTION_STAGE_ALLOWLIST=tuple(s.slug for s in STAGES))
    def test_all_stages_are_off_by_default(self):
        self.assertEqual(len(STAGES), 11)
        self.assertFalse(any(_enabled_for_commit(s.slug) for s in STAGES))

    @override_settings(SICO_ENGAGEMENT_COMMITS_ENABLED=True,
                       SICO_AI_EXECUTION_STAGE_ALLOWLIST=['assets', 'case_setup'])
    def test_explicit_per_stage_allowlist_and_case_setup_exclusion(self):
        self.assertTrue(_enabled_for_commit('assets'))
        self.assertFalse(_enabled_for_commit('case_setup'))
        self.assertFalse(_enabled_for_commit('risk_scenarios'))

    @override_settings(SICO_ENGAGEMENT_COMMITS_ENABLED=True,
                       SICO_AI_EXECUTION_STAGE_ALLOWLIST='assets')
    def test_unstructured_allowlist_never_enables_a_tool(self):
        self.assertFalse(_enabled_for_commit('assets'))

    def test_catalog_returns_all_reviewed_stages(self):
        reply = self._post(SicoAiToolCatalogView, '/catalog/', {})
        self.assertEqual(reply.status_code, 200)
        self.assertEqual(reply.data['reviewed_count'], len(STAGES))
        self.assertFalse(any(t['can_commit'] for t in reply.data['tools']))

    def test_prepare_rejects_unknown_service_without_dispatch(self):
        with patch('ai_onboarding.sico_ai_tool_hub_views.execute_stage') as execute:
            reply = self._post(SicoAiToolPrepareView, '/prepare/', {
                'engagement_id': self.engagement, 'stage': '__import__',
                'batch_key': 'x', 'operation_payload': {'dry_run': True},
            })
        self.assertEqual(reply.status_code, 400)
        execute.assert_not_called()

    def test_prepare_rejects_commit_mode_payload(self):
        with patch('ai_onboarding.sico_ai_tool_hub_views.execute_stage') as execute:
            reply = self._post(SicoAiToolPrepareView, '/prepare/', {
                'engagement_id': self.engagement, 'stage': 'assets',
                'batch_key': 'x', 'operation_payload': {'dry_run': False},
            })
        self.assertEqual(reply.status_code, 400)
        execute.assert_not_called()

    def test_prepare_dispatches_only_reviewed_stage(self):
        digest = 'a' * 64
        expected = {'result': {'_sico_review': {'prepared_digest': digest},
                               'commit_status': 'validated'}}
        with patch('ai_onboarding.sico_ai_tool_hub_views.execute_stage', return_value=expected) as execute:
            reply = self._post(SicoAiToolPrepareView, '/prepare/', {
                'engagement_id': self.engagement, 'stage': 'assets',
                'batch_key': 'one', 'operation_payload': {'dry_run': True},
            })
        self.assertEqual(reply.status_code, 200)
        self.assertFalse(reply.data['grc_records_changed'])
        self.assertEqual(execute.call_args.kwargs['mode'], 'dry_run')
        self.assertFalse(execute.call_args.kwargs['explicitly_approved'])

    def test_commit_is_off_and_does_not_even_read_receipt(self):
        with patch('ai_onboarding.sico_ai_tool_hub_views.get_prepared_receipt') as get_receipt:
            reply = self._post(SicoAiToolCommitView, '/commit/', {
                'engagement_id': self.engagement, 'stage': 'risk_scenarios',
                'batch_key': 'one', 'prepared_digest': 'b' * 64,
                'confirm_commit': True,
            })
        self.assertEqual(reply.status_code, 403)
        get_receipt.assert_not_called()

    def test_payload_approval_does_not_change_record_ids_or_actions(self):
        data = {
            'dry_run': True,
            'folder_reference': self.folder,
            'risk_reference': str(uuid4()),
            'decisions': [{'action': 'reuse', 'human_approved': False}],
        }
        from .engagement_rules import reviewed_payload_digest
        digest = reviewed_payload_digest(data)
        modified = _approved_operation_payload(data)
        self.assertFalse(modified['dry_run'])
        self.assertTrue(modified['decisions'][0]['human_approved'])
        self.assertEqual(modified['risk_reference'], data['risk_reference'])
        self.assertEqual(modified['folder_reference'], data['folder_reference'])
        self.assertEqual(reviewed_payload_digest(modified), digest)
        self.assertTrue(data['dry_run'])

    @override_settings(SICO_ENGAGEMENT_COMMITS_ENABLED=True,
                       SICO_AI_EXECUTION_STAGE_ALLOWLIST=['assets'])
    def test_unapproved_receipt_cannot_commit(self):
        receipt = Mock()
        receipt.approved_by_id = ''
        receipt.prepared_digest = 'c' * 64
        with patch('ai_onboarding.sico_ai_tool_hub_views.get_prepared_receipt', return_value=receipt), \
             patch('ai_onboarding.sico_ai_tool_hub_views.verified_review_snapshot', return_value={}), \
             patch('ai_onboarding.sico_ai_tool_hub_views.execute_stage') as execute, \
             patch('ai_onboarding.sico_ai_tool_hub_views.transaction.atomic', return_value=nullcontext()):
            reply = self._post(SicoAiToolCommitView, '/commit/', {
                'engagement_id': self.engagement, 'stage': 'assets',
                'batch_key': 'one', 'prepared_digest': 'c' * 64,
                'confirm_commit': True,
            })
        self.assertEqual(reply.status_code, 403)
        execute.assert_not_called()
