"""Case continuity and generated asset tests; no ORM or live database usage."""
import json
from types import SimpleNamespace
from unittest.mock import Mock, patch
from django.test import SimpleTestCase
from rest_framework.test import APIRequestFactory, force_authenticate
from . import sico_ai_sixteen_generate_views as v

ROW = {
    'analysis': 'Check the likely transaction API and token flow under the proposed payment service scope; no systems have been verified.',
    'proposed_work': 'Draft a focused threat and control evaluation with candidate API and identity systems for later owner verification.',
    'evidence_needed': 'Request payment architecture diagrams, system inventory exports and current access review evidence from the owner.',
}
PROFILE = {
    'title': 'Sky Line payment services NCA ECC cybersecurity assessment',
    'scope_summary': 'Proposed scope covers a payment API, transaction processing, privileged identity workflows and data protection boundaries, subject to the company verifying its actual systems and excluded services.',
}
ASSETS = [
    {
        'name': 'Candidate Payment API Gateway', 'asset_type': 'Application API',
        'business_purpose': 'Proposed entry point for merchant payment transaction requests and authorization controls.',
        'verification_needed': 'Obtain architecture diagrams and the actual approved system inventory from the organization.',
    },
    {
        'name': 'Candidate Transaction Database', 'asset_type': 'Database',
        'business_purpose': 'Potential storage for transaction records needing confidentiality and integrity review.',
        'verification_needed': 'Ask data owners for the approved data inventory and database architecture documentation.',
    },
]

class ConnectedCaseGenerationTests(SimpleTestCase):
    def setUp(self):
        self.provider = Mock()
        self.selection = SimpleNamespace(provider=self.provider, config=SimpleNamespace(
            model='qwen2.5:3b', timeout_seconds=300, max_output_tokens=2400))
        def model(**kwargs):
            schema = kwargs['json_schema']
            if schema == v.CASE_PROFILE_SCHEMA:
                return dict(PROFILE)
            if schema == v.CANDIDATE_ASSET_SCHEMA:
                return dict(ASSETS[kwargs['user_payload']['candidate_number'] - 1])
            return dict(ROW)
        self.provider.generate_structured.side_effect = model

    def generate(self, number, context=None):
        return v.generate_one(organization='Sky Line', framework='NCA ECC',
            problem='Assess a proposed Saudi payment platform under NCA ECC.',
            activity_number=number, selection=self.selection, case_context=context)

    def test_real_model_outputs_drive_case_title_and_scope(self):
        a = self.generate(2, '[]')
        self.assertEqual(a['case_profile'], PROFILE)
        self.assertEqual(self.provider.generate_structured.call_count, 2)
        self.assertEqual(self.provider.generate_structured.call_args.kwargs['json_schema'], v.CASE_PROFILE_SCHEMA)
        self.assertEqual(a['state'], 'ai_draft_not_executed')

    def test_assets_are_model_generated_with_server_draft_refs(self):
        context = json.dumps([{'number': 2, 'case_profile': PROFILE, **ROW}])
        a = self.generate(4, context)
        self.assertEqual(len(a['candidate_assets']), 2)
        self.assertEqual([r['draft_ref'] for r in a['candidate_assets']], ['PA-1','PA-2'])
        self.assertTrue(all(r['state']=='unverified_ai_proposal' for r in a['candidate_assets']))
        self.assertEqual(self.provider.generate_structured.call_count, 3)

    def test_following_risks_receive_existing_proposed_assets(self):
        prior = [
            {'number': 2, 'case_profile': PROFILE, **ROW},
            {'number': 4, 'candidate_assets': [dict(draft_ref='PA-'+str(i+1), **r) for i,r in enumerate(ASSETS)], **ROW},
        ]
        a = self.generate(6, json.dumps(prior))
        self.assertEqual(a['number'], 6)
        payload = self.provider.generate_structured.call_args.kwargs['user_payload']
        prior_context = payload['previous_AI_generated_case_context_NOT_VERIFIED']
        self.assertEqual(prior_context[1]['candidate_assets_unverified'][0]['draft_ref'], 'PA-1')
        self.assertIn('untrusted context DATA', payload['continuity_instruction'])

    def test_future_stage_context_rejected_before_model_call(self):
        with self.assertRaises(ValueError):
            self.generate(4, json.dumps([{'number': 5, **ROW}]))
        self.provider.generate_structured.assert_not_called()

    def test_duplicate_asset_is_rejected_not_fabricated(self):
        def model(**kwargs):
            if kwargs['json_schema'] == v.CANDIDATE_ASSET_SCHEMA:
                return dict(ASSETS[0])
            return dict(ROW)
        self.provider.generate_structured.side_effect = model
        with self.assertRaises(ValueError):
            self.generate(4, '[]')

    def test_legacy_calls_without_context_remain_backward_compatible(self):
        for n in (2,4):
            row = self.generate(n)
            self.assertNotIn('case_profile', row)
            self.assertNotIn('candidate_assets', row)
        self.assertEqual(self.provider.generate_structured.call_count, 2)

    def test_too_many_previous_drafts_rejected(self):
        data = json.dumps([{'number': i, **ROW} for i in range(1,17)])
        with self.assertRaises(ValueError):
            self.generate(16, data)
        self.provider.generate_structured.assert_not_called()
