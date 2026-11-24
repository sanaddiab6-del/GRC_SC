"""Focused engine/API tests; no database access allowed in this module."""
from types import SimpleNamespace
from unittest.mock import Mock, patch

from django.test import SimpleTestCase
from rest_framework.test import APIRequestFactory, force_authenticate

from .llm_errors import AiProviderExecutionError
from .llm_provider import _build_ollama_prompt, _ollama_output_format
from .sico_ai_agent import AgentBlocked, AgentLimits, decision_schema, run_agent
from .sico_ai_agent_views import SicoAiAgentView


def tool(name='frameworks.search', arguments=None):
    return dict(kind='tool', explanation='Look up the requested records.', tool=name,
                arguments=arguments if arguments is not None else {'query': 'NCA ECC'})


def final(**changes):
    result = dict(kind='final', explanation='Explain retrieved records.',
                  answer='NCA ECC was found. Scope and evidence need review.',
                  citations=['observation_1'], unresolved=['Confirm scope and supporting evidence.'])
    result.update(changes)
    return result


class AgentTests(SimpleTestCase):
    def setUp(self):
        self.registry = Mock()
        self.registry.catalog.return_value = [dict(name='frameworks.search', arguments={
            'type': 'object', 'properties': {'query': {'type': 'string'}},
            'required': ['query'], 'additionalProperties': False,
        })]
        self.registry.execute.return_value = {'records': [{'id': 'real-record', 'name': 'NCA ECC'}]}
        self.provider = Mock()
        self.selection = SimpleNamespace(provider=self.provider, config=SimpleNamespace(
            model='qwen3:4b-instruct', timeout_seconds=30, max_output_tokens=1200))

    def run_loop(self, **kwargs):
        return run_agent(instruction='Find NCA ECC and inspect authorized compliance information.',
                         registry=self.registry, selection=self.selection, **kwargs)

    def test_actual_observation_goes_back_before_second_decision(self):
        self.provider.generate_structured.side_effect = [tool(), final()]
        outcome = self.run_loop()
        self.assertEqual(outcome['status'], 'completed')
        self.assertEqual(len(outcome['verified_results']), 1)
        second = self.provider.generate_structured.call_args_list[1].kwargs['user_payload']
        self.assertEqual(second['observations'][0]['result'], self.registry.execute.return_value)
        self.assertFalse(outcome['writes_enabled'])

    def test_model_can_chain_different_modules(self):
        self.registry.catalog.return_value.append(dict(name='assets.list', arguments={
            'type': 'object', 'properties': {}, 'additionalProperties': False,
        }))
        self.provider.generate_structured.side_effect = [tool(), tool('assets.list', {}), final(citations=['observation_1', 'observation_2'])]
        outcome = self.run_loop()
        self.assertEqual(outcome['status'], 'completed')
        self.assertEqual(self.registry.execute.call_args_list[1].args[:2], ('assets.list', {}))

    def test_invalid_tool_selection_is_never_dispatched(self):
        self.provider.generate_structured.return_value = tool('delete_everything')
        self.assertEqual(self.run_loop()['status'], 'invalid_decision')
        self.registry.execute.assert_not_called()

    def test_premature_answer_in_tool_decision_is_refused(self):
        decision = tool()
        decision['answer'] = 'Invented completed assessment'
        self.provider.generate_structured.return_value = decision
        self.assertEqual(self.run_loop()['status'], 'invalid_decision')
        self.registry.execute.assert_not_called()

    def test_blocked_without_observations_has_no_record_claim(self):
        self.provider.generate_structured.return_value = final(kind='blocked', citations=[], answer='Invented facts')
        outcome = self.run_loop()
        self.assertEqual(outcome['status'], 'blocked')
        self.assertNotIn('Invented facts', outcome['final_answer'])

    def test_failed_argument_validation_returns_error_to_model(self):
        self.registry.execute.side_effect = AgentBlocked('Tool arguments failed independent validation.')
        self.provider.generate_structured.side_effect = [tool(), final(kind='blocked', citations=[])]
        outcome = self.run_loop()
        self.assertEqual(outcome['status'], 'blocked')
        self.assertEqual(outcome['verified_results'], [])
        payload = self.provider.generate_structured.call_args_list[1].kwargs['user_payload']
        self.assertEqual(payload['observations'][0]['status'], 'failed')

    def test_unsupported_citations_fail_closed(self):
        self.provider.generate_structured.side_effect = [tool(), final(citations=['invented'])]
        self.assertEqual(self.run_loop()['status'], 'invalid_decision')

    def test_final_cannot_omit_a_successful_source(self):
        self.registry.catalog.return_value.append(dict(name='assets.list', arguments={
            'type': 'object', 'properties': {}, 'additionalProperties': False,
        }))
        self.provider.generate_structured.side_effect = [tool(), tool('assets.list', {}), final()]
        self.assertEqual(self.run_loop()['status'], 'invalid_decision')

    def test_no_success_claim_without_verified_results(self):
        self.provider.generate_structured.return_value = final(citations=[])
        self.assertEqual(self.run_loop()['status'], 'invalid_decision')

    def test_model_failure_preserves_partial_verified_trace(self):
        self.provider.generate_structured.side_effect = [tool(), AiProviderExecutionError('test', 'secret')]
        outcome = self.run_loop()
        self.assertEqual(outcome['status'], 'model_failed')
        self.assertEqual(len(outcome['verified_results']), 1)
        self.assertNotIn('secret', str(outcome))

    def test_schema_failure_gets_one_bounded_repair_without_tool_reexecution(self):
        self.provider.generate_structured.side_effect = [
            tool(), AiProviderExecutionError('local_ai_provider_schema_mismatch', 'secret'), final(),
        ]
        outcome = self.run_loop()
        self.assertEqual(outcome['status'], 'completed')
        self.assertEqual(outcome['model_validation_retries'], 1)
        self.assertEqual(self.registry.execute.call_count, 1)
        self.assertEqual(outcome['trace'][1]['origin'], 'server_validation')
        self.assertTrue(self.provider.generate_structured.call_args.kwargs['user_payload']['validation_feedback'])
        self.assertNotIn('secret', str(outcome))

    def test_schema_repair_does_not_retry_indefinitely(self):
        self.provider.generate_structured.side_effect = [
            tool(), AiProviderExecutionError('local_ai_provider_schema_mismatch', 'one'),
            AiProviderExecutionError('local_ai_provider_schema_mismatch', 'two'),
        ]
        outcome = self.run_loop()
        self.assertEqual(outcome['status'], 'model_failed')
        self.assertEqual(outcome['model_validation_retries'], 1)
        self.assertEqual(outcome['model_calls'], 3)

    def test_step_limit(self):
        self.provider.generate_structured.return_value = tool()
        outcome = self.run_loop(limits=AgentLimits(max_steps=0))
        self.assertEqual(outcome['status'], 'step_limit')
        self.assertEqual(outcome['model_calls'], 0)

    def test_final_bounded_turn_cannot_request_another_tool(self):
        self.provider.generate_structured.side_effect = [tool(), final()]
        outcome = self.run_loop(limits=AgentLimits(max_steps=2))
        self.assertEqual(outcome['status'], 'completed')
        last = self.provider.generate_structured.call_args_list[-1].kwargs
        self.assertEqual(last['user_payload']['available_tools'], [])
        self.assertTrue(last['user_payload']['final_response_required'])
        self.assertNotIn('tool', last['json_schema']['properties'])
        self.assertEqual(self.registry.execute.call_count, 1)

    def test_duplicate_success_is_not_executed_again(self):
        self.provider.generate_structured.side_effect = [tool(), tool(), final()]
        outcome = self.run_loop()
        self.assertEqual(outcome['status'], 'completed')
        self.assertEqual(self.registry.execute.call_count, 1)
        self.assertEqual(outcome['observations'][1]['status'], 'failed')
        self.assertTrue(self.provider.generate_structured.call_args.kwargs['user_payload']['final_response_required'])

    def test_cancel_after_first_tool(self):
        self.provider.generate_structured.return_value = tool()
        outcome = self.run_loop(cancelled=lambda: self.registry.execute.call_count > 0)
        self.assertEqual(outcome['status'], 'interrupted')
        self.assertEqual(self.registry.execute.call_count, 1)

    def test_deadline_before_execution(self):
        self.provider.generate_structured.return_value = tool()
        late = AgentLimits().total_seconds + 1
        clock = iter([0, 0, 0, late])
        outcome = self.run_loop(now=lambda: next(clock, late))
        self.assertEqual(outcome['status'], 'timeout')
        self.registry.execute.assert_not_called()

    def test_context_limit_does_not_silently_drop_observations(self):
        self.assertEqual(self.run_loop(limits=AgentLimits(max_context_chars=10))['status'], 'context_limit')
        self.provider.generate_structured.assert_not_called()

    def test_revoked_access_clears_retained_data(self):
        self.provider.generate_structured.side_effect = [tool(), final()]
        self.registry.reauthorize_results.side_effect = [None, None, AgentBlocked('revoked'), AgentBlocked('revoked')]
        outcome = self.run_loop()
        self.assertEqual(outcome['status'], 'blocked')
        self.assertEqual(outcome['observations'], [])
        self.assertEqual(outcome['trace'], [])
        self.assertEqual(outcome['final_answer'], '')

    def test_large_result_not_claimed_verified(self):
        self.registry.execute.return_value = {'text': 'x' * 7000}
        self.provider.generate_structured.side_effect = [tool(), final(kind='blocked', citations=[])]
        self.assertEqual(self.run_loop()['verified_results'], [])

    def test_provider_uses_agent_schema_without_intake_skeleton(self):
        schema = decision_schema(self.registry.catalog.return_value)
        self.assertEqual(_ollama_output_format('sico_ai_agent_decision_v1', schema), schema)
        prompt = _build_ollama_prompt(capability='grc_capability_selection', system_prompt='agent',
                                      user_payload={}, json_schema=schema, schema_name='sico_ai_agent_decision_v1')
        self.assertNotIn('AiCaseIntakeDraft', prompt)

    def test_unauthenticated_request(self):
        request = APIRequestFactory().post('/execute/', {'instruction': 'Find available NCA ECC frameworks'}, format='json')
        self.assertIn(SicoAiAgentView.as_view()(request).status_code, (401, 403))

    @patch('ai_onboarding.sico_ai_agent_views.GrcReadRegistry')
    @patch('ai_onboarding.sico_ai_agent_views.get_advisory_provider_selection')
    def test_unauthorized_folder_never_reaches_model(self, select, registry):
        registry.return_value.authorize.side_effect = AgentBlocked('forbidden')
        request = APIRequestFactory().post('/execute/', {'instruction': 'Find available NCA ECC frameworks'}, format='json')
        force_authenticate(request, user=SimpleNamespace(pk='user', is_authenticated=True))
        self.assertEqual(SicoAiAgentView.as_view()(request).status_code, 403)
        select.assert_not_called()
