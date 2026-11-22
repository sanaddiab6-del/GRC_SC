"""No live database: safety and wiring tests for the one-instruction SICO lifecycle.

A separate disposable PostgreSQL integration suite is still required to certify
specific write-service payloads, transactions and object-level RBAC.
"""
from contextlib import nullcontext
from types import SimpleNamespace
from unittest.mock import Mock, patch
from uuid import uuid4

from django.test import SimpleTestCase, override_settings
from rest_framework import status
from rest_framework.response import Response
from rest_framework.test import APIRequestFactory, force_authenticate

from .sico_ai_lifecycle import ACTIVITIES, SERVICE_SEQUENCE, eligible_stage, lifecycle_snapshot
from .sico_ai_lifecycle_views import (
    LifecycleStartView, LifecycleDraftNextView, LifecycleStageCommitView,
    _approval_flags, _preview_flags, _unknown_uuids, _commit_enabled,
)


def receipt(stage, status='committed', approved_by_id=''):
    return SimpleNamespace(stage=stage, status=status, approved_by_id=approved_by_id)


class LifecyclePolicyTests(SimpleTestCase):
    def test_exactly_sixteen_professional_activities(self):
        self.assertEqual(len(ACTIVITIES), 16)
        self.assertEqual(ACTIVITIES[0].code, '01_framework')
        self.assertEqual(ACTIVITIES[-1].code, '16_reports')

    def test_eleventh_reviewed_writer_preserved(self):
        self.assertEqual(len(SERVICE_SEQUENCE), 11)
        self.assertEqual(len(set(SERVICE_SEQUENCE)), 11)

    def test_no_receipt_means_no_compliance_conclusion(self):
        obj = lifecycle_snapshot(folder_id=uuid4(), framework_id=uuid4(),
                                 assessment_id=None, receipts=[])
        self.assertFalse(obj['case_complete'])
        self.assertEqual(obj['compliance_verdict'], 'not_established')
        self.assertTrue(all(x['state'] != 'completed' for x in obj['lifecycle']))

    def test_committed_stage_is_not_a_professional_signoff(self):
        obj = lifecycle_snapshot(folder_id=uuid4(), framework_id=uuid4(),
                                 assessment_id=uuid4(), receipts=[receipt('case_setup')])
        self.assertEqual(obj['lifecycle'][2]['state'], 'operation_recorded_not_professional_signoff')
        self.assertFalse(obj['case_complete'])

    def test_approvals_are_a_stop_not_a_hidden_write(self):
        next_stage, reason = eligible_stage([receipt('case_setup'), receipt('assets', 'prepared')])
        self.assertIsNone(next_stage)
        self.assertIn('human review', reason)

    def test_without_case_setup_no_ai_writes(self):
        stage, reason = eligible_stage([])
        self.assertIsNone(stage)
        self.assertIn('initial assessment', reason)

    def test_first_next_writer_uses_existing_registry_order(self):
        stage, reason = eligible_stage([receipt('case_setup')])
        self.assertEqual(stage, 'assets')
        self.assertIsNone(reason)

    def test_human_review_flags_cannot_change_business_content(self):
        source = {'dry_run': True, 'approved': False, 'nested': {
            'human_approved': False, 'name': 'Risk Treatment A'}}
        outcome = _approval_flags(source)
        self.assertFalse(outcome['dry_run'])
        self.assertTrue(outcome['approved'])
        self.assertTrue(outcome['nested']['human_approved'])
        self.assertEqual(outcome['nested']['name'], 'Risk Treatment A')
        self.assertTrue(source['dry_run'])

    def test_model_cannot_supply_nested_approval(self):
        value = {'dry_run': False, 'approved_by_user': True, 'nested': {'human_approved': True}}
        prepared = _preview_flags(value)
        self.assertTrue(prepared['dry_run'])
        self.assertFalse(prepared['approved_by_user'])
        self.assertFalse(prepared['nested']['human_approved'])

    def test_model_invented_record_id_fails_closed(self):
        real = str(uuid4())
        fake = str(uuid4())
        self.assertEqual(_unknown_uuids({'asset_id': fake}, {real}), ['asset_id'])
        self.assertEqual(_unknown_uuids({'asset_id': real}, {real}), [])

    @override_settings(SICO_ENGAGEMENT_COMMITS_ENABLED=False,
                       SICO_ENGAGEMENT_COMMIT_STAGE_ALLOWLIST=('assets',))
    def test_commits_disabled_by_default_even_with_allowlist(self):
        self.assertFalse(_commit_enabled('assets'))

    @override_settings(SICO_ENGAGEMENT_COMMITS_ENABLED=True,
                       SICO_ENGAGEMENT_COMMIT_STAGE_ALLOWLIST=('assets',))
    def test_only_explicit_allowlisted_writer_can_commit(self):
        self.assertTrue(_commit_enabled('assets'))
        self.assertFalse(_commit_enabled('audit_report'))


class LifecycleEndpointTests(SimpleTestCase):
    def setUp(self):
        self.user = SimpleNamespace(pk=uuid4(), is_authenticated=True, is_active=True)
        self.factory = APIRequestFactory()
        self.engagement = SimpleNamespace(pk=uuid4(), folder_id=uuid4(), framework_id=uuid4(),
            compliance_assessment_id=None, executions=SimpleNamespace(all=lambda: []),
            plan={}, save=Mock(), title='Human-selected NCA ECC assessment')

    def test_unapproved_writer_returns_403_without_touching_database(self):
        with override_settings(SICO_ENGAGEMENT_COMMITS_ENABLED=False):
            data = dict(engagement_id=str(self.engagement.pk), stage='assets',
                        prepared_digest='a'*64, confirm_reviewed=True)
            request = self.factory.post('/test/', data, format='json')
            force_authenticate(request, user=self.user)
            with patch('ai_onboarding.sico_ai_lifecycle_views.execute_stage') as writer:
                result = LifecycleStageCommitView.as_view()(request)
            self.assertEqual(result.status_code, 403)
            writer.assert_not_called()

    @patch('ai_onboarding.sico_ai_lifecycle_views._summary')
    @patch('ai_onboarding.sico_ai_lifecycle_views._lifecycle_engagement')
    @patch('ai_onboarding.sico_ai_lifecycle_views.verify_principal')
    def test_draft_does_not_invoke_qwen_before_initial_approval(self, principal, auth, summary):
        auth.return_value = self.engagement
        summary.return_value = {'case_complete': False}
        request = self.factory.post('/test/', {'engagement_id': str(self.engagement.pk)}, format='json')
        force_authenticate(request, user=self.user)
        with patch('ai_onboarding.sico_ai_lifecycle_views._model_draft') as qwen:
            result = LifecycleDraftNextView.as_view()(request)
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.data['status'], 'blocked')
        qwen.assert_not_called()

    @patch('ai_onboarding.sico_ai_lifecycle_views._summary')
    @patch('ai_onboarding.sico_ai_lifecycle_views.authorized_engagement')
    @patch('ai_onboarding.sico_ai_lifecycle_views.transaction.atomic', return_value=nullcontext())
    @patch('ai_onboarding.sico_ai_lifecycle_views.prepare_workflow')
    def test_start_preserves_exact_user_selected_scope(self, prepare, atomic, auth, summary):
        auth.return_value = self.engagement
        prepare.return_value = Response({'engagement_id': str(self.engagement.pk)}, status=201)
        summary.return_value = {'case_complete': False}
        request = self.factory.post('/test/', {
            'instruction': 'Assess our actual NCA ECC scope, identify gaps and request evidence.',
            'folder_id': str(self.engagement.folder_id),
            'framework_id': str(self.engagement.framework_id),
            'assessment_name': 'GRC review', 'new_perimeter_name': 'Current scope',
        }, format='json')
        force_authenticate(request, user=self.user)
        result = LifecycleStartView.as_view()(request)
        self.assertEqual(result.status_code, 201)
        self.assertEqual(self.engagement.plan['user_selected_framework_id'], str(self.engagement.framework_id))
        self.assertEqual(self.engagement.plan['user_selected_organization_id'], str(self.engagement.folder_id))
        self.engagement.save.assert_called_once()
