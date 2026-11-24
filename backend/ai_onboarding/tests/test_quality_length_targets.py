"""Offline tests: shorter length targets in the prompt and the CJK-character gate.

Told only the hard limits, the model wrote up to them and Ollama cut fields mid-word,
sometimes finishing with a Chinese word. No DB, Docker or model calls.
"""
import unittest

from ai_onboarding.tests import test_quality_evidence_requests as evidence_tests
from ai_onboarding import quality_sico_drafts_v5 as quality
from ai_onboarding.llm_errors import AiProviderExecutionError


class LengthTargetRuleTests(unittest.TestCase):
    def test_every_activity_gets_targets_below_its_hard_limits(self):
        for code in quality.CONTRACTS:
            with self.subTest(activity=code):
                schema = quality.quality_wire_schema_for(code)
                rules = ' '.join(quality.output_rules_for(code, schema))
                props = schema['properties']
                attr_max = max(p['maxLength'] for p in props['attributes']['properties'].values())
                # Hard limits are still stated unchanged.
                self.assertIn(f"{props['content']['minLength']}-{props['content']['maxLength']}", rules)
                self.assertIn(f'at most {attr_max} characters', rules)
                # Targets are stated and stay below the limits.
                low, high = quality.TARGET_CONTENT_CHARS
                fewest, most = quality.TARGET_CONTENT_SENTENCES
                self.assertIn(f'Write {fewest}-{most} complete sentences', rules)
                self.assertIn(f'roughly {low}-{high} characters', rules)
                self.assertLess(high, props['content']['maxLength'])
                self.assertGreater(low, props['content']['minLength'])
                for field, target in quality.TARGET_MAX_CHARS.items():
                    limit = attr_max if field == 'attribute' else props[field]['maxLength']
                    self.assertLess(target, limit, field)
                    self.assertIn(f'aim for at most {target}', rules)
                self.assertIn('Latin characters only', rules)

    def test_schema_hard_limits_are_unchanged(self):
        props = quality.quality_wire_schema_for('assets')['properties']
        self.assertEqual(props['content']['maxLength'], 670)
        self.assertEqual(props['evidence_request']['maxLength'], 260)
        self.assertEqual(props['verification_question']['maxLength'], 240)
        for spec in props['attributes']['properties'].values():
            self.assertEqual(spec['maxLength'], 180)

    def test_cjk_rejection_has_a_server_hint(self):
        hint = quality.rejection_hint('assets', 'cjk_characters_in_draft')
        self.assertIn('Latin characters only', hint)


def at_limit(text, limit):
    """Pad the front so `text` ends exactly at `limit`, as Ollama's cut does."""
    filler = ('The proposed payment database stores wallet transactions for mobile customers. '
              'Support staff reach it through laptops and a cloud identity provider. '
              'Owners must confirm scope, classification and retention before any assessment. ')
    padding = (filler * 10)[-(limit - len(text)):] if limit > len(text) else ''
    return padding + text


class DropUnfinishedSentenceTests(unittest.TestCase):
    drop = staticmethod(quality.drop_unfinished_sentence)

    def test_cut_content_ends_at_its_last_full_sentence(self):
        for fragment in ('The asset is managed through a', 'This isa', 'The U',
                         'by restricting and', 'This action directly addresses A.'):
            with self.subTest(fragment):
                text = at_limit('Access is reviewed every quarter. ' + fragment, 670)
                self.assertEqual(len(text), 670)
                result = self.drop(text, 670, min_length=115, min_distinct_words=19)
                self.assertTrue(result.endswith('Access is reviewed every quarter.'), result[-60:])

    def test_numbered_steps_keep_complete_steps_only(self):
        steps = ('1. Configure MFA policies for all privileged API roles. 2. Assign MFA to all users '
                 'with elevated access. 3. Restrict API access to only approved roles. 4.')
        text = at_limit(steps, 180)[-180:]
        result = self.drop(text, 180, min_length=3)
        self.assertTrue(result.endswith('3. Restrict API access to only approved roles.'), result)

    def test_text_below_the_limit_is_never_changed(self):
        text = 'A shorter field that simply has no final period'
        self.assertEqual(self.drop(text, 180, min_length=3), text)

    def test_text_is_kept_when_trimming_would_break_a_minimum(self):
        text = at_limit('Short. ' + 'x' * 160, 180)
        self.assertEqual(self.drop(text, 180, min_length=170), text)
        single = 'y' * 180
        self.assertEqual(self.drop(single, 180, min_length=3), single)

    def test_generation_trims_before_the_gates(self):
        case = CjkGateTests('test_clean_english_draft_is_accepted')
        case.setUp()
        output = evidence_tests.evidence_output()
        output['content'] = at_limit('No compliance result is established yet. The request is managed through a', 670)
        output['attributes']['request_scope'] = at_limit(
            'Proposed identity service and administrator accounts. Confirm boundaries with', 180)
        draft = case.generate(output)['draft']
        self.assertTrue(draft['content'].endswith('No compliance result is established yet.'))
        scope = next(a['proposed_value'] for a in draft['proposed_attributes'] if a['field'] == 'request_scope')
        self.assertTrue(scope.endswith('administrator accounts.'), scope)


class CjkGateTests(unittest.TestCase):
    transport = evidence_tests.EvidenceRequestTests.transport

    def setUp(self):
        evidence_tests.EvidenceRequestTests.setUp(self)

    def generate(self, output):
        with self.transport(output):
            return quality.generate_quality_draft(
                self.selection, organization='Offline example', framework='NCA ECC',
                objective='Request evidence for the proposed privileged access control.',
                phase=8, draft_index=1, prior_drafts=[], case_context=self.context)

    def test_clean_english_draft_is_accepted(self):
        self.assertEqual(self.generate(evidence_tests.evidence_output())['activity_code'], 'evidence_requests')

    def test_cjk_in_any_field_is_rejected(self):
        cases = {
            'content end (seen: 监控)': lambda d: d.update(content=d['content'][:-1] + ' and 监控'),
            'content single char (seen: 臾)': lambda d: d.update(content=d['content'] + '臾'),
            'title': lambda d: d.update(title=d['title'] + ' 异常'),
            'attribute (seen: 境)': lambda d: d['attributes'].update(request_scope='Proposed cloud 境'),
            'evidence_request': lambda d: d.update(evidence_request=d['evidence_request'] + ' 滥'),
            'verification_question': lambda d: d.update(verification_question='確認 ' + d['verification_question']),
            'korean': lambda d: d['attributes'].update(request_purpose='Support review 검토 of safeguard.'),
        }
        for name, change in cases.items():
            with self.subTest(name):
                output = evidence_tests.evidence_output()
                change(output)
                with self.assertRaisesRegex((ValueError, AiProviderExecutionError), 'cjk_characters_in_draft'):
                    self.generate(output)

    def test_arabic_text_is_not_rejected(self):
        output = evidence_tests.evidence_output()
        output['attributes']['request_owner_role'] = 'Proposed identity control owner at شركة عمّان للمدفوعات.'
        self.assertEqual(self.generate(output)['activity_code'], 'evidence_requests')


if __name__ == '__main__':
    unittest.main(verbosity=2)
