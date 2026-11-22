"""Focused safety tests for SICO's existing-service write workflow.

These tests use no historical database or Docker volume. Full PostgreSQL
create/rollback and tenant tests are mandatory before enabling live commits.
"""
from __future__ import annotations

import copy
from types import SimpleNamespace
from unittest.mock import patch
from uuid import uuid4

from django.test import SimpleTestCase, override_settings
from rest_framework.test import APIRequestFactory, force_authenticate

from .engagement_rules import STAGES, reviewed_payload_digest
from .engagement_service import EngagementBlocked, execute_stage
from .sico_ai_workflow_views import (
    WorkflowCommitView, WorkflowPrepareView, case_payload, workflow_status,
)


class CasePayloadTests(SimpleTestCase):
    def setUp(self):
        self.folder_id = uuid4()
        self.framework_id = uuid4()
        self.perimeter_id = uuid4()
        self.risk_matrix_id = uuid4()
        self.framework = SimpleNamespace(pk=self.framework_id, name='NCA ECC')
        self.values = {
            'instruction': 'Prepare a real NCA ECC cybersecurity GRC case for this company.',
            'folder_id': self.folder_id, 'framework_id': self.framework_id,
            'perimeter_id': self.perimeter_id, 'assessment_name': 'NCA ECC - Q4 review',
        }

    def test_existing_records_are_explicitly_reused(self):
        result = case_payload(self.values, self.framework)
        self.assertEqual(result['folder_domain_decision']['selected_existing_id'], str(self.folder_id))
        self.assertEqual(result['perimeter_decision']['selected_existing_id'], str(self.perimeter_id))
        self.assertEqual(result['framework_resolution']['selected_framework_id'], str(self.framework_id))
        self.assertEqual(result['compliance_assessment_decision']['action'], 'create')
        self.assertEqual(result['risk_assessment_decision']['action'], 'skip')
        self.assertTrue(result['dry_run'])
        self.assertFalse(result['approved_by_user'])
        self.assertTrue(result['source_step1_draft_hash'].startswith('sha256:'))
        self.assertNotIn('result', result['compliance_assessment_decision']['proposed_fields'])

    def test_risk_matrix_adds_optional_risk_assessment(self):
        values = dict(self.values, risk_matrix_id=self.risk_matrix_id)
        result = case_payload(values, self.framework)
        self.assertEqual(result['risk_assessment_decision']['action'], 'create')
        self.assertEqual(result['risk_assessment_decision']['proposed_fields']['selected_risk_matrix_id'],
                         str(self.risk_matrix_id))

    def test_new_perimeter_is_explicit_and_requires_review(self):
        values = dict(self.values)
        values.pop('perimeter_id')
        values['new_perimeter_name'] = 'Cybersecurity scope for selected company'
        result = case_payload(values, self.framework)
        self.assertEqual(result['perimeter_decision']['action'], 'create')
        self.assertEqual(result['perimeter_decision']['proposed_fields']['name'], values['new_perimeter_name'])
        self.assertFalse(result['perimeter_decision']['human_approved'])

    def test_same_intended_operation_binds_review_and_commit_flags(self):
        result = case_payload(self.values, self.framework)
        original = reviewed_payload_digest(result)
        committed = copy.deepcopy(result)
        committed['dry_run'] = False
        committed['approved_by_user'] = True
        for key in ('folder_domain_decision', 'perimeter_decision',
                    'compliance_assessment_decision', 'risk_assessment_decision'):
            committed[key]['human_approved'] = True
        self.assertEqual(original, reviewed_payload_digest(committed))
        committed['framework_resolution']['selected_framework_id'] = str(uuid4())
        self.assertNotEqual(original, reviewed_payload_digest(committed))

    def test_instruction_bound_to_source_trace(self):
        result = case_payload(self.values, self.framework)
        other = case_payload(dict(self.values, instruction=self.values['instruction'] + ' changed'), self.framework)
        self.assertNotEqual(result['source_step1_draft_hash'], other['source_step1_draft_hash'])


class WriteGatesTests(SimpleTestCase):
    @override_settings(SICO_CASE_SETUP_COMMITS_ENABLED=False,
                       SICO_ENGAGEMENT_COMMITS_ENABLED=True,
                       SICO_ENGAGEMENT_COMMIT_STAGE_ALLOWLIST=['assets'])
    def test_case_requires_trusted_flow_and_its_own_flag(self):
        for trusted in (False, True):
            with self.assertRaises(EngagementBlocked) as raised:
                execute_stage(SimpleNamespace(user=None), uuid4(), stage='case_setup',
                              batch_key='initial', mode='commit', payload={'dry_run': False},
                              explicitly_approved=True, trusted_case_setup_workflow=trusted)
            self.assertEqual(raised.exception.http_status, 403)

    @override_settings(SICO_CASE_SETUP_COMMITS_ENABLED=True,
                       SICO_ENGAGEMENT_COMMITS_ENABLED=False,
                       SICO_ENGAGEMENT_COMMIT_STAGE_ALLOWLIST=[])
    def test_case_flag_cannot_enable_other_writers(self):
        for stage in ('assets', 'risk_scenarios', 'audit_report'):
            with self.assertRaises(EngagementBlocked):
                execute_stage(SimpleNamespace(user=None), uuid4(), stage=stage,
                              batch_key='initial', mode='commit', payload={'dry_run': False},
                              explicitly_approved=True, trusted_case_setup_workflow=True)

    @override_settings(SICO_CASE_SETUP_COMMITS_ENABLED=False)
    def test_commit_view_defaults_closed(self):
        fake_user = SimpleNamespace(is_authenticated=True, pk=uuid4())
        request = APIRequestFactory().post('/ai/workforce/assistant/workflow/commit/', {
            'engagement_id': str(uuid4()), 'prepared_digest': 'a' * 64, 'confirm_reviewed': True,
        }, format='json')
        force_authenticate(request, user=fake_user)
        response = WorkflowCommitView.as_view()(request)
        self.assertEqual(response.status_code, 403)
        self.assertIn('disabled', response.data['detail'])

    def test_invalid_preparation_never_reaches_database(self):
        fake_user = SimpleNamespace(is_authenticated=True, pk=uuid4())
        request = APIRequestFactory().post('/ai/workforce/assistant/workflow/prepare/', {
            'instruction': 'Make a real compliance and risk case for this company.',
            'folder_id': str(uuid4()), 'framework_id': str(uuid4()),
            'perimeter_id': str(uuid4()), 'new_perimeter_name': 'Ambiguous new perimeter',
            'assessment_name': 'NCA ECC - Q4 Review'
        }, format='json')
        force_authenticate(request, user=fake_user)
        with patch('ai_onboarding.sico_ai_workflow_views.allowed_folder') as folder:
            response = WorkflowPrepareView.as_view()(request)
        self.assertEqual(response.status_code, 400)
        folder.assert_not_called()


class WorklistTests(SimpleTestCase):

    def test_workflow_api_paths_exist(self):
        from django.urls import reverse
        for name, suffix in (
            ('sico-ai-workflow-options', '/workforce/assistant/workflow/options/'),
            ('sico-ai-workflow-prepare', '/workforce/assistant/workflow/prepare/'),
            ('sico-ai-workflow-review', '/workforce/assistant/workflow/review/'),
            ('sico-ai-workflow-approve', '/workforce/assistant/workflow/approve/'),
            ('sico-ai-workflow-commit', '/workforce/assistant/workflow/commit/'),
            ('sico-ai-workflow-resume', '/workforce/assistant/workflow/resume/'),
        ):
            self.assertTrue(reverse(name).endswith(suffix))
    def test_not_prepared_is_not_completed(self):
        engagement = SimpleNamespace(pk=uuid4(), folder_id=uuid4(),
                                    framework_id=None, compliance_assessment_id=None,
                                    risk_assessment_id=None)
        engagement.executions = SimpleNamespace(all=lambda: [
            SimpleNamespace(stage='case_setup', status='prepared', approved_by_id='')])
        with patch('ai_onboarding.sico_ai_workflow_views.authorized_engagement', return_value=engagement):
            status = workflow_status(SimpleNamespace(pk=uuid4()), engagement)
        self.assertEqual(len(status['workflow']), len(STAGES))
        self.assertEqual(status['workflow'][0]['status'], 'prepared_needs_approval')
        self.assertTrue(all(item['status'] == 'not_prepared' for item in status['workflow'][1:]))

    def test_approval_is_not_business_completion(self):
        engagement = SimpleNamespace(pk=uuid4(), folder_id=uuid4(),
                                    framework_id=None, compliance_assessment_id=None,
                                    risk_assessment_id=None)
        engagement.executions = SimpleNamespace(all=lambda: [
            SimpleNamespace(stage='case_setup', status='prepared', approved_by_id='reviewer')])
        with patch('ai_onboarding.sico_ai_workflow_views.authorized_engagement', return_value=engagement):
            status = workflow_status(SimpleNamespace(pk=uuid4()), engagement)
        self.assertEqual(status['workflow'][0]['status'], 'approved_not_committed')
        self.assertNotEqual(status['workflow'][0]['status'], 'committed')
