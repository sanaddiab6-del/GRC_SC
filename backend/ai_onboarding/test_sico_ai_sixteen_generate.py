"""Disconnected tests: no database access and no actual Qwen required."""
from types import SimpleNamespace
from unittest.mock import Mock, patch
from django.test import SimpleTestCase
from rest_framework.test import APIRequestFactory, force_authenticate
from . import sico_ai_sixteen_generate_views as v

SAMPLE = {'results': [
    {'analysis': 'Evaluate authentication mechanisms used for fintech payment operations and identify possible weak controls.',
     'proposed_work': 'Prepare a scoped review of payment system access management, authorization flow and segregation of duties.',
     'evidence_needed': 'Request current security architecture, policies and access review logs for verification.'}
    for _ in range(4)]}

class SixteenDraftTests(SimpleTestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = Mock(is_authenticated=True, is_active=True, pk='test-user')
        self.config = SimpleNamespace(model='qwen2.5:3b', timeout_seconds=300, max_output_tokens=2400)
        self.provider = Mock()
        self.provider.generate_structured.return_value = SAMPLE
        self.selection = SimpleNamespace(provider=self.provider, config=self.config)

    def call(self, phase=0, org='New Synthetic Fintech'):
        request = self.factory.post('/api/ai/workforce/assistant/lifecycle/generate-four/', {
            'organization_name': org, 'framework_name': 'NCA ECC',
            'problem': 'Assess the security risks and compliance obligations of a synthetic payment service.',
            'phase': phase}, format='json')
        force_authenticate(request, self.user)
        return v.SicoSixteenGenerateBatchView.as_view()(request)

    def test_sixteen_defined_stages_are_unique(self):
        self.assertEqual(len(v.STAGES), 16)
        self.assertEqual(len(set(code for code, _ in v.STAGES)), 16)

    def test_no_organization_lookup_or_db_write_required_for_new_company(self):
        with patch.object(v, 'resolve_advisory_capability_config'), \
             patch.object(v, 'get_advisory_provider_selection', return_value=self.selection):
            result = self.call(org='Completely New Synthetic Organization')
        self.assertEqual(result.status_code, 200)
        self.assertTrue(result.data['generated_by_model'])
        self.assertFalse(result.data['business_records_written'])
        self.assertEqual(result.data['activities'][0]['number'], 1)
        self.assertEqual(result.data['compliance_verdict'], 'not_established')
        self.provider.generate_structured.assert_called_once()

    def test_last_batch_has_exact_last_four(self):
        rows = v.generate_four(organization='NewOrg', framework='NCA ECC',
             problem='Synthetic payment assessment', phase=3, selection=self.selection)
        self.assertEqual([r['number'] for r in rows], [13,14,15,16])
        self.assertEqual(rows[-1]['code'], '16_reports')
        self.assertTrue(all(r['state'] == 'ai_draft_not_executed' for r in rows))

    def test_invalid_provider_output_is_rejected_not_fabricated(self):
        self.provider.generate_structured.return_value = {'results': []}
        with patch.object(v, 'resolve_advisory_capability_config'), \
             patch.object(v, 'get_advisory_provider_selection', return_value=self.selection):
            result = self.call()
        self.assertEqual(result.status_code, 503)
        self.assertNotIn('activities', result.data)

    def test_active_authenticated_user_required(self):
        self.user.is_active = False
        result = self.call()
        self.assertEqual(result.status_code, 403)

    def test_invalid_phase_rejected_without_model_call(self):
        result = self.call(phase=9)
        self.assertEqual(result.status_code, 400)
        self.provider.generate_structured.assert_not_called()
