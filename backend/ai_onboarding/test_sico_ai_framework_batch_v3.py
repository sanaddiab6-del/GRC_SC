"""No-DB endpoint contract tests for the opt-in, read-only Activity 1 v3 mode."""
from types import SimpleNamespace
from unittest.mock import patch

from django.test import SimpleTestCase
from rest_framework.test import APIRequestFactory, force_authenticate

from . import sico_ai_sixteen_generate_views as views
from . import sico_ai_framework_batch_v3 as full


class FrameworkBatchV3EndpointTests(SimpleTestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = SimpleNamespace(pk='test-user', is_authenticated=True, is_active=True)
        self.inputs = {
            'organization_name': 'Sky Line',
            'framework_name': 'ISO 27001:2022',
            'problem': 'Assess the organization against the selected standard and request supporting evidence.',
            'activity_number': 1,
            'full_framework_batch': True,
        }

    def post(self, **changes):
        payload = {**self.inputs, **changes}
        request = self.factory.post('/api/ai/workforce/assistant/lifecycle/generate-one/', payload, format='json')
        force_authenticate(request, user=self.user)
        return views.SicoSixteenGenerateItemView.as_view()(request)

    @patch.object(full, 'generate_framework_batch')
    @patch.object(views, 'get_advisory_provider_selection')
    @patch.object(views, 'resolve_advisory_capability_config')
    def test_v3_uses_existing_endpoint_and_selection(self, resolve, choose, generate):
        generate.return_value = {
            'status': 'partial', 'coverage': {'accessible_total': 114, 'reviewed_through': 2},
            'requirement_reviews': [{'reference': 'REAL-CONTROL'}],
            'next_cursor': 'signed-cursor', 'business_records_written': False,
        }
        result = self.post(framework_batch_size=2)
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.data['framework_batch']['coverage']['accessible_total'], 114)
        self.assertFalse(result.data['business_records_written'])
        self.assertEqual(generate.call_args.kwargs['framework'], 'ISO 27001:2022')
        self.assertEqual(generate.call_args.kwargs['user'].pk, 'test-user')

    def test_v3_disallowed_for_other_activities(self):
        result = self.post(activity_number=2)
        self.assertEqual(result.status_code, 400)

    @patch.object(full, 'generate_framework_batch', side_effect=full.FrameworkBatchError('invalid_or_stale_cursor'))
    @patch.object(views, 'get_advisory_provider_selection')
    @patch.object(views, 'resolve_advisory_capability_config')
    def test_stale_cursor_fails_closed(self, resolve, choose, generate):
        result = self.post(framework_cursor='invalid')
        self.assertEqual(result.status_code, 409)
        self.assertEqual(result.data['error_kind'], 'invalid_or_stale_cursor')
        self.assertFalse(result.data['business_records_written'])

    @patch.object(views, 'generate_one', return_value={'number': 1, 'state': 'ai_draft_not_executed'})
    @patch.object(views, 'get_advisory_provider_selection')
    @patch.object(views, 'resolve_advisory_capability_config')
    def test_legacy_path_unchanged_without_opt_in(self, resolve, choose, generate):
        result = self.post(full_framework_batch=False)
        self.assertEqual(result.status_code, 200)
        self.assertIn('activity', result.data)
        self.assertNotIn('framework_batch', result.data)
        self.assertEqual(generate.call_args.kwargs['activity_number'], 1)
