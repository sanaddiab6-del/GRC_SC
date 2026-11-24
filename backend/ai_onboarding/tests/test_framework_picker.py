"""Framework picker: list and suggestions help the user pick an exact name.

Nothing here may select a framework: _framework_candidates (exact name/reference)
stays the only way a typed name becomes a framework. No DB writes.
"""
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from rest_framework.test import APIRequestFactory, force_authenticate

from ai_onboarding import authorized_framework_source as source
from ai_onboarding import sico_ai_framework_batch_v3 as batch
from ai_onboarding import sico_ai_lifecycle_views as lifecycle

LIBRARY = [
    SimpleNamespace(pk=1, name='Essential Cybersecurity Controls', ref_id='essential-cybersecurity-controls'),
    SimpleNamespace(pk=2, name='International standard ISO/IEC 27001:2022', ref_id='ISO/IEC 27001:2022'),
    SimpleNamespace(pk=3, name='NIST CSF v2.0', ref_id='NIST-CSF-2.0'),
    SimpleNamespace(pk=4, name='Payment Card Industry Data Security Standard (PCI-DSS) 4.0.1', ref_id='PCI DSS 4.0.1'),
]
USER = SimpleNamespace(pk='u1', is_active=True, is_authenticated=True)


def names(rows):
    return [r.name for r in rows]


class MatchingTests(unittest.TestCase):
    def matches(self, query):
        return [f.name for f in LIBRARY if lifecycle.framework_name_matches(query, f.name, f.ref_id)]

    def test_typed_words_match_the_start_of_framework_words(self):
        iso, nist = LIBRARY[1].name, LIBRARY[2].name
        pci, ecc = LIBRARY[3].name, LIBRARY[0].name
        cases = {
            'iso 27001': [iso], 'ISO 27001': [iso], 'ISO/IEC 27001': [iso], 'iso 27': [iso],
            'IS': [iso], 'pci': [pci], 'PCI DSS': [pci], 'nist csf': [nist], 'n': [nist],
            'ecc': [ecc], 'nca ecc': [], 'essential': [ecc],
        }
        for query, expected in cases.items():
            with self.subTest(query=query):
                self.assertEqual(self.matches(query), expected)

    def test_single_letter_lists_every_framework_with_such_a_word(self):
        # "I" starts International, ISO, IEC and Industry.
        self.assertEqual(self.matches('I'), [LIBRARY[1].name, LIBRARY[3].name])

    def test_unrelated_or_empty_text_matches_nothing(self):
        for query in ('hello', '', '  ', '27002', 'iso 27002'):
            with self.subTest(query=query):
                self.assertEqual(self.matches(query), [])


FAKE_FRAMEWORK_MODEL = SimpleNamespace(objects=SimpleNamespace(order_by=lambda *fields: LIBRARY))


@patch.object(lifecycle, 'Framework', FAKE_FRAMEWORK_MODEL)
class ChoicesAndSuggestionsTests(unittest.TestCase):
    def test_choices_use_the_same_readable_rule_as_exact_matching(self):
        with patch.object(lifecycle, 'readable', side_effect=lambda user, model, pk: pk != 3):
            self.assertEqual(names(lifecycle.authorized_framework_choices(USER)),
                             [LIBRARY[0].name, LIBRARY[1].name, LIBRARY[3].name])

    def test_suggestions_never_include_unreadable_frameworks(self):
        with patch.object(lifecycle, 'readable', side_effect=lambda user, model, pk: pk != 2):
            self.assertEqual(lifecycle.framework_suggestions(USER, 'iso 27001'), [])
        with patch.object(lifecycle, 'readable', return_value=True):
            self.assertEqual(names(lifecycle.framework_suggestions(USER, 'iso 27001')), [LIBRARY[1].name])


class NeverSelectsTests(unittest.TestCase):
    def test_not_found_returns_suggestions_but_no_framework(self):
        with patch.object(lifecycle, '_framework_candidates', return_value=[]), \
             patch.object(lifecycle, 'framework_suggestions', return_value=[LIBRARY[1]]):
            meta, rows = batch._load_authorized_requirements(USER, 'iso 27001')
        self.assertEqual(meta['status'], 'not_found_or_not_authorized')
        self.assertEqual(meta['suggestions'], [LIBRARY[1].name])
        self.assertNotIn('framework_id', meta)
        self.assertEqual(list(rows), [])

    def test_ambiguous_exact_matches_do_not_add_suggestions(self):
        with patch.object(lifecycle, '_framework_candidates', return_value=LIBRARY[:2]), \
             patch.object(lifecycle, 'framework_suggestions') as suggest:
            meta, _ = batch._load_authorized_requirements(USER, 'x')
        self.assertEqual(meta['status'], 'ambiguous')
        self.assertEqual(meta['suggestions'], [])
        suggest.assert_not_called()

    def test_source_page_passes_suggestions_through(self):
        meta = {'status': 'not_found_or_not_authorized', 'candidates': [], 'suggestions': ['A']}
        with patch.object(source, '_load_authorized_requirements', return_value=(meta, iter(()))):
            page = source.read_authorized_source_page(user=USER, framework_name='a b')
        self.assertEqual(page['suggestions'], ['A'])
        self.assertEqual(page['requirements'], [])
        self.assertFalse(page['business_records_written'])


class ChoicesViewTests(unittest.TestCase):
    def test_view_returns_names_and_references_only(self):
        request = APIRequestFactory().post('/x', {}, format='json')
        force_authenticate(request, user=USER)
        stored = SimpleNamespace(pk='9f0c1a52-0d3e-4b71-a0de-3c2b1e4f5a6b', name='NIS2 Directive', ref_id='nis2', locale='en')
        with patch.object(lifecycle, 'authorized_framework_choices', return_value=LIBRARY[1:3]), \
             patch.object(lifecycle, 'unloaded_framework_libraries', return_value=[stored]):
            response = source.AuthorizedFrameworkChoicesView.as_view()(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['frameworks'], [
            {'name': LIBRARY[1].name, 'reference': LIBRARY[1].ref_id, 'loaded': True},
            {'name': LIBRARY[2].name, 'reference': LIBRARY[2].ref_id, 'loaded': True},
            {'name': 'NIS2 Directive', 'reference': 'nis2', 'loaded': False, 'library_id': stored.pk, 'locale': 'en'},
        ])
        self.assertFalse(response.data['business_records_written'])

    def test_listing_unloaded_libraries_never_loads_or_matches_them(self):
        # An unloaded library is never an exact match, so it can never start AI drafting.
        with patch.object(lifecycle, '_framework_candidates', return_value=[]), \
             patch.object(lifecycle, 'framework_suggestions', return_value=[]):
            meta, rows = batch._load_authorized_requirements(USER, 'NIS2 Directive')
        self.assertEqual(meta['status'], 'not_found_or_not_authorized')
        self.assertEqual(list(rows), [])


if __name__ == '__main__':
    unittest.main(verbosity=2)
