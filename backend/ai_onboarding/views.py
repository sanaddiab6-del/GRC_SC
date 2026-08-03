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
from .audit_report_commit_guardrails import (
    AuditReportCommitValidationError,
    validate_audit_report_commit_guardrails,
)
from .audit_report_commit_serializers import AiAuditReportCommitInputSerializer
from .audit_report_commit_service import execute_audit_report_commit
from .audit_report_suggestion_guardrails import (
    AuditReportSuggestionDraftValidationError,
    validate_audit_report_suggestion_request_guardrails,
)
from .audit_report_suggestion_provider import AuditReportSuggestionProviderError
from .audit_report_suggestion_serializers import AiAuditReportSuggestionInputSerializer
from .audit_report_suggestion_service import build_audit_report_suggestion_draft
from .audit_readiness_commit_guardrails import (
    AuditReadinessCommitValidationError,
    validate_audit_readiness_commit_guardrails,
)
from .audit_readiness_commit_serializers import AiAuditReadinessCommitInputSerializer
from .audit_readiness_commit_service import execute_audit_readiness_commit
from .audit_readiness_suggestion_guardrails import (
    AuditReadinessSuggestionDraftValidationError,
    validate_audit_readiness_suggestion_request_guardrails,
)
from .audit_readiness_suggestion_provider import AuditReadinessSuggestionProviderError
from .audit_readiness_suggestion_serializers import (
    AiAuditReadinessSuggestionInputSerializer,
)
from .audit_readiness_suggestion_service import build_audit_readiness_suggestion_draft
from .control_effectiveness_commit_guardrails import (
    ControlEffectivenessCommitValidationError,
    validate_control_effectiveness_commit_guardrails,
)
from .control_effectiveness_commit_serializers import (
    AiControlEffectivenessCommitInputSerializer,
)
from .control_effectiveness_commit_service import execute_control_effectiveness_commit
from .control_effectiveness_suggestion_guardrails import (
    ControlEffectivenessSuggestionDraftValidationError,
    validate_control_effectiveness_suggestion_request_guardrails,
)
from .control_effectiveness_suggestion_provider import (
    ControlEffectivenessSuggestionProviderError,
)
from .control_effectiveness_suggestion_serializers import (
    AiControlEffectivenessSuggestionInputSerializer,
)
from .control_effectiveness_suggestion_service import (
    build_control_effectiveness_suggestion_draft,
)
from .final_review_commit_guardrails import (
    FinalReviewCommitValidationError,
    validate_final_review_commit_guardrails,
)
from .final_review_commit_serializers import AiFinalReviewCommitInputSerializer
from .final_review_commit_service import execute_final_review_commit
from .final_review_suggestion_guardrails import (
    FinalReviewSuggestionDraftValidationError,
    validate_final_review_suggestion_request_guardrails,
)
from .final_review_suggestion_provider import FinalReviewSuggestionProviderError
from .final_review_suggestion_serializers import AiFinalReviewSuggestionInputSerializer
from .final_review_suggestion_service import build_final_review_suggestion_draft
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
from .risk_scenario_commit_guardrails import (
    RiskScenarioCommitValidationError,
    validate_risk_scenario_commit_guardrails,
)
from .risk_scenario_commit_serializers import AiRiskScenarioCommitInputSerializer
from .risk_scenario_commit_service import execute_risk_scenario_commit
from .risk_scenario_suggestion_guardrails import (
    RiskScenarioSuggestionDraftValidationError,
    validate_risk_scenario_suggestion_request_guardrails,
)
from .risk_scenario_suggestion_provider import RiskScenarioSuggestionProviderError
from .risk_scenario_suggestion_serializers import AiRiskScenarioSuggestionInputSerializer
from .risk_scenario_suggestion_service import build_risk_scenario_suggestion_draft
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


class AiRiskScenarioSuggestionView(APIView):
    """Step 8A: advisory risk scenario suggestion. No database writes.

    Scenarios are advisory drafts only: no risk record is created, no risk is accepted or
    treated, and no assessment is closed.
    """

    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(request=AiRiskScenarioSuggestionInputSerializer)
    def post(self, request, format=None):
        request_guardrail_errors = validate_risk_scenario_suggestion_request_guardrails(
            request.data if isinstance(request.data, dict) else {}
        )
        if request_guardrail_errors:
            return Response(request_guardrail_errors, status=400)

        serializer = AiRiskScenarioSuggestionInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            with transaction.atomic():
                draft = build_risk_scenario_suggestion_draft(
                    serializer.validated_data,
                    base_dir=str(settings.BASE_DIR.parent),
                )
                transaction.set_rollback(True)
        except (
            RiskScenarioSuggestionDraftValidationError,
            RiskScenarioSuggestionProviderError,
        ) as exc:
            return Response(exc.to_response(), status=exc.status_code)

        return Response(draft)


class AiControlEffectivenessSuggestionView(APIView):
    """Step 9A: advisory control effectiveness suggestion. No database writes.

    Judgements are advisory drafts only: no RequirementAssessment is updated, no audit is
    closed, and no compliance is certified.
    """

    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(request=AiControlEffectivenessSuggestionInputSerializer)
    def post(self, request, format=None):
        request_guardrail_errors = (
            validate_control_effectiveness_suggestion_request_guardrails(
                request.data if isinstance(request.data, dict) else {}
            )
        )
        if request_guardrail_errors:
            return Response(request_guardrail_errors, status=400)

        serializer = AiControlEffectivenessSuggestionInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            with transaction.atomic():
                draft = build_control_effectiveness_suggestion_draft(
                    serializer.validated_data,
                    base_dir=str(settings.BASE_DIR.parent),
                )
                transaction.set_rollback(True)
        except (
            ControlEffectivenessSuggestionDraftValidationError,
            ControlEffectivenessSuggestionProviderError,
        ) as exc:
            return Response(exc.to_response(), status=exc.status_code)

        return Response(draft)


class AiFinalReviewCommitView(APIView):
    """Step 12B: deterministic case handoff commit. No AI provider is used.

    Only the audit's own observation note is appended to. The workflow is never marked
    complete, the audit status is never changed, the audit is never closed, and no
    compliance is certified.
    """

    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(request=AiFinalReviewCommitInputSerializer)
    def post(self, request, format=None):
        try:
            # Run on the raw payload so AI/provider, completion, and raw-identifier keys are
            # reported through the Step 12B blocking_errors contract rather than as a generic
            # unknown-field error.
            validate_final_review_commit_guardrails(
                request.data if isinstance(request.data, dict) else {}
            )
        except FinalReviewCommitValidationError as exc:
            return Response(exc.to_response(), status=exc.status_code)

        serializer = AiFinalReviewCommitInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            result = execute_final_review_commit(request, serializer.validated_data)
        except FinalReviewCommitValidationError as exc:
            return Response(exc.to_response(), status=exc.status_code)

        return Response(result)


class AiFinalReviewSuggestionView(APIView):
    """Step 12A: advisory final end-to-end review summary. No database writes.

    The summary is a review aid only: the workflow is never marked complete, no audit is
    closed, and no compliance is certified.
    """

    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(request=AiFinalReviewSuggestionInputSerializer)
    def post(self, request, format=None):
        request_guardrail_errors = validate_final_review_suggestion_request_guardrails(
            request.data if isinstance(request.data, dict) else {}
        )
        if request_guardrail_errors:
            return Response(request_guardrail_errors, status=400)

        serializer = AiFinalReviewSuggestionInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            with transaction.atomic():
                draft = build_final_review_suggestion_draft(
                    serializer.validated_data,
                    base_dir=str(settings.BASE_DIR.parent),
                )
                transaction.set_rollback(True)
        except (
            FinalReviewSuggestionDraftValidationError,
            FinalReviewSuggestionProviderError,
        ) as exc:
            return Response(exc.to_response(), status=exc.status_code)

        return Response(draft)


class AiAuditReportCommitView(APIView):
    """Step 11B: deterministic report save. No AI provider is used.

    The reviewed draft is stored as a DRAFT document record. The report is never marked
    final or published, the audit status is never changed, and no compliance is certified.
    """

    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(request=AiAuditReportCommitInputSerializer)
    def post(self, request, format=None):
        try:
            # Run on the raw payload so AI/provider, report-finalization, and raw-identifier
            # keys are reported through the Step 11B blocking_errors contract rather than as
            # a generic unknown-field error.
            validate_audit_report_commit_guardrails(
                request.data if isinstance(request.data, dict) else {}
            )
        except AuditReportCommitValidationError as exc:
            return Response(exc.to_response(), status=exc.status_code)

        serializer = AiAuditReportCommitInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            result = execute_audit_report_commit(request, serializer.validated_data)
        except AuditReportCommitValidationError as exc:
            return Response(exc.to_response(), status=exc.status_code)

        return Response(result)


class AiAuditReportSuggestionView(APIView):
    """Step 11A: advisory management/audit report draft. No database writes.

    The draft is never a final audit opinion, a compliance certification, or a
    regulator-approved result, and it always states that human review is required.
    """

    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(request=AiAuditReportSuggestionInputSerializer)
    def post(self, request, format=None):
        request_guardrail_errors = validate_audit_report_suggestion_request_guardrails(
            request.data if isinstance(request.data, dict) else {}
        )
        if request_guardrail_errors:
            return Response(request_guardrail_errors, status=400)

        serializer = AiAuditReportSuggestionInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            with transaction.atomic():
                draft = build_audit_report_suggestion_draft(
                    serializer.validated_data,
                    base_dir=str(settings.BASE_DIR.parent),
                )
                transaction.set_rollback(True)
        except (
            AuditReportSuggestionDraftValidationError,
            AuditReportSuggestionProviderError,
        ) as exc:
            return Response(exc.to_response(), status=exc.status_code)

        return Response(draft)


class AiAuditReadinessCommitView(APIView):
    """Step 10B: deterministic audit readiness commit. No AI provider is used.

    Only the audit's own observation note is appended to. The audit status is never
    changed, the audit is never marked ready or complete, and no compliance is certified.
    """

    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(request=AiAuditReadinessCommitInputSerializer)
    def post(self, request, format=None):
        try:
            # Run on the raw payload so AI/provider, readiness-marking, and raw-identifier
            # keys are reported through the Step 10B blocking_errors contract rather than as
            # a generic unknown-field error.
            validate_audit_readiness_commit_guardrails(
                request.data if isinstance(request.data, dict) else {}
            )
        except AuditReadinessCommitValidationError as exc:
            return Response(exc.to_response(), status=exc.status_code)

        serializer = AiAuditReadinessCommitInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            result = execute_audit_readiness_commit(request, serializer.validated_data)
        except AuditReadinessCommitValidationError as exc:
            return Response(exc.to_response(), status=exc.status_code)

        return Response(result)


class AiAuditReadinessSuggestionView(APIView):
    """Step 10A: advisory audit readiness summary. No database writes.

    The summary is a draft only: nothing is marked ready, nothing is closed, and no
    compliance is certified.
    """

    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(request=AiAuditReadinessSuggestionInputSerializer)
    def post(self, request, format=None):
        request_guardrail_errors = validate_audit_readiness_suggestion_request_guardrails(
            request.data if isinstance(request.data, dict) else {}
        )
        if request_guardrail_errors:
            return Response(request_guardrail_errors, status=400)

        serializer = AiAuditReadinessSuggestionInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            with transaction.atomic():
                draft = build_audit_readiness_suggestion_draft(
                    serializer.validated_data,
                    base_dir=str(settings.BASE_DIR.parent),
                )
                transaction.set_rollback(True)
        except (
            AuditReadinessSuggestionDraftValidationError,
            AuditReadinessSuggestionProviderError,
        ) as exc:
            return Response(exc.to_response(), status=exc.status_code)

        return Response(draft)


class AiControlEffectivenessCommitView(APIView):
    """Step 9B: deterministic control effectiveness commit. No AI provider is used.

    Only the auditor-owned result and observation of an existing RequirementAssessment are
    written. No audit status is changed, no audit is closed, and no compliance is certified.
    """

    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(request=AiControlEffectivenessCommitInputSerializer)
    def post(self, request, format=None):
        try:
            # Run on the raw payload so AI/provider, audit-closure, and raw-identifier keys
            # are reported through the Step 9B blocking_errors contract rather than as a
            # generic unknown-field error.
            validate_control_effectiveness_commit_guardrails(
                request.data if isinstance(request.data, dict) else {}
            )
        except ControlEffectivenessCommitValidationError as exc:
            return Response(exc.to_response(), status=exc.status_code)

        serializer = AiControlEffectivenessCommitInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            result = execute_control_effectiveness_commit(request, serializer.validated_data)
        except ControlEffectivenessCommitValidationError as exc:
            return Response(exc.to_response(), status=exc.status_code)

        return Response(result)


class AiRiskScenarioCommitView(APIView):
    """Step 8B: deterministic risk scenario commit. No AI provider is used."""

    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(request=AiRiskScenarioCommitInputSerializer)
    def post(self, request, format=None):
        try:
            # Run on the raw payload so AI/provider, risk-treatment, and raw-identifier keys
            # are reported through the Step 8B blocking_errors contract rather than as a
            # generic unknown-field error.
            validate_risk_scenario_commit_guardrails(
                request.data if isinstance(request.data, dict) else {}
            )
        except RiskScenarioCommitValidationError as exc:
            return Response(exc.to_response(), status=exc.status_code)

        serializer = AiRiskScenarioCommitInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            result = execute_risk_scenario_commit(request, serializer.validated_data)
        except RiskScenarioCommitValidationError as exc:
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