"""Offline Activity 10 tests: the model copies the selected SICO requirement reference.

Before this fix the prompt showed both `reference` and the internal `requirement_id`,
and the model kept writing the id into framework_requirement_reference, so every
Activity 10 draft was rejected. No DB, Docker or model calls.
"""
import json
import unittest

from jsonschema import Draft202012Validator, ValidationError

from ai_onboarding.tests import test_quality_evidence_requests as evidence_tests
from ai_onboarding import quality_sico_drafts_v5 as quality
from ai_onboarding.llm_errors import AiProviderExecutionError

CHOSEN = {'reference': '4.1', 'requirement_id': 'c4a01c41-a1ba-4130-b19d-825c3914133d',
          'requirement_name': 'Understanding the organization and its context',
          'description': 'The organization shall determine external and internal issues.'}


def review_output(reference='4.1'):
    return {
        'title': 'Requirement review: Context issues applicability walkthrough',
        'content': (
            'Review the selected requirement by interviewing the proposed process owner, '
            'mapping documented internal and external issues to the scope, and assessing '
            'whether the record is current. No conformity result is established; the '
            'reviewer records gaps for human signoff.'
        ),
        'attributes': {
            'framework_requirement_reference': reference,
            'review_method': 'Owner interview plus document walkthrough of the proposed context register.',
            'evidence_needed': 'Dated context register and management review minutes; scope to confirm.',
            'review_status': 'Pending human review; no assessment result recorded.',
        },
        'evidence_request': 'Request the dated context register and the latest management review minutes from the owner.',
        'verification_question': 'Does the context register list current internal and external issues for the agreed scope?',
        'related_draft_references': ['draft-07-01'],
    }


class RequirementReviewTests(unittest.TestCase):
    transport = evidence_tests.EvidenceRequestTests.transport

    def setUp(self):
        evidence_tests.EvidenceRequestTests.setUp(self)

    def generate(self, output=None):
        with self.transport(review_output() if output is None else output):
            return quality.generate_quality_draft(
                self.selection, organization='Offline example', framework='ISO/IEC 27001:2022',
                objective='Review the selected requirement for the proposed scope.',
                phase=9, draft_index=1, prior_drafts=[], case_context=self.context,
                authorized_requirements=[CHOSEN], chosen_requirement=CHOSEN)

    def ref_schema(self):
        return self.calls[0]['format']['properties']['attributes']['properties']['framework_requirement_reference']

    def test_selected_reference_is_the_only_value_the_schema_allows(self):
        result = self.generate()
        self.assertEqual(self.ref_schema(), {'type': 'string', 'maxLength': 180, 'enum': ['4.1']})
        self.assertEqual(result['draft']['framework_requirement_mapping_status'], 'verified_SICO_authorized_record')
        self.assertEqual(result['draft']['authorized_requirement_id'], CHOSEN['requirement_id'])

    def test_internal_requirement_id_is_never_sent_to_the_model(self):
        self.generate()
        self.assertNotIn(CHOSEN['requirement_id'], json.dumps(self.calls[0]))
        self.assertIn('4.1', self.calls[0]['prompt'])

    def test_model_writing_the_internal_id_is_still_rejected(self):
        with self.assertRaises((ValueError, AiProviderExecutionError)):
            self.generate(review_output(reference=CHOSEN['requirement_id']))

    def test_short_reference_keeps_a_satisfiable_schema(self):
        schema = quality.quality_wire_schema_for('requirement_reviews', allowed_related=['draft-07-01'],
                                                 selected_requirement_ref='A1')
        Draft202012Validator(schema).validate(review_output(reference='A1'))
        with self.assertRaises(ValidationError):
            Draft202012Validator(schema).validate(review_output(reference='A2'))
        # Code that states the limits to the model reads maxLength from every attribute.
        for name, spec in schema['properties']['attributes']['properties'].items():
            self.assertEqual(spec.get('maxLength'), 180, name)

    def test_other_activities_keep_the_requirement_id_and_bounds(self):
        self.assertEqual(
            quality.quality_wire_schema_for('requirement_reviews')['properties']['attributes']
            ['properties']['framework_requirement_reference'],
            {'type': 'string', 'minLength': 3, 'maxLength': 180})
        with self.transport(evidence_tests.evidence_output()):
            quality.generate_quality_draft(
                self.selection, organization='Offline example', framework='NCA ECC',
                objective='Request evidence for the proposed privileged access control.',
                phase=8, draft_index=1, prior_drafts=[], case_context=self.context,
                authorized_requirements=[dict(CHOSEN, description='privileged access evidence export')])
        self.assertIn(CHOSEN['requirement_id'], self.calls[0]['prompt'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
