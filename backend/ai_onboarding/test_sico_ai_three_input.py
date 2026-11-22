"""Fail-closed tests for SICO's three-input start: no business-record writes.

Executable without a live database: all ORM calls are mocked. The separately
verified PostgreSQL write and rollback tests remain mandatory before commits.
"""
from types import SimpleNamespace
from unittest.mock import patch, Mock
from uuid import uuid4

from django.test import SimpleTestCase
from rest_framework.test import APIRequestFactory, force_authenticate
from rest_framework.response import Response
from .sico_ai_lifecycle_views import LifecycleThreeInputView

MODULE = 'ai_onboarding.sico_ai_lifecycle_views'


class ThreeInputTests(SimpleTestCase):
    def setUp(self):
        self.user = SimpleNamespace(pk=uuid4(), is_authenticated=True, is_active=True)
        self.folder = SimpleNamespace(pk=uuid4(), name='Al-Rawasi Fintech')
        self.framework = SimpleNamespace(pk=uuid4(), name='Essential Cybersecurity Controls', ref_id='nca-ecc')
        self.factory = APIRequestFactory()
        self.payload = {
            'organization_name': self.folder.name,
            'framework_name': 'NCA ECC',
            'problem': 'Assess our payment platform across all applicable verified controls and risks.',
        }

    def invoke(self, payload):
        req = self.factory.post('/api/ai/workforce/assistant/lifecycle/intake/', payload, format='json')
        force_authenticate(req, user=self.user)
        return LifecycleThreeInputView.as_view()(req)

    def test_missing_company_has_no_side_effect(self):
        with patch(f'{MODULE}.verify_principal'), patch(f'{MODULE}._scope_candidates', return_value=[]), \
             patch(f'{MODULE}._framework_candidates', return_value=[self.framework]), \
             patch(f'{MODULE}.start_lifecycle_from_validated_input') as start:
            r = self.invoke(self.payload)
        self.assertEqual(r.status_code, 404)
        start.assert_not_called()

    def test_unknown_framework_never_uses_nearest_unrelated_library(self):
        with patch(f'{MODULE}.verify_principal'), patch(f'{MODULE}._scope_candidates', return_value=[self.folder]), \
             patch(f'{MODULE}._framework_candidates', return_value=[]), \
             patch(f'{MODULE}.start_lifecycle_from_validated_input') as start:
            r = self.invoke(self.payload)
        self.assertEqual(r.status_code, 404)
        start.assert_not_called()

    def test_ambiguous_framework_must_be_selected_by_human(self):
        other = SimpleNamespace(pk=uuid4(), name='Essential Cybersecurity Controls 2018', ref_id='ecc-2018')
        with patch(f'{MODULE}.verify_principal'), patch(f'{MODULE}._scope_candidates', return_value=[self.folder]), \
             patch(f'{MODULE}._framework_candidates', return_value=[self.framework, other]), \
             patch(f'{MODULE}.start_lifecycle_from_validated_input') as start:
            r = self.invoke(self.payload)
        self.assertEqual(r.status_code, 409)
        self.assertEqual(r.data['status'], 'needs_exact_selection')
        start.assert_not_called()

    def test_nca_ecc_alias_is_not_silent_framework_confirmation(self):
        with patch(f'{MODULE}.verify_principal'), patch(f'{MODULE}._scope_candidates', return_value=[self.folder]), \
             patch(f'{MODULE}._framework_candidates', return_value=[self.framework]), \
             patch(f'{MODULE}.start_lifecycle_from_validated_input') as start:
            r = self.invoke(self.payload)
        self.assertEqual(r.status_code, 409)
        self.assertEqual(len(r.data['frameworks']), 1)
        start.assert_not_called()

    def test_unrelated_supplied_framework_id_rejected(self):
        payload = {**self.payload, 'selected_framework_id': str(uuid4())}
        with patch(f'{MODULE}.verify_principal'), patch(f'{MODULE}._scope_candidates', return_value=[self.folder]), \
             patch(f'{MODULE}._framework_candidates', return_value=[self.framework]), \
             patch(f'{MODULE}.start_lifecycle_from_validated_input') as start:
            r = self.invoke(payload)
        self.assertEqual(r.status_code, 409)
        start.assert_not_called()

    def test_wrong_organization_id_rejected(self):
        payload = {**self.payload, 'selected_organization_id': str(uuid4())}
        with patch(f'{MODULE}.verify_principal'), patch(f'{MODULE}._scope_candidates', return_value=[self.folder]), \
             patch(f'{MODULE}._framework_candidates', return_value=[self.framework]), \
             patch(f'{MODULE}.start_lifecycle_from_validated_input') as start:
            r = self.invoke(payload)
        self.assertEqual(r.status_code, 403)
        start.assert_not_called()

    def test_verified_three_inputs_generate_scoped_existing_writer_payload(self):
        payload = {**self.payload, 'selected_framework_id': str(self.framework.pk)}
        prepared = Response({'engagement_id': str(uuid4()), 'review': {'operation_payload': {}},
                             'prepared_digest': 'a' * 64}, status=201)
        with patch(f'{MODULE}.verify_principal'), patch(f'{MODULE}._scope_candidates', return_value=[self.folder]), \
             patch(f'{MODULE}._framework_candidates', return_value=[self.framework]), \
             patch(f'{MODULE}.Perimeter.objects') as perimeters, \
             patch(f'{MODULE}.RiskMatrix.objects') as matrices, \
             patch(f'{MODULE}.add_allowed', return_value=True), \
             patch(f'{MODULE}.start_lifecycle_from_validated_input', return_value=prepared) as start:
            perimeters.filter.return_value.order_by.return_value.__getitem__.return_value = []
            matrices.all.return_value.order_by.return_value.__getitem__.return_value = []
            r = self.invoke(payload)
        self.assertEqual(r.status_code, 201)
        start.assert_called_once()
        validated = start.call_args.args[1]
        self.assertEqual(str(validated['folder_id']), str(self.folder.pk))
        self.assertEqual(str(validated['framework_id']), str(self.framework.pk))
        self.assertEqual(validated['instruction'], self.payload['problem'])
        self.assertTrue(validated['new_perimeter_name'])
        self.assertNotIn('risk_matrix_id', validated)
        self.assertEqual(r.data['resolved_from_three_inputs']['risk_assessment'],
                         'deferred_until_risk_matrix_verified')

    def test_no_perimeter_permission_or_unique_reuse_blocks(self):
        payload = {**self.payload, 'selected_framework_id': str(self.framework.pk)}
        with patch(f'{MODULE}.verify_principal'), patch(f'{MODULE}._scope_candidates', return_value=[self.folder]), \
             patch(f'{MODULE}._framework_candidates', return_value=[self.framework]), \
             patch(f'{MODULE}.Perimeter.objects') as perimeters, \
             patch(f'{MODULE}.add_allowed', return_value=False), \
             patch(f'{MODULE}.start_lifecycle_from_validated_input') as start:
            perimeters.filter.return_value.order_by.return_value.__getitem__.return_value = []
            r = self.invoke(payload)
        self.assertEqual(r.status_code, 403)
        start.assert_not_called()

    def test_input_is_rejected_if_problem_missing(self):
        payload = {**self.payload, 'problem': 'short'}
        with patch(f'{MODULE}.start_lifecycle_from_validated_input') as start:
            r = self.invoke(payload)
        self.assertEqual(r.status_code, 400)
        start.assert_not_called()
