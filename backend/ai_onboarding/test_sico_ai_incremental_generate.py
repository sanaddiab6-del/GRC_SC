"""Tests for the model-driven incremental generation endpoint, no DB access."""
from types import SimpleNamespace
from unittest.mock import Mock, patch
from django.test import SimpleTestCase
from rest_framework.test import APIRequestFactory, force_authenticate
from . import sico_ai_sixteen_generate_views as v

ROW = {
    'analysis': 'Review the Saudi fintech payment application authentication path and identify potential access-control gaps for evidence-based examination.',
    'proposed_work': 'Prepare a scoped assessment of privileged access and application transaction authorization with responsible staff interviews.',
    'evidence_needed': 'Request architecture diagrams, access review logs, configured policies and signed assessment scope.',
}

class IncrementalGenerationTests(SimpleTestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = Mock(is_authenticated=True, is_active=True, pk='test-user')
        self.provider = Mock()
        self.provider.generate_structured.return_value = ROW.copy()
        self.selection = SimpleNamespace(provider=self.provider, config=SimpleNamespace(
            model='qwen2.5:3b', timeout_seconds=300, max_output_tokens=2400))

    def request(self, number=1, org='New Synthetic Fintech'):
        req = self.factory.post('/api/ai/workforce/assistant/lifecycle/generate-one/', {
            'organization_name': org,
            'framework_name': 'NCA ECC',
            'problem': 'Assess the potential security risks of a synthetic fintech payment platform.',
            'activity_number': number,
        }, format='json')
        force_authenticate(req, self.user)
        return req

    def test_all_sixteen_exact_activity_numbers(self):
        rows = [v.generate_one(organization='New Org', framework='NCA ECC',
            problem='Synthetic payment assessment', activity_number=n,
            selection=self.selection) for n in range(1, 17)]
        self.assertEqual([item['number'] for item in rows], list(range(1,17)))
        self.assertEqual(len({row['code'] for row in rows}), 16)
        self.assertTrue(all(row['state'] == 'ai_draft_not_executed' for row in rows))

    def test_new_organization_can_generate_without_being_provisioned(self):
        with patch.object(v, 'resolve_advisory_capability_config'), \
             patch.object(v, 'get_advisory_provider_selection', return_value=self.selection):
            response = v.SicoSixteenGenerateItemView.as_view()(self.request())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['activity']['number'], 1)
        self.assertFalse(response.data['business_records_written'])
        self.assertEqual(response.data['compliance_verdict'], 'not_established')

    def test_strict_small_schema_and_bounded_generation(self):
        v.generate_one(organization='X', framework='NCA ECC', problem='Synthetic payment',
                       activity_number=1, selection=self.selection)
        args = self.provider.generate_structured.call_args.kwargs
        self.assertEqual(args['json_schema'], v.ONE_ITEM_SCHEMA)
        self.assertLessEqual(args['max_output_tokens'], 850)
        self.assertLessEqual(args['timeout_seconds'], 150)
        self.assertEqual(args['user_payload']['activity_number'], 1)

    def test_invalid_primary_recovers_only_missing_field_from_real_model(self):
        incomplete = dict(ROW)
        incomplete['evidence_needed'] = ''
        self.provider.generate_structured.side_effect = [incomplete, {'text': ROW['evidence_needed']}]
        with patch.object(v, 'resolve_advisory_capability_config'), \
             patch.object(v, 'get_advisory_provider_selection', return_value=self.selection):
            response = v.SicoSixteenGenerateItemView.as_view()(self.request(number=3))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['activity']['evidence_needed'], ROW['evidence_needed'])
        self.assertEqual(self.provider.generate_structured.call_count, 2)
        self.assertEqual(self.provider.generate_structured.call_args.kwargs['json_schema'], v.ONE_FIELD_SCHEMA)

    def test_bad_primary_recovers_three_fields_from_model_not_templates(self):
        self.provider.generate_structured.side_effect = [
            {'analysis': 'short'},
            {'text': ROW['analysis']}, {'text': ROW['proposed_work']},
            {'text': ROW['evidence_needed']},
        ]
        with patch.object(v, 'resolve_advisory_capability_config'), \
             patch.object(v, 'get_advisory_provider_selection', return_value=self.selection):
            response = v.SicoSixteenGenerateItemView.as_view()(self.request(number=3))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.provider.generate_structured.call_count, 4)
        self.assertEqual(response.data['activity']['analysis'], ROW['analysis'])

    def test_failed_recovery_is_not_claimed_as_generated(self):
        self.provider.generate_structured.return_value = {'analysis': 'too short'}
        with patch.object(v, 'resolve_advisory_capability_config'), \
             patch.object(v, 'get_advisory_provider_selection', return_value=self.selection):
            response = v.SicoSixteenGenerateItemView.as_view()(self.request(number=3))
        self.assertEqual(response.status_code, 503)
        self.assertNotIn('activity', response.data)
        self.assertEqual(self.provider.generate_structured.call_count, 2)

    def test_timeout_triggers_bounded_small_response_recovery(self):
        self.provider.generate_structured.side_effect = [
            TimeoutError('provider timed out'),
            {'text': ROW['analysis']}, {'text': ROW['proposed_work']},
            {'text': ROW['evidence_needed']},
        ]
        with patch.object(v, 'resolve_advisory_capability_config'), \
             patch.object(v, 'get_advisory_provider_selection', return_value=self.selection):
            response = v.SicoSixteenGenerateItemView.as_view()(self.request(number=3))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.provider.generate_structured.call_count, 4)

    def test_all_fields_still_need_real_generation(self):
        self.provider.generate_structured.side_effect = [
            ValueError('malformed primary response'),
            {'text': ROW['analysis']},
            TimeoutError('fallback failed'),
        ]
        with patch.object(v, 'resolve_advisory_capability_config'), \
             patch.object(v, 'get_advisory_provider_selection', return_value=self.selection):
            response = v.SicoSixteenGenerateItemView.as_view()(self.request(number=3))
        self.assertEqual(response.status_code, 503)
        self.assertNotIn('activity', response.data)
        self.assertEqual(self.provider.generate_structured.call_count, 3)

    def test_stage_specific_instructions_for_compliance_setup(self):
        v.generate_one(organization='New Org', framework='NCA ECC',
            problem='Synthetic payment assessment', activity_number=3,
            selection=self.selection)
        payload = self.provider.generate_structured.call_args.kwargs['user_payload']
        self.assertIn('ComplianceAssessment', payload['specialized_focus_for_this_stage'])
        self.assertIn('no access', payload['data_limitations'].lower())

    def test_invalid_stage_rejected_before_model_call(self):
        response = v.SicoSixteenGenerateItemView.as_view()(self.request(number=17))
        self.assertEqual(response.status_code, 400)
        self.provider.generate_structured.assert_not_called()

    def test_inactive_account_denied(self):
        self.user.is_active = False
        response = v.SicoSixteenGenerateItemView.as_view()(self.request())
        self.assertEqual(response.status_code, 403)
        self.provider.generate_structured.assert_not_called()
