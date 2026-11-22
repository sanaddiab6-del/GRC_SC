"""Offline Activity 5 contract/diagnostic tests. No DB, Docker or model calls."""
import copy
import json
import unittest
from types import SimpleNamespace
from unittest.mock import patch

# Reuse only the isolated settings and mocked HTTP helper, not its test cases.
from ai_onboarding.tests import test_quality_evidence_requests as evidence_tests
from ai_onboarding.tests.test_quality_evidence_requests import previous_drafts
from ai_onboarding import quality_sico_drafts_v5 as quality
from ai_onboarding import sico_ai_case_quality_views as views
from ai_onboarding.llm_errors import AiProviderExecutionError
from rest_framework.test import APIRequestFactory, force_authenticate


def threat_output():
    return {
        'title': 'Threat hypothesis: Conditional credential phishing against the proposed directory',
        'content': (
            'A potential external actor could attempt phishing against accounts in the proposed '
            'identity directory. If access protections were insufficient, compromised credentials '
            'might expose business records. This is an unverified hypothesis; confirm protections '
            'and scope with the owner before assessing any weakness or incident.'
        ),
        'attributes': {
            'asset_reference': 'draft-04-01',
            'threat_source': 'Potential external phishing actor; identity and capability unverified.',
            'weakness_hypothesis': 'If account safeguards were insufficient, credentials could be misused; evidence required.',
            'impact_if_realized': 'Conditional unauthorized access to proposed directory records; impact requires owner review.',
        },
        'evidence_request': 'Request owner-reviewed access configuration and relevant monitoring records to evaluate the hypothesis.',
        'verification_question': 'Which safeguards and source records support or disprove the proposed credential misuse hypothesis?',
        'related_draft_references': ['draft-04-01'],
    }


class ThreatDraftTests(unittest.TestCase):
    transport = evidence_tests.EvidenceRequestTests.transport

    def setUp(self):
        evidence_tests.EvidenceRequestTests.setUp(self)
        self.one_asset_checkpoint = {'schema': self.checkpoint['schema'],
                                     'items': [copy.deepcopy(self.checkpoint['items'][0])]}
        self.context = previous_drafts(self.one_asset_checkpoint)

    def generate(self, output=None, **changes):
        args = dict(organization='Offline example', framework='NCA ECC',
                    objective='Propose conditional threats for the candidate identity directory.',
                    phase=4, draft_index=1, prior_drafts=[], case_context=self.context)
        args.update(changes)
        with self.transport(threat_output() if output is None else output):
            return quality.generate_quality_draft(self.selection, **args)

    def post(self, output, checkpoint=None):
        source = self.one_asset_checkpoint if checkpoint is None else checkpoint
        before = copy.deepcopy(source)
        meta = {'status': 'matched', 'framework_id': '00000000-0000-0000-0000-000000000001'}
        rows = [{'reference': 'OFFLINE-REQ', 'requirement_id': 'offline-source-only'}]
        request = APIRequestFactory().post('/api/ai/workforce/assistant/case-draft/quality-one/', {
            'organization_name': 'Offline example', 'framework_name': 'NCA ECC',
            'problem': 'Propose conditional threats for the candidate identity directory.',
            'activity_number': 5,
            'draft_index': 1 + sum(row['activity_number'] == 5 for row in source['items']),
            'source_digest': 'a' * 64,
            'previous_drafts': previous_drafts(source),
        }, format='json')
        force_authenticate(request, user=SimpleNamespace(pk='offline-user', is_active=True, is_authenticated=True))
        with patch.object(views, '_load_authorized_requirements', return_value=(meta, rows)), \
             patch.object(views, '_page_and_digest', return_value=(rows, 114, 'a' * 64)), \
             patch.object(views, 'resolve_advisory_capability_config'), \
             patch.object(views, 'get_advisory_provider_selection', return_value=self.selection), \
             self.transport(output):
            response = views.SicoQualityDraftOneView.as_view()(request)
        self.assertEqual(source, before)
        return response

    def test_existing_single_record_contract_accepts_a_valid_threat(self):
        result = self.generate()
        self.assertEqual(result['activity_code'], 'threats')
        self.assertEqual(result['draft']['record_type'], 'Threat / Vulnerability')
        self.assertEqual(result['draft']['draft_reference'], 'draft-05-01')
        self.assertEqual(result['draft']['status'], 'new_unsaved_ai_draft_pending_verification')
        self.assertFalse(result['draft']['is_verified_existing_asset_or_evidence'])
        self.assertFalse(result['business_records_written'])
        self.assertEqual(len(self.calls), 1)
        schema = self.calls[0]['format']
        self.assertEqual(schema['type'], 'object')
        self.assertNotIn('results', schema['properties'])
        self.assertEqual(schema['properties']['attributes']['type'], 'object')
        self.assertEqual(set(schema['properties']['attributes']['required']), set(quality.CONTRACTS['threats'][1]))

    def test_flat_schema_failures_report_sanitized_path_and_rule(self):
        cases = [
            (lambda d: d.update(attributes=[]), ['attributes'], 'type'),
            (lambda d: d.pop('evidence_request'), [], 'required'),
            (lambda d: d.update(content='Too short'), ['content'], 'minLength'),
            (lambda d: d.update(title='Vulnerability: Unverified example'), ['title'], 'pattern'),
            (lambda d: d['attributes'].update(threat_source={'secret': 'do-not-disclose'}),
             ['attributes', 'threat_source'], 'type'),
            (lambda d: d['attributes'].update(asset_reference='unknown-ref'),
             ['attributes', 'asset_reference'], 'enum'),
        ]
        for change, suffix, rule in cases:
            with self.subTest(rule=rule, path=suffix):
                output = threat_output()
                change(output)
                response = self.post(output)
                self.assertEqual(response.status_code, 503)
                self.assertEqual(response.data['failure_reason'], 'local_ai_provider_schema_mismatch')
                self.assertEqual(response.data.get('validation_failure'), {
                    'path': suffix, 'rule': rule,
                })
                self.assertIn(f'({rule})', response.data['detail'])
                self.assertNotIn('do-not-disclose', json.dumps(response.data))
                self.assertNotIn('draft', response.data)

    def test_two_drafts_are_rejected_without_retry(self):
        output = {'results': [{'drafts': [threat_output(), threat_output()]}]}
        response = self.post(output)
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.data['failure_reason'], 'local_ai_provider_schema_mismatch')
        self.assertEqual(len(self.calls), 1)

    def test_asset_attribute_must_match_the_accepted_candidate_relationship(self):
        for reference in ('draft-04-02', '00000000-0000-0000-0000-000000000001', 'An invented production server'):
            with self.subTest(reference=reference):
                output = threat_output()
                output['attributes']['asset_reference'] = reference
                with self.assertRaises((ValueError, AiProviderExecutionError)):
                    self.generate(output)

    def test_asset_must_be_present_before_a_provider_call(self):
        with self.assertRaisesRegex(ValueError, 'threat_requires_candidate_asset'):
            self.generate(case_context=[])
        self.assertEqual(self.calls, [])

    def test_blank_duplicate_and_missing_attributes_are_rejected(self):
        for change in (
            lambda d: d['attributes'].pop('impact_if_realized'),
            lambda d: d['attributes'].update(unexpected_field='untrusted'),
            lambda d: d['attributes'].update(asset_reference=''),
        ):
            output = threat_output()
            change(output)
            with self.assertRaises((AiProviderExecutionError, ValueError)):
                self.generate(output)

    def test_one_and_five_draft_checkpoints_remain_usable_on_success_and_failure(self):
        for checkpoint in (self.one_asset_checkpoint, self.checkpoint):
            with self.subTest(accepted=len(checkpoint['items'])):
                success = self.post(threat_output(), checkpoint)
                self.assertEqual(success.status_code, 200)
                self.assertEqual(success.data['authorized_requirement_count'], 114)
                self.assertEqual(success.data['provenance'], 'qwen_quality_single_authenticated_v7')
                invalid = threat_output()
                invalid.pop('verification_question')
                self.assertEqual(self.post(invalid, checkpoint).status_code, 503)

    def test_invalid_json_is_rejected_without_exposing_or_resetting_checkpoint(self):
        response = self.post('{"results": [')
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.data['failure_reason'], 'local_ai_provider_invalid_output')
        self.assertFalse(response.data['business_records_written'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
