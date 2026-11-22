"""Authenticated entry point for the existing SICO AI Next workspace."""
from rest_framework import permissions, serializers
from rest_framework.response import Response
from rest_framework.views import APIView

from .llm_config import CAPABILITY_GRC_CAPABILITY_SELECTION, resolve_advisory_capability_config
from .llm_errors import AiProviderError
from .llm_provider import get_advisory_provider_selection
from .sico_ai_agent import run_agent
from .sico_ai_agent_tools import GrcReadRegistry


class AgentInput(serializers.Serializer):
    instruction = serializers.CharField(min_length=20, max_length=12000)
    organization_hint = serializers.CharField(required=False, allow_blank=True, max_length=150)
    folder_id = serializers.UUIDField(required=False)


class SicoAiAgentView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['post', 'options']

    def post(self, request, format=None):
        form = AgentInput(data=request.data)
        form.is_valid(raise_exception=True)
        data = form.validated_data
        registry = GrcReadRegistry(request.user, folder_id=data.get('folder_id'),
                                   organization_hint=data.get('organization_hint', ''))
        try:
            registry.authorize()
        except Exception:
            return Response({'detail': 'Active authorized folder membership could not be verified.'}, status=403)
        try:
            config = resolve_advisory_capability_config(CAPABILITY_GRC_CAPABILITY_SELECTION)
            selection = get_advisory_provider_selection(config)
        except AiProviderError:
            return Response({'detail': 'Local AI configuration is unavailable. No operations executed.'}, status=503)
        outcome = run_agent(instruction=data['instruction'], registry=registry, selection=selection)
        return Response(outcome)
