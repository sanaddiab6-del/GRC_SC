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
from .framework_control_mapping_commit_guardrails import (
    FrameworkControlMappingCommitValidationError,
    validate_framework_control_mapping_commit_guardrails,
)
from .framework_control_mapping_commit_serializers import (
    AiFrameworkControlMappingCommitInputSerializer,
)
from .framework_control_mapping_commit_service import (
    execute_framework_control_mapping_commit,
)
from .framework_control_mapping_suggestion_guardrails import (
    FrameworkControlMappingSuggestionDraftValidationError,
    validate_framework_control_mapping_suggestion_request_guardrails,
)
from .framework_control_mapping_suggestion_provider import (
    FrameworkControlMappingSuggestionProviderError,
)
from .framework_control_mapping_suggestion_serializers import (
    AiFrameworkControlMappingSuggestionInputSerializer,
)
from .framework_control_mapping_suggestion_service import (
    build_framework_control_mapping_suggestion_draft,
)
from .evidence_finding_commit_guardrails import EvidenceFindingCommitValidationError
from .evidence_finding_commit_serializers import AiEvidenceFindingCommitInputSerializer
from .evidence_finding_commit_service import execute_evidence_finding_commit
from .evidence_finding_suggestion_guardrails import EvidenceFindingSuggestionDraftValidationError
from .evidence_finding_suggestion_provider import EvidenceFindingSuggestionProviderError
from .evidence_finding_suggestion_serializers import AiEvidenceFindingSuggestionInputSerializer
from .evidence_finding_suggestion_service import build_evidence_finding_suggestion_draft
from .remediation_action_commit_guardrails import RemediationActionCommitValidationError
from .remediation_action_commit_serializers import AiRemediationActionCommitInputSerializer
from .remediation_action_commit_service import execute_remediation_action_commit
from .remediation_action_suggestion_guardrails import (
    RemediationActionSuggestionDraftValidationError,
    validate_remediation_action_suggestion_request_guardrails,
)
from .remediation_action_suggestion_provider import RemediationActionSuggestionProviderError
from .remediation_action_suggestion_serializers import (
    AiRemediationActionSuggestionInputSerializer,
)
from .remediation_action_suggestion_service import build_remediation_action_suggestion_draft
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


class AiEvidenceFindingSuggestionView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(request=AiEvidenceFindingSuggestionInputSerializer)
    def post(self, request, format=None):
        serializer = AiEvidenceFindingSuggestionInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            with transaction.atomic():
                draft = build_evidence_finding_suggestion_draft(
                    request,
                    serializer.validated_data,
                    base_dir=str(settings.BASE_DIR.parent),
                )
                transaction.set_rollback(True)
        except (
            EvidenceFindingSuggestionDraftValidationError,
            EvidenceFindingSuggestionProviderError,
        ) as exc:
            return Response(exc.to_response(), status=exc.status_code)

        return Response(draft)


class AiEvidenceFindingCommitView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(request=AiEvidenceFindingCommitInputSerializer)
    def post(self, request, format=None):
        serializer = AiEvidenceFindingCommitInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            result = execute_evidence_finding_commit(request, serializer.validated_data)
        except EvidenceFindingCommitValidationError as exc:
            return Response(exc.to_response(), status=exc.status_code)

        return Response(result)


class AiRemediationActionSuggestionView(APIView):
    """Step 6A: advisory remediation/action-plan suggestion. No database writes."""

    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(request=AiRemediationActionSuggestionInputSerializer)
    def post(self, request, format=None):
        request_guardrail_errors = validate_remediation_action_suggestion_request_guardrails(
            request.data if isinstance(request.data, dict) else {}
        )
        if request_guardrail_errors:
            return Response(request_guardrail_errors, status=400)

        serializer = AiRemediationActionSuggestionInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            with transaction.atomic():
                draft = build_remediation_action_suggestion_draft(
                    serializer.validated_data,
                    base_dir=str(settings.BASE_DIR.parent),
                )
                transaction.set_rollback(True)
        except (
            RemediationActionSuggestionDraftValidationError,
            RemediationActionSuggestionProviderError,
        ) as exc:
            return Response(exc.to_response(), status=exc.status_code)

        return Response(draft)


class AiFrameworkControlMappingSuggestionView(APIView):
    """Step 7A: advisory framework control mapping suggestion. No database writes.

    Mappings may only point at framework controls that already exist: either supplied in
    candidate_framework_controls or found by a safe read-only lookup. No frameworks,
    requirements, framework controls, or mappings are created here.
    """

    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(request=AiFrameworkControlMappingSuggestionInputSerializer)
    def post(self, request, format=None):
        request_guardrail_errors = (
            validate_framework_control_mapping_suggestion_request_guardrails(
                request.data if isinstance(request.data, dict) else {}
            )
        )
        if request_guardrail_errors:
            return Response(request_guardrail_errors, status=400)

        serializer = AiFrameworkControlMappingSuggestionInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            with transaction.atomic():
                draft = build_framework_control_mapping_suggestion_draft(
                    request,
                    serializer.validated_data,
                    base_dir=str(settings.BASE_DIR.parent),
                )
                transaction.set_rollback(True)
        except (
            FrameworkControlMappingSuggestionDraftValidationError,
            FrameworkControlMappingSuggestionProviderError,
        ) as exc:
            return Response(exc.to_response(), status=exc.status_code)

        return Response(draft)


class AiFrameworkControlMappingCommitView(APIView):
    """Step 7B: deterministic framework control mapping commit. No AI provider is used."""

    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(request=AiFrameworkControlMappingCommitInputSerializer)
    def post(self, request, format=None):
        try:
            # Run on the raw payload so AI/provider, write-intent, and raw-identifier keys
            # are reported through the Step 7B blocking_errors contract rather than as a
            # generic unknown-field error.
            validate_framework_control_mapping_commit_guardrails(
                request.data if isinstance(request.data, dict) else {}
            )
        except FrameworkControlMappingCommitValidationError as exc:
            return Response(exc.to_response(), status=exc.status_code)

        serializer = AiFrameworkControlMappingCommitInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            result = execute_framework_control_mapping_commit(
                request, serializer.validated_data
            )
        except FrameworkControlMappingCommitValidationError as exc:
            return Response(exc.to_response(), status=exc.status_code)

        return Response(result)


class AiRemediationActionCommitView(APIView):
    """Step 6B: deterministic remediation action commit. No AI provider is used."""

    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(request=AiRemediationActionCommitInputSerializer)
    def post(self, request, format=None):
        serializer = AiRemediationActionCommitInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            result = execute_remediation_action_commit(request, serializer.validated_data)
        except RemediationActionCommitValidationError as exc:
            return Response(exc.to_response(), status=exc.status_code)

        return Response(result)