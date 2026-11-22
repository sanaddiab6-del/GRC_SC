"""Disconnected no-database tests for the generated assessment endpoint."""
from types import SimpleNamespace
from unittest.mock import patch, Mock
import uuid
from django.http import Http404
from django.test import SimpleTestCase
from rest_framework.test import APIRequestFactory, force_authenticate

from . import sico_ai_generated_assessment_views as v

REPORT = {
    'assessment_summary': 'For the selected payment processing services, validate access governance, '
                          'transaction monitoring, and incident handling against the actual scoped controls.',
    'potential_risk_scenarios': [{
        'scenario': 'Unauthorized modifications to payment settlement configuration could disrupt integrity.',
        'possible_impact': 'Incorrect transaction settlement and operational disruption.',
        'verification_needed': 'Review payment service change approvals and privileged access logs.'}],
    'control_review': [{
        'control_area': 'Privileged access governance',
        'assessment_question': 'Which roles can change settlement rules and how are their changes reviewed?',
        'verification_needed': 'Role assignments, change records and privileged activity review evidence.'}],
    'evidence_requests': [{
        'request': 'Provide the latest approved production privileged-access review.',
        'purpose': 'Verify that permissions for settlement rule changes are appropriate and monitored.'}],
    'next_actions': ['Confirm the payment systems and services in the assessment scope.',
                     'Request relevant access governance evidence from responsible teams.'],
}
FOLDER_ID = uuid.uuid4()
FRAMEWORK_ID = uuid.uuid4()
ENGAGEMENT_ID = uuid.uuid4()


def context():
    return {'organization': {'name': 'Authorized Example Company', 'folder_id': str(FOLDER_ID)},
            'framework': {'id': str(FRAMEWORK_ID), 'name': 'Essential Cybersecurity Controls'},
            'inventory': {'assets': {'samples': [], 'scan_limited': False},
                          'evidence': {'samples': [], 'scan_limited': False}}}


class GeneratedAssessmentTests(SimpleTestCase):
    def setUp(self):
        self.user = Mock(is_authenticated=True)
        self.user.pk = 'user-1'
        self.engagement = Mock(pk=ENGAGEMENT_ID, folder_id=FOLDER_ID,
                               framework_id=FRAMEWORK_ID,
                               objective='Review cybersecurity risks affecting the payment service and assess controls.')
        self.factory = APIRequestFactory()

    def call(self):
        request = self.factory.post('/ai/workforce/assistant/lifecycle/generate/',
                                    {'engagement_id': str(ENGAGEMENT_ID)}, format='json')
        force_authenticate(request, user=self.user)
        return v.SicoAiGeneratedAssessmentView.as_view()(request)

    @patch.object(v, 'authorized_engagement', side_effect=Http404())
    def test_unauthorized_engagement_not_generated(self, _):
        response = self.call()
        self.assertEqual(response.status_code, 404)

    @patch.object(v, 'verify_principal')
    @patch.object(v, 'assemble_real_engagement_context')
    @patch.object(v, 'authorized_engagement')
    def test_wrong_framework_refused(self, auth, assemble, principal):
        auth.return_value = self.engagement
        bad = context(); bad['framework']['id'] = str(uuid.uuid4())
        assemble.return_value = bad
        response = self.call()
        self.assertEqual(response.status_code, 403)

    @patch.object(v, 'get_advisory_provider_selection')
    @patch.object(v, 'resolve_advisory_capability_config')
    @patch.object(v, 'verify_principal')
    @patch.object(v, 'assemble_real_engagement_context')
    @patch.object(v, 'authorized_engagement')
    def test_real_provider_output_validated_and_permissions_rechecked(self, auth, assemble, principal, config, get_provider):
        auth.return_value = self.engagement
        assemble.return_value = context()
        provider = Mock()
        provider.generate_structured.return_value = REPORT
        config.return_value = Mock()
        get_provider.return_value = SimpleNamespace(provider=provider, config=SimpleNamespace(
            model='local-qwen', timeout_seconds=90, max_output_tokens=2400))
        response = self.call()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data['generated_by_model'])
        self.assertFalse(response.data['business_records_written'])
        self.assertEqual(response.data['compliance_verdict'], 'not_established')
        self.assertEqual(auth.call_count, 2)
        self.assertEqual(principal.call_count, 2)
        provider.generate_structured.assert_called_once()
        opts = provider.generate_structured.call_args.kwargs
        self.assertEqual(opts['max_output_tokens'], 900)
        self.assertEqual(opts['timeout_seconds'], 90)
        self.engagement.save.assert_not_called()

    @patch.object(v, 'get_advisory_provider_selection')
    @patch.object(v, 'resolve_advisory_capability_config')
    @patch.object(v, 'verify_principal')
    @patch.object(v, 'assemble_real_engagement_context')
    @patch.object(v, 'authorized_engagement')
    def test_invalid_generated_text_is_not_presented_as_work(self, auth, assemble, principal, config, get_provider):
        auth.return_value = self.engagement
        assemble.return_value = context()
        provider = Mock(); provider.generate_structured.return_value = {'assessment_summary': 'too short'}
        get_provider.return_value = SimpleNamespace(provider=provider, config=SimpleNamespace(
            model='local-qwen', timeout_seconds=90, max_output_tokens=2400))
        response = self.call()
        self.assertEqual(response.status_code, 503)
        self.assertNotIn('report', response.data)
        self.engagement.save.assert_not_called()
