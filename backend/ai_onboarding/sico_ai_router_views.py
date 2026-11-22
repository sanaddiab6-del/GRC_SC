"""Model-driven, read-only capability routing for the existing SICO GRC platform.

The local model selects reviewed stage slugs. It cannot call URLs, execute tools,
access records or authorize writes. This is deliberately NOT a full agent.
"""
from __future__ import annotations

import re

from rest_framework import permissions, serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .engagement_rules import STAGES
from .llm_config import CAPABILITY_CASE_INTAKE, resolve_advisory_capability_config
from .llm_errors import AiProviderExecutionError
from .llm_provider import get_advisory_provider_selection


class RouterInput(serializers.Serializer):
    instruction = serializers.CharField(min_length=20, max_length=12000)
    organization_hint = serializers.CharField(required=False, allow_blank=True, max_length=150)


# These figures are a static AST inventory, not verified permissions or live routes.
# The categories are useful for showing coverage without publishing internal paths.
INVENTORY_AREAS = {
    'assets': 7,
    'audits': 8,
    'controls_and_policies': 5,
    'evidence_and_findings': 12,
    'frameworks_and_compliance': 17,
    'organizations_and_identity': 43,
    'other_platform_functions': 122,
    'remediation_and_followup': 5,
    'reporting_and_exports': 8,
    'risks': 18,
}


def parse_model_selection(answer: str, allowed: tuple[str, ...]) -> list[str]:
    """Reject malformed/unknown tool IDs; never expand a model's access."""
    if not isinstance(answer, str) or not answer.strip() or len(answer) > 1200:
        raise ValueError('Invalid model routing response.')
    # Explicit, tiny grammar: comma-separated, exact stage slugs, or NONE.
    content = answer.strip()
    if content == 'NONE':
        return []
    tokens = [x.strip() for x in content.split(',')]
    if len(tokens) > len(allowed) or any(not re.fullmatch(r'[a-z_]+', t) for t in tokens):
        raise ValueError('Model selection did not match the required format.')
    if len(set(tokens)) != len(tokens) or any(t not in allowed for t in tokens):
        raise ValueError('Model proposed an unsupported or repeated capability.')
    if not tokens:
        raise ValueError('Missing selected capability.')
    return [name for name in allowed if name in tokens]


class SicoAiCapabilityRouterView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['post', 'options']

    def post(self, request, format=None):
        form = RouterInput(data=request.data)
        form.is_valid(raise_exception=True)
        data = form.validated_data
        allowed = tuple(s.slug for s in STAGES)
        config = resolve_advisory_capability_config(CAPABILITY_CASE_INTAKE)
        selection = get_advisory_provider_selection(config)
        if selection.provider is None:
            return Response({'detail': 'Local AI provider is unavailable; no operation selected.'}, status=503)
        prompt = (
            'You route requests to registered SICO GRC stages, but you have no execution authority. '
            'NCA ECC means Saudi National Cybersecurity Authority Essential Cybersecurity Controls. '
            'Choose stages only from the provided allowed list. For a complete GRC engagement, choose '
            'all relevant stages. Do not invent tools. If the user only asks a conceptual question, '
            'choose NONE. You MUST return a JSON object with exactly one field named answer. '
            'The answer string MUST be either NONE or a comma-separated list of exact lowercase '
            'stage slugs, with NO explanations or markdown. Every stage slug must occur in the '
            'allowed list. Selection does not execute or authorize anything.'
        )
        schema = {
            'type': 'object',
            'properties': {'answer': {'type': 'string'}},
            'required': ['answer'],
            'additionalProperties': False,
        }
        try:
            draft = selection.provider.generate_structured(
                capability=CAPABILITY_CASE_INTAKE,
                model=selection.config.model,
                system_prompt=prompt,
                user_payload={
                    'instruction': data['instruction'],
                    'organization_hint_unverified': data.get('organization_hint') or None,
                    'allowed_stage_slugs': list(allowed),
                },
                json_schema=schema,
                timeout_seconds=min(selection.config.timeout_seconds, 120),
                max_output_tokens=min(selection.config.max_output_tokens, 250),
                temperature=0.0,
                schema_name='sico_ai_simple_answer_v1',
            )
        except AiProviderExecutionError as exc:
            return Response({'detail': 'Model routing failed; no operations executed.', 'error_code': exc.error_code}, status=502)
        try:
            chosen = parse_model_selection(draft.get('answer') if isinstance(draft, dict) else None, allowed)
        except ValueError:
            return Response({'detail': 'Model returned unrecognized stage names; routing refused. No operations executed.'}, status=422)
        return Response({
            'routing_mode': 'ai_selected_reviewed_stages',
            'model': selection.config.model,
            'selected_stages': chosen,
            'selected_count': len(chosen),
            'reviewed_stage_count': len(allowed),
            'inventory_source': 'static_ast_inventory_20261110',
            'inventory_route_registrations': sum(INVENTORY_AREAS.values()),
            'inventory_area_counts': INVENTORY_AREAS,
            'inventory_warning': 'Registrations are not verified, authorized, distinct executable tools.',
            'scope_verified': False,
            'authorization_checked_for_target_records': False,
            'execution_performed': False,
            'grc_records_written': False,
            'next_step': 'Resolve an authorized organization and operation payload, then separately prepare and approve it.',
        }, status=status.HTTP_200_OK)
