"""Offline Activity 9 contract tests: no project settings, database or Qwen calls.

Run this module with unittest and backend on PYTHONPATH. Framework reads are
stubbed; the REAL LocalAiProvider validates mocked Ollama HTTP responses.
"""
from __future__ import annotations

import copy
import json
import os
import socket
import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from django.conf import settings

if not settings.configured and not os.environ.get('DJANGO_SETTINGS_MODULE'):
    settings.configure(
        SECRET_KEY='offline-contract-test-only', INSTALLED_APPS=[],
        DATABASES={'default': {'ENGINE': 'django.db.backends.dummy'}},
        REST_FRAMEWORK={'DEFAULT_AUTHENTICATION_CLASSES': [], 'UNAUTHENTICATED_USER': None},
        USE_TZ=True,
    )
    import django
    django.setup()

from jsonschema import Draft202012Validator
from rest_framework.test import APIRequestFactory, force_authenticate

from ai_onboarding import quality_sico_drafts_v5 as quality
from ai_onboarding import sico_ai_case_quality_views as views
from ai_onboarding.evidence_finding_suggestion_serializers import EvidenceRequestSerializer
from ai_onboarding.llm_errors import AiProviderExecutionError
from ai_onboarding.llm_provider import LocalAiProvider


def evidence_output():
    return {
        'title': 'Evidence request: Privileged account MFA configuration export',
        'content': (
            'Request a dated configuration export for the proposed identity service and '
            'privileged account scope. The control owner must confirm boundaries and '
            'collection dates before a reviewer checks completeness. No artifact has '
            'been supplied and no compliance result is established.'
        ),
        'attributes': {
            'linked_control_reference': 'draft-07-01',
            'artifact_to_collect': 'Read-only identity configuration export listing privileged roles and MFA settings.',
            'request_purpose': 'Support human evaluation of the proposed privileged access safeguard; no verdict.',
            'request_scope': 'Proposed identity service and administrator accounts; confirm boundaries with the owner.',
            'request_owner_role': 'Proposed identity control owner; accountable person to confirm.',
            'collection_period': 'Proposed preceding 90 days and current configuration; exact dates to confirm.',
            'acceptance_criteria': 'Reviewer checks source, dates, scope coverage and completeness; missing items remain unverified.',
        },
        'evidence_request': 'Request a dated privileged-role and MFA export from the proposed identity control owner; confirm scope and collection period.',
        'verification_question': 'Does the supplied export cover the agreed account scope and owner-confirmed collection period?',
        'related_draft_references': ['draft-04-01', 'draft-07-01'],
    }


def accepted_checkpoint():
    names = (
        (4, 'Asset:', 'Proposed identity directory'),
        (5, 'Threat hypothesis:', 'Conditional credential compromise'),
        (6, 'Risk scenario:', 'Potential privileged access misuse'),
        (7, 'Applied control:', 'Proposed privileged MFA safeguard'),
        (8, 'Policy:', 'Proposed access governance policy'),
    )
    return {'schema': 'sico-authenticated-quality-drafts-v7', 'items': [{
        'activity_number': number,
        'draft': {
            'draft_reference': f'draft-{number:02d}-01',
            'record_type': quality.DRAFT_ACTIVITIES[number-1][2],
            'title': prefix + ' ' + title,
            'content': 'Previously accepted hypothetical proposal retained in the browser checkpoint.',
            'proposed_attributes': [{'field': 'existing_field', 'proposed_value': 'Retained unchanged'}],
            'status': 'new_unsaved_ai_draft_pending_verification',
        },
    } for number, prefix, title in names]}


def previous_drafts(checkpoint):
    return [{key: row['draft'][key] for key in ('draft_reference', 'record_type', 'title', 'content')}
            for row in checkpoint['items']]


class EvidenceRequestTests(unittest.TestCase):
    def setUp(self):
        self.network_guard = patch.object(socket.socket, 'connect', side_effect=AssertionError('Network forbidden'))
        self.network_guard.start()
        self.addCleanup(self.network_guard.stop)
        self.provider = LocalAiProvider(base_url='http://127.0.0.1:9', base_url_safe=True, base_url_warning=None)
        self.selection = SimpleNamespace(provider=self.provider, config=SimpleNamespace(
            model='offline-qwen-fixture', timeout_seconds=60, max_output_tokens=1200,
        ))
        self.checkpoint = accepted_checkpoint()
        self.context = previous_drafts(self.checkpoint)
        self.calls = []

    def transport(self, output):
        def respond(request, **kwargs):
            self.calls.append(json.loads(request.data))
            response = MagicMock()
            response.__enter__.return_value.read.return_value = json.dumps(
                {'response': output if isinstance(output, str) else json.dumps(output)},
            ).encode()
            return response
        return patch('ai_onboarding.llm_provider.urllib.request.urlopen', side_effect=respond)

    def generate(self, output=None, **changes):
        args = dict(organization='Offline example', framework='NCA ECC',
                    objective='Request evidence for the proposed privileged access control.',
                    phase=8, draft_index=1, prior_drafts=[], case_context=self.context)
        args.update(changes)
        with self.transport(evidence_output() if output is None else output):
            return quality.generate_quality_draft(self.selection, **args)

    def post(self, output):
        meta = {'status': 'matched', 'framework_id': '00000000-0000-0000-0000-000000000001'}
        rows = [{'reference': 'OFFLINE-REQ', 'requirement_id': 'offline-source-only'}]
        request = APIRequestFactory().post('/api/ai/workforce/assistant/case-draft/quality-one/', {
            'organization_name': 'Offline example', 'framework_name': 'NCA ECC',
            'problem': 'Request evidence for the proposed privileged access control.',
            'activity_number': 9, 'draft_index': 1, 'source_digest': 'a' * 64,
            'previous_drafts': self.context,
        }, format='json')
        force_authenticate(request, user=SimpleNamespace(pk='offline-user', is_active=True, is_authenticated=True))
        with patch.object(views, '_load_authorized_requirements', return_value=(meta, rows)), \
             patch.object(views, '_page_and_digest', return_value=(rows, 114, 'a' * 64)), \
             patch.object(views, 'resolve_advisory_capability_config'), \
             patch.object(views, 'get_advisory_provider_selection', return_value=self.selection), \
             self.transport(output):
            return views.SicoQualityDraftOneView.as_view()(request)

    def test_valid_request_uses_real_provider_validation_and_stable_checkpoint_envelope(self):
        result = self.generate()
        draft = result['draft']
        self.assertEqual(draft['draft_reference'], 'draft-09-01')
        self.assertEqual(draft['record_type'], 'Evidence')
        self.assertEqual(draft['status'], 'new_unsaved_ai_draft_pending_verification')
        self.assertFalse(draft['is_verified_existing_asset_or_evidence'])
        self.assertFalse(result['business_records_written'])
        self.assertEqual({a['field']: a['proposed_value'] for a in draft['proposed_attributes']},
                         evidence_output()['attributes'])
        self.assertEqual(len(self.calls), 1)

    def test_prompt_and_ollama_schema_agree_on_one_named_field_record(self):
        self.generate()
        body = self.calls[0]
        self.assertEqual(body['format']['type'], 'object')
        self.assertNotIn('results', body['format']['properties'])
        self.assertIn('ONE', body['prompt'].upper())
        self.assertIn('named', body['prompt'])
        attrs = body['format']['properties']['attributes']
        self.assertEqual(attrs['type'], 'object')
        self.assertEqual(set(attrs['required']), set(quality.CONTRACTS['evidence_requests'][1]))
        self.assertEqual(attrs['properties']['linked_control_reference']['enum'], ['draft-07-01'])
        self.assertEqual(body['options']['num_predict'], 1100)

    def test_all_required_request_details_are_strictly_required(self):
        for field in quality.CONTRACTS['evidence_requests'][1]:
            with self.subTest(field=field):
                output = evidence_output()
                del output['attributes'][field]
                with self.assertRaises(AiProviderExecutionError) as error:
                    self.generate(output)
                self.assertEqual(error.exception.error_code, 'local_ai_provider_schema_mismatch')

    def test_invalid_attribute_values_are_not_coerced_or_filled(self):
        for invalid in (None, '', ' ', 3, {'artifact': 'export'}, 'x' * 181):
            with self.subTest(value=invalid):
                output = evidence_output()
                output['attributes']['artifact_to_collect'] = invalid
                with self.assertRaises(AiProviderExecutionError):
                    self.generate(output)

    def test_extra_fields_and_false_verification_are_rejected(self):
        for location, key in (('attributes', 'verified'), ('draft', 'compliance_result'), ('draft', 'is_verified')):
            with self.subTest(key=key):
                output = evidence_output()
                target = output
                if location == 'attributes':
                    target = target['attributes']
                target[key] = True
                with self.assertRaises(AiProviderExecutionError):
                    self.generate(output)

    def test_two_requests_are_rejected(self):
        output = {'results': [{'drafts': [evidence_output(), evidence_output()]}]}
        with self.assertRaises(AiProviderExecutionError):
            self.generate(output)

    def test_native_evidence_batch_is_not_mistaken_for_quality_output(self):
        with self.assertRaises(AiProviderExecutionError) as error:
            self.generate({'evidence_requests': []})
        self.assertEqual(error.exception.error_code, 'local_ai_provider_schema_mismatch')

    def test_invalid_truncated_and_nonobject_json_are_rejected(self):
        before = copy.deepcopy(self.checkpoint)
        for raw in ('not JSON', '{"results": [', '[]', 'null', '', '{"results": []} trailing'):
            with self.subTest(raw=raw):
                with self.assertRaises(AiProviderExecutionError) as error:
                    self.generate(raw)
                self.assertEqual(error.exception.error_code, 'local_ai_provider_invalid_output')
                self.assertEqual(self.checkpoint, before)

    def test_array_of_four_attributes_is_not_silently_expanded(self):
        output = evidence_output()
        output['attributes'] = [
            {'field': key, 'proposed_value': value}
            for key, value in list(output['attributes'].items())[:4]
        ]
        with self.assertRaises(AiProviderExecutionError):
            self.generate(output)

    def test_unknown_control_reference_is_rejected_at_provider_boundary(self):
        output = evidence_output()
        output['attributes']['linked_control_reference'] = 'draft-07-02'
        with self.assertRaises(AiProviderExecutionError):
            self.generate(output)

    def test_control_must_be_in_relationships(self):
        output = evidence_output()
        output['related_draft_references'] = ['draft-04-01']
        with self.assertRaisesRegex(ValueError, 'evidence_request_control_link_mismatch'):
            self.generate(output)

    def test_invented_duplicate_and_unrelated_relationships_are_rejected(self):
        for refs in (['draft-07-01', 'draft-04-02'], ['draft-07-01', 'draft-07-01'], ['draft-08-01']):
            with self.subTest(refs=refs):
                output = evidence_output()
                output['related_draft_references'] = refs
                with self.assertRaises((ValueError, AiProviderExecutionError)):
                    self.generate(output)

    def test_no_control_draft_is_explicitly_unlinked(self):
        output = evidence_output()
        output['attributes']['linked_control_reference'] = 'UNLINKED - control draft needed'
        output['related_draft_references'] = []
        self.assertFalse(self.generate(output, case_context=[])['business_records_written'])

    def test_prompt_placeholder_values_are_not_accepted_as_generated_content(self):
        output = evidence_output()
        output['attributes']['request_purpose'] = '<replace this placeholder>'
        with self.assertRaisesRegex(ValueError, 'evidence_request_placeholder_value'):
            self.generate(output)

    def test_success_and_failure_do_not_mutate_accepted_drafts_or_provider_response(self):
        before = copy.deepcopy(self.checkpoint)
        output = evidence_output()
        output_before = copy.deepcopy(output)
        self.generate(output)
        self.assertEqual(output, output_before)
        del output['attributes']['collection_period']
        with self.assertRaises(AiProviderExecutionError):
            self.generate(output)
        self.assertEqual(self.checkpoint, before)
        self.assertEqual(self.context, previous_drafts(before))

    def test_existing_four_attribute_evidence_checkpoint_can_resume(self):
        old = {'draft_reference': 'draft-09-01', 'record_type': 'Evidence',
               'title': 'Evidence request: Backup restoration exercise record',
               'content': 'Previously accepted backup collection request kept unchanged.',
               'proposed_attributes': [{'field': key, 'proposed_value': 'Legacy value'} for key in
                                       ('linked_control_reference', 'artifact_to_collect', 'request_owner_role', 'acceptance_criteria')]}
        before = copy.deepcopy(old)
        result = self.generate(draft_index=2, prior_drafts=[old])
        self.assertEqual(result['draft']['draft_reference'], 'draft-09-02')
        self.assertEqual(old, before)

    def test_accepted_evidence_draft_cannot_be_regenerated_as_a_new_record(self):
        existing = {'draft_reference': 'draft-09-01',
                    'title': evidence_output()['title'],
                    'content': 'Existing accepted draft remains in its original checkpoint slot.'}
        before = copy.deepcopy(existing)
        with self.assertRaisesRegex(ValueError, 'repeated_or_near_duplicate_title'):
            self.generate(draft_index=2, prior_drafts=[existing])
        self.assertEqual(existing, before)

    def test_endpoint_success_preserves_checkpoint_and_provenance(self):
        before = copy.deepcopy(self.checkpoint)
        response = self.post(evidence_output())
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.data['business_records_written'])
        self.assertEqual(response.data['provenance'], 'qwen_quality_single_authenticated_v7')
        self.assertEqual(response.data['authorized_requirement_count'], 114)
        self.assertEqual(response.data['source_digest'], 'a' * 64)
        self.assertEqual(self.checkpoint, before)
        self.assertEqual(len(self.calls), 1)

    def test_endpoint_failure_preserves_checkpoint_and_does_not_retry(self):
        before = copy.deepcopy(self.checkpoint)
        output = evidence_output()
        del output['attributes']['request_scope']
        response = self.post(output)
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.data['failure_reason'], 'local_ai_provider_schema_mismatch')
        self.assertEqual(response.data['validation_failure'], {
            'path': ['attributes'], 'rule': 'required',
        })
        self.assertFalse(response.data['business_records_written'])
        self.assertNotIn('draft', response.data)
        self.assertEqual(self.checkpoint, before)
        self.assertEqual(len(self.calls), 1)

    def test_schema_diagnostic_identifies_field_without_disclosing_its_value(self):
        output = evidence_output()
        output['attributes']['request_owner_role'] = {
            'secret': 'must-not-be-returned',
        }
        response = self.post(output)
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.data['validation_failure'], {
            'path': ['attributes', 'request_owner_role'], 'rule': 'type',
        })
        self.assertNotIn('must-not-be-returned', json.dumps(response.data))

    def test_request_can_describe_the_existing_sico_evidence_contract_without_saved_ids(self):
        draft = self.generate()['draft']
        fields = {a['field']: a['proposed_value'] for a in draft['proposed_attributes']}
        native = EvidenceRequestSerializer(data={
            'temporary_id': draft['draft_reference'], 'title': draft['title'],
            'description': draft['content'] + '\n' + json.dumps(fields),
            'rationale': fields['request_purpose'], 'linked_asset_ids': [],
            'linked_applied_control_ids': [], 'confidence': 0.0,
            'review_status': 'pending_review', 'ambiguity_flags': [],
        })
        self.assertTrue(native.is_valid(), native.errors)

    def test_other_activities_keep_legacy_checkpoint_contract_but_use_named_wire_attributes(self):
        for code in quality.CONTRACTS:
            with self.subTest(activity=code):
                legacy = quality.schema_for(code)
                Draft202012Validator.check_schema(legacy)
                wire = quality.quality_wire_schema_for(code)
                Draft202012Validator.check_schema(wire)
                attrs = wire['properties']['attributes']
                self.assertEqual(attrs['type'], 'object')
                self.assertEqual(set(attrs['required']), set(quality.CONTRACTS[code][1]))



if __name__ == '__main__':
    unittest.main(verbosity=2)
