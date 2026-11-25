"""Disconnected/no-DB tests for Activity 1 using real SICO framework interfaces."""
from types import SimpleNamespace
from unittest.mock import Mock, patch
from django.test import SimpleTestCase
from jsonschema import ValidationError as JsonSchemaError
from . import sico_ai_sixteen_generate_views as v

BASE = {
    'analysis': 'Proposed fintech platform scope needs confirmation of payment data flow and service ownership before applicability is concluded.',
    'proposed_work': 'Draft a regulatory applicability workbook tied to permitted SICO framework requirements and named business processes.',
    'evidence_needed': 'Obtain business licensing details, approved assessment scope, merchant processing diagrams and system inventory exports.',
}
SAMPLE = [
    {'reference': 'REAL-CTRL-1', 'name': 'Access management', 'description': 'Control access to critical systems', 'typical_evidence': 'Access review records'},
    {'reference': 'REAL-CTRL-2', 'name': 'Third-party security', 'description': 'Manage supplier risk', 'typical_evidence': 'Supplier review records'},
]
REVIEW = {
    'regulatory_applicability_question': 'Which services are regulated payment services and which legal entity operates the proposed platform?',
    'reviews': [
        {'applicability': 'needs_confirmation',
         'rationale': 'If merchant-facing APIs exist, identity controls are likely pertinent to administrative access and payment integrity, subject to scope confirmation.',
         'evidence_to_request': 'Obtain the privileged identity inventory and signed payment architecture from the technical owner.'},
        {'applicability': 'potentially_applicable',
         'rationale': 'If external processors or cloud vendors are involved, supplier oversight may be relevant to payment operations but must be verified.',
         'evidence_to_request': 'Request the approved supplier inventory and current third-party security assessments.'},
    ],
}


class FrameworkLibraryStageTests(SimpleTestCase):
    def setUp(self):
        self.provider = Mock()
        self.selection = SimpleNamespace(provider=self.provider,
            config=SimpleNamespace(model='qwen-local', timeout_seconds=250,
                                   max_output_tokens=1800))
        self.user = Mock(is_active=True, is_authenticated=True)
        self.catalog = {
            'status': 'matched',
            'matched_framework': {'name': 'Official-looking library name',
                                  'reference': 'nca-ecc-library',
                                  'urn': 'urn:sample', 'provider': 'NCA'},
            'candidate_names': [], 'accessible_requirement_count': 32,
            'sample': SAMPLE, 'regulator_edition_status': 'not_independently_verified',
            'source': 'sico_authorized_framework_library_read_only',
        }

    def test_real_sico_references_are_server_owned_not_generated_by_qwen(self):
        def model(**kwargs):
            return REVIEW if kwargs['schema_name'] == 'sico_library_anchored_framework_review_v1' else BASE
        self.provider.generate_structured.side_effect = model
        with patch.object(v, '_read_authorized_framework_catalog', return_value=self.catalog) as reader:
            result = v.generate_one(organization='Sky Line', framework='NCA ECC',
                problem='Assess the cybersecurity of a proposed payment service.',
                activity_number=1, selection=self.selection, user=self.user, case_context='[]')
        reader.assert_called_once()
        review = result['framework_review']
        self.assertEqual([r['reference'] for r in review['requirement_reviews']],
                         ['REAL-CTRL-1', 'REAL-CTRL-2'])
        self.assertEqual(review['accessible_requirement_count'], 32)
        self.assertEqual(review['regulator_edition_status'], 'not_independently_verified')
        self.assertEqual(review['coverage'], 'sample_only_not_full_framework_assessment')
        self.assertEqual(review['requirement_reviews'][0]['rationale'], REVIEW['reviews'][0]['rationale'])
        payload = self.provider.generate_structured.call_args.kwargs['user_payload']
        self.assertEqual(payload['actual_authorized_requirements_in_exact_order'][0]['reference_from_SICO'],
                         'REAL-CTRL-1')
        self.assertEqual(self.provider.generate_structured.call_count, 2)

    def test_ambiguous_framework_is_not_silently_selected(self):
        self.provider.generate_structured.return_value = BASE
        ambiguous = {**self.catalog, 'status': 'ambiguous',
            'matched_framework': None, 'candidate_names': ['ECC 2018', 'ECC 2024'],
            'accessible_requirement_count': 0, 'sample': []}
        with patch.object(v, '_read_authorized_framework_catalog', return_value=ambiguous):
            item = v.generate_one(organization='Sky Line', framework='NCA ECC',
                problem='Assess a proposed fintech platform and its payment services.',
                activity_number=1, selection=self.selection, user=self.user, case_context='[]')
        self.assertEqual(item['framework_review']['status'], 'ambiguous')
        self.assertEqual(item['framework_review']['requirement_reviews'], [])
        self.assertEqual(self.provider.generate_structured.call_count, 1)

    def test_invalid_review_never_claimed_as_success(self):
        self.provider.generate_structured.side_effect = [BASE, {'reviews': []}]
        with patch.object(v, '_read_authorized_framework_catalog', return_value=self.catalog):
            with self.assertRaises(JsonSchemaError):
                v.generate_one(organization='Sky Line', framework='NCA ECC',
                    problem='Assess a proposed fintech platform and its payment services.',
                    activity_number=1, selection=self.selection, user=self.user, case_context='[]')

    def test_legacy_stage_one_does_not_add_db_reads(self):
        self.provider.generate_structured.return_value = BASE
        with patch.object(v, '_read_authorized_framework_catalog') as reader:
            item = v.generate_one(organization='Sky Line', framework='NCA ECC',
                problem='Assess a proposed fintech platform and its payment services.',
                activity_number=1, selection=self.selection)
        self.assertNotIn('framework_review', item)
        reader.assert_not_called()

    def test_framework_lookup_preserves_sico_permissions_and_not_alias_guess(self):
        framework = SimpleNamespace(name='Loaded sample framework', ref_id='NCA-ECC',
                                    urn='urn:nca:test', provider='NCA')
        framework_qs = Mock()
        framework_qs.count.return_value = 2
        framework_qs.order_by.return_value.values.return_value = []
        # No read access to RequirementNodes => no sampled requirement text.
        with patch('ai_onboarding.sico_ai_lifecycle_views._framework_candidates',
                   return_value=[framework]) as candidate_lookup, \
             patch('core.models.RequirementNode') as node_model, \
             patch('iam.models.RoleAssignment.get_accessible_object_ids',
                   return_value=([], [], [])) as permissions, \
             patch('iam.models.Folder.get_root_folder', return_value='root'):
            node_model.objects.filter.return_value = framework_qs
            result = v._read_authorized_framework_catalog(
                self.user, 'NCA ECC', 'Assess the payment service.')
        candidate_lookup.assert_called_once_with(self.user, 'NCA ECC')
        filter_kw = node_model.objects.filter.call_args.kwargs
        self.assertEqual(filter_kw['id__in'], [])
        self.assertEqual(result['sample'], [])
        self.assertEqual(result['status'], 'no_accessible_assessable_requirements')
        self.assertTrue(permissions.called)

    def test_two_authorized_framework_versions_remain_ambiguous(self):
        a = SimpleNamespace(name='ECC A')
        b = SimpleNamespace(name='ECC B')
        with patch('ai_onboarding.sico_ai_lifecycle_views._framework_candidates',
                   return_value=[a, b]), patch('core.models.RequirementNode') as nodes:
            result = v._read_authorized_framework_catalog(
                self.user, 'NCA ECC', 'Assess a proposed payment platform.')
        self.assertEqual(result['status'], 'ambiguous')
        self.assertEqual(result['candidate_names'], ['ECC A', 'ECC B'])
        nodes.objects.filter.assert_not_called()

    def test_connected_http_endpoint_reads_authorized_framework_for_request_user(self):
        from rest_framework.test import APIRequestFactory, force_authenticate
        factory = APIRequestFactory()
        request = factory.post('/api/ai/workforce/assistant/lifecycle/generate-one/', {
            'organization_name': 'Sky Line', 'framework_name': 'NCA ECC',
            'problem': 'Assess a proposed payment platform for cybersecurity and compliance.',
            'activity_number': 1, 'case_context': '[]',
        }, format='json')
        force_authenticate(request, self.user)
        self.provider.generate_structured.side_effect = lambda **kwargs: (
            REVIEW if kwargs['schema_name'] == 'sico_library_anchored_framework_review_v1' else BASE)
        with patch.object(v, 'resolve_advisory_capability_config'), \
             patch.object(v, 'get_advisory_provider_selection', return_value=self.selection), \
             patch.object(v, '_read_authorized_framework_catalog', return_value=self.catalog) as reader:
            response = v.SicoSixteenGenerateItemView.as_view()(request)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.data['business_records_written'])
        self.assertEqual(response.data['activity']['framework_review']['status'], 'matched')
        self.assertIs(reader.call_args.args[0], self.user)
