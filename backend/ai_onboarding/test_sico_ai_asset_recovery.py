"""No-DB tests of real model-only asset recovery and no-fabrication guards."""
from types import SimpleNamespace
from unittest.mock import Mock
from django.test import SimpleTestCase
from . import sico_ai_sixteen_generate_views as v


class CandidateAssetRecoveryTests(SimpleTestCase):
    def setUp(self):
        self.provider = Mock()
        self.selection = SimpleNamespace(provider=self.provider, config=SimpleNamespace(
            model='qwen-local', timeout_seconds=300, max_output_tokens=2400))
        self.payload = {
            'organization_name_user_supplied': 'Sky Line',
            'assessment_objective': 'Propose a Saudi fintech assessment.',
        }
        self.api = {
            'name': 'Proposed Merchant Payment API', 'asset_type': 'Application API',
            'business_purpose': 'May route merchant authorization requests and enforce transaction session limits.',
            'verification_needed': 'Confirm using approved application inventory and merchant API architecture diagrams.',
        }
        self.iam = {
            'name': 'Proposed Privileged Identity Service', 'asset_type': 'Identity Platform',
            'business_purpose': 'May enforce privileged access and authentication for payment system administrators.',
            'verification_needed': 'Ask asset owner for identity tenant diagram and current privileged user inventory.',
        }

    def test_two_distinct_model_generated_assets_keep_stable_references(self):
        self.provider.generate_structured.side_effect = [self.api, self.iam]
        assets = v._generate_candidate_assets(self.selection, self.payload)
        self.assertEqual([asset['draft_ref'] for asset in assets], ['PA-1', 'PA-2'])
        self.assertEqual(assets[0]['name'], self.api['name'])
        self.assertEqual(assets[1]['name'], self.iam['name'])
        self.assertTrue(all(a['state'] == 'unverified_ai_proposal' for a in assets))
        self.assertEqual(self.provider.generate_structured.call_count, 2)

    def test_duplicate_first_response_is_retried_with_exclusion(self):
        self.provider.generate_structured.side_effect = [self.api, self.api, self.iam]
        assets = v._generate_candidate_assets(self.selection, self.payload)
        self.assertEqual(assets[1]['name'], self.iam['name'])
        third = self.provider.generate_structured.call_args_list[2].kwargs['user_payload']
        self.assertEqual(third['attempt_number'], 2)
        self.assertEqual(third['already_proposed_names'], [self.api['name']])
        self.assertIn('distinct', third['correction_if_second_attempt'])

    def test_temporary_invalid_schema_is_retried_without_synthetic_data(self):
        invalid = {'name': 'Bad item'}
        self.provider.generate_structured.side_effect = [invalid, self.api, self.iam]
        assets = v._generate_candidate_assets(self.selection, self.payload)
        self.assertEqual([a['name'] for a in assets], [self.api['name'], self.iam['name']])

    def test_persistent_invalid_asset_fails_with_precise_safe_status(self):
        self.provider.generate_structured.side_effect = [self.api, self.api, self.api]
        with self.assertRaises(v.ProposedAssetGenerationError) as error:
            v._generate_candidate_assets(self.selection, self.payload)
        self.assertEqual(error.exception.asset_number, 2)
        self.assertEqual(self.provider.generate_structured.call_count, 3)

    def test_all_asset_field_content_must_be_model_generated_and_valid(self):
        invalid = dict(self.api, verification_needed='       ')
        self.provider.generate_structured.side_effect = [invalid, invalid]
        with self.assertRaises(v.ProposedAssetGenerationError) as error:
            v._generate_candidate_assets(self.selection, self.payload)
        self.assertEqual(error.exception.asset_number, 1)
        self.assertEqual(self.provider.generate_structured.call_count, 2)

    def test_stage_4_remains_read_only(self):
        self.provider.generate_structured.side_effect = [
            {'analysis': 'Testable candidate assets include a merchant API and a privileged identity system.',
             'proposed_work': 'Proposed PA-1 merchant API and PA-2 identity asset register for scope verification.',
             'evidence_needed': 'Obtain approved asset inventory exports and service architecture diagrams.'},
            self.api, self.iam,
        ]
        activity = v.generate_one(organization='Sky Line', framework='NCA ECC',
            problem='Assess cybersecurity compliance of a Saudi online payment system.',
            activity_number=4, selection=self.selection, case_context='[]')
        self.assertEqual(activity['state'], 'ai_draft_not_executed')
        self.assertEqual(len(activity['candidate_assets']), 2)
        self.assertNotIn('business_records_written', activity)

class ActivityFieldRecoveryTests(SimpleTestCase):
    def setUp(self):
        self.provider = Mock()
        self.selection = SimpleNamespace(provider=self.provider, config=SimpleNamespace(
            model='qwen-local', timeout_seconds=300, max_output_tokens=2400))
        self.exact_fields = {
            'analysis': 'Proposed fintech risk scenario includes merchant API authorization and payment processing integrity.',
            'proposed_work': 'Draft risk scenario PA-1 API misuse and conditional controls requiring owner confirmation.',
            'evidence_needed': 'Request current merchant API gateway configuration and identity access reports.',
        }

    def test_malformed_primary_and_one_bad_recovery_can_still_use_real_qwen_fields(self):
        self.provider.generate_structured.side_effect = [
            {}, {'text': ''}, {'text': self.exact_fields['analysis']},
            {'text': self.exact_fields['proposed_work']},
            {'text': self.exact_fields['evidence_needed']},
        ]
        item = v.generate_one(organization='Sky Line', framework='NCA ECC',
            problem='Assess cybersecurity compliance of a Saudi online payment system.',
            activity_number=3, selection=self.selection, case_context='[]')
        for field, value in self.exact_fields.items():
            self.assertEqual(item[field], value)
        self.assertEqual(self.provider.generate_structured.call_count, 5)

    def test_exhausted_recovery_names_failed_field_instead_of_generic_error(self):
        self.provider.generate_structured.side_effect = [{}, {}, {}]
        with self.assertRaises(v.ProposedActivityFieldError) as caught:
            v.generate_one(organization='Sky Line', framework='NCA ECC',
                problem='Assess cybersecurity compliance of a Saudi online payment system.',
                activity_number=4, selection=self.selection, case_context='[]')
        self.assertEqual(caught.exception.field, 'analysis')
        self.assertEqual(self.provider.generate_structured.call_count, 3)


class LegacyIncrementalCompatibilityTests(SimpleTestCase):
    """Original callers do not pass case_context and have a one-try budget."""
    def setUp(self):
        self.provider = Mock()
        self.selection = SimpleNamespace(provider=self.provider, config=SimpleNamespace(
            model='qwen-local', timeout_seconds=300, max_output_tokens=2400))

    def test_invalid_primary_and_invalid_first_recovery_use_only_two_calls(self):
        self.provider.generate_structured.return_value = {'analysis': 'too short'}
        with self.assertRaises(v.ProposedActivityFieldError):
            v.generate_one(organization='Sky Line', framework='NCA ECC',
                problem='Assess a synthetic Saudi payment platform.',
                activity_number=3, selection=self.selection)
        self.assertEqual(self.provider.generate_structured.call_count, 2)

    def test_error_in_second_recovery_field_does_not_consume_extra_retry(self):
        self.provider.generate_structured.side_effect = [
            ValueError('malformed primary response'),
            {'text': 'Assess whether the proposed merchant payment API requires authentication and request signing.'},
            TimeoutError('legacy second-field recovery failed'),
        ]
        with self.assertRaises(v.ProposedActivityFieldError) as failure:
            v.generate_one(organization='Sky Line', framework='NCA ECC',
                problem='Assess a synthetic Saudi payment platform.',
                activity_number=3, selection=self.selection)
        self.assertEqual(failure.exception.field, 'proposed_work')
        self.assertEqual(self.provider.generate_structured.call_count, 3)
