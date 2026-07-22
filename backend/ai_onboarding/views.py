from __future__ import annotations

from django.conf import settings
from django.db import transaction
from drf_spectacular.utils import extend_schema
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from .applied_control_commit_guardrails import AppliedControlCommitValidationError
from .applied_control_commit_serializers import AiAppliedControlCommitInputSerializer
from .applied_control_commit_service import execute_applied_control_commit
from .asset_commit_guardrails import AssetCommitValidationError
from .asset_commit_serializers import AiAssetCommitInputSerializer
from .asset_commit_service import execute_asset_commit
from .applied_control_suggestion_guardrails import AppliedControlSuggestionDraftValidationError
from .applied_control_suggestion_provider import AppliedControlSuggestionProviderError
from .applied_control_suggestion_serializers import AiAppliedControlSuggestionInputSerializer
from .applied_control_suggestion_service import build_applied_control_suggestion_draft
from .asset_suggestion_guardrails import AssetSuggestionDraftValidationError
from .asset_suggestion_provider import AssetSuggestionProviderError
from .asset_suggestion_serializers import AiAssetSuggestionInputSerializer
from .asset_suggestion_service import build_asset_suggestion_draft
from .case_setup_guardrails import CaseSetupValidationError
from .case_setup_serializers import AiCaseSetupInputSerializer
from .case_setup_service import execute_case_setup
from .case_intake_guardrails import CaseIntakeDraftValidationError
from .case_intake_provider import CaseIntakeProviderError
from .case_intake_serializers import AiCaseIntakeInputSerializer
from .case_intake_service import build_case_intake_draft


class AiCaseIntakeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(request=AiCaseIntakeInputSerializer)
    def post(self, request, format=None):
        serializer = AiCaseIntakeInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            with transaction.atomic():
                draft = build_case_intake_draft(
                    serializer.validated_data,
                    base_dir=str(settings.BASE_DIR.parent),
                )
                transaction.set_rollback(True)
        except (CaseIntakeDraftValidationError, CaseIntakeProviderError) as exc:
            return Response(exc.to_response(), status=exc.status_code)

        return Response(draft)


class AiCaseSetupView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(request=AiCaseSetupInputSerializer)
    def post(self, request, format=None):
        serializer = AiCaseSetupInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            result = execute_case_setup(request, serializer.validated_data)
        except CaseSetupValidationError as exc:
            return Response(exc.to_response(), status=exc.status_code)

        return Response(result)


class AiAssetSuggestionView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(request=AiAssetSuggestionInputSerializer)
    def post(self, request, format=None):
        serializer = AiAssetSuggestionInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            with transaction.atomic():
                draft = build_asset_suggestion_draft(
                    request,
                    serializer.validated_data,
                    base_dir=str(settings.BASE_DIR.parent),
                )
                transaction.set_rollback(True)
        except (AssetSuggestionDraftValidationError, AssetSuggestionProviderError) as exc:
            return Response(exc.to_response(), status=exc.status_code)

        return Response(draft)


class AiAssetCommitView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(request=AiAssetCommitInputSerializer)
    def post(self, request, format=None):
        serializer = AiAssetCommitInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            result = execute_asset_commit(request, serializer.validated_data)
        except AssetCommitValidationError as exc:
            return Response(exc.to_response(), status=exc.status_code)

        return Response(result)


class AiAppliedControlSuggestionView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, format=None):
        serializer = AiAppliedControlSuggestionInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            with transaction.atomic():
                draft = build_applied_control_suggestion_draft(
                    request,
                    serializer.validated_data,
                    base_dir=str(settings.BASE_DIR.parent),
                )
                transaction.set_rollback(True)
        except (
            AppliedControlSuggestionDraftValidationError,
            AppliedControlSuggestionProviderError,
        ) as exc:
            return Response(exc.to_response(), status=exc.status_code)

        return Response(draft)


class AiAppliedControlCommitView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(request=AiAppliedControlCommitInputSerializer)
    def post(self, request, format=None):
        serializer = AiAppliedControlCommitInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            result = execute_applied_control_commit(request, serializer.validated_data)
        except AppliedControlCommitValidationError as exc:
            return Response(exc.to_response(), status=exc.status_code)

        return Response(result)