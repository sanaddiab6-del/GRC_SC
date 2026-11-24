"""Isolated, no-DB tests for model-driven reviewed-capability selection."""
from types import SimpleNamespace
from unittest.mock import patch
from uuid import uuid4

from django.test import SimpleTestCase
from rest_framework.test import APIRequestFactory, force_authenticate

from .engagement_rules import STAGES
from .sico_ai_router_views import (
    INVENTORY_AREAS, SicoAiCapabilityRouterView, parse_model_selection,
)


class RoutingTests(SimpleTestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = SimpleNamespace(pk=uuid4(), is_authenticated=True)
        self.allowed = tuple(x.slug for x in STAGES)

    def post(self, instruction='Assess compliance and risk for a Saudi hospital under NCA ECC'):
        req = self.factory.post('/api/ai/workforce/assistant/route/', {'instruction': instruction}, format='json')
        force_authenticate(req, user=self.user)
        return SicoAiCapabilityRouterView.as_view()(req)

    def test_inventory_counts(self):
        self.assertEqual(sum(INVENTORY_AREAS.values()), 245)
        self.assertEqual(len(self.allowed), 11)

    def test_stage_order_owned_by_registry(self):
        self.assertEqual(parse_model_selection('risk_scenarios,case_setup', self.allowed), ['case_setup', 'risk_scenarios'])

    def test_none_is_empty(self):
        self.assertEqual(parse_model_selection('NONE', self.allowed), [])

    def test_reject_invented_tool(self):
        with self.assertRaises(ValueError):
            parse_model_selection('case_setup,delete_everything', self.allowed)

    def test_reject_duplicate_tool(self):
        with self.assertRaises(ValueError):
            parse_model_selection('assets,assets', self.allowed)

    def test_reject_free_text(self):
        with self.assertRaises(ValueError):
            parse_model_selection('I would recommend assets.', self.allowed)

    def test_reject_blank_answer(self):
        with self.assertRaises(ValueError):
            parse_model_selection(' ', self.allowed)

    def test_reject_invalid_auth(self):
        req = self.factory.post('/api/ai/workforce/assistant/route/', {'instruction': 'Assess compliance and risk for a Saudi hospital under NCA ECC'}, format='json')
        reply = SicoAiCapabilityRouterView.as_view()(req)
        self.assertIn(reply.status_code, (401, 403))

    @patch('ai_onboarding.sico_ai_router_views.get_advisory_provider_selection')
    @patch('ai_onboarding.sico_ai_router_views.resolve_advisory_capability_config')
    def test_model_selects_without_executing(self, cfg, select):
        cfg.return_value = SimpleNamespace()
        model = SimpleNamespace(model='qwen3:4b-instruct', timeout_seconds=60, max_output_tokens=500)
        provider = SimpleNamespace(generate_structured=lambda **kwargs: {'answer': 'risk_scenarios,case_setup'})
        select.return_value = SimpleNamespace(provider=provider, config=model)
        reply = self.post()
        self.assertEqual(reply.status_code, 200)
        self.assertEqual(reply.data['selected_stages'], ['case_setup', 'risk_scenarios'])
        self.assertFalse(reply.data['execution_performed'])
        self.assertFalse(reply.data['grc_records_written'])

    @patch('ai_onboarding.sico_ai_router_views.get_advisory_provider_selection')
    @patch('ai_onboarding.sico_ai_router_views.resolve_advisory_capability_config')
    def test_bad_model_selection_fails_closed(self, cfg, select):
        cfg.return_value = SimpleNamespace()
        model = SimpleNamespace(model='qwen3:4b-instruct', timeout_seconds=60, max_output_tokens=500)
        provider = SimpleNamespace(generate_structured=lambda **kwargs: {'answer': 'arbitrary_admin_delete'})
        select.return_value = SimpleNamespace(provider=provider, config=model)
        reply = self.post()
        self.assertEqual(reply.status_code, 422)
