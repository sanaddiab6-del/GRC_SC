from django.urls import path

from .views import (
    AiAppliedControlCommitView,
    AiControlEffectivenessCommitView,
    AiControlEffectivenessSuggestionView,
    AiAppliedControlSuggestionView,
    AiAuditReadinessCommitView,
    AiAuditReadinessSuggestionView,
    AiAuditReportCommitView,
    AiAuditReportSuggestionView,
    AiAssetCommitView,
    AiAssetSuggestionView,
    AiCaseIntakeView,
    AiCaseSetupView,
    AiEvidenceFindingCommitView,
    AiFinalReviewCommitView,
    AiFinalReviewSuggestionView,
    AiEvidenceFindingSuggestionView,
    AiFrameworkControlMappingCommitView,
    AiFrameworkControlMappingSuggestionView,
    AiRemediationActionCommitView,
    AiRemediationActionSuggestionView,
    AiRiskScenarioCommitView,
    AiRiskScenarioSuggestionView,
)


from .audit_risk_preview_views import AiAssessmentAuditPreviewView, AiRiskMatrixPreviewView

from .workforce_discovery_views import AiWorkforceDiscoveryView

urlpatterns = [
    path("onboarding/case-intake/", AiCaseIntakeView.as_view(), name="ai-case-intake"),
    path("onboarding/case-setup/", AiCaseSetupView.as_view(), name="ai-case-setup"),
    path("onboarding/assets/suggest/", AiAssetSuggestionView.as_view(), name="ai-asset-suggestion"),
    path("onboarding/assets/commit/", AiAssetCommitView.as_view(), name="ai-asset-commit"),
    path(
        "onboarding/applied-controls/suggest/",
        AiAppliedControlSuggestionView.as_view(),
        name="ai-applied-control-suggestion",
    ),
    path(
        "onboarding/applied-controls/commit/",
        AiAppliedControlCommitView.as_view(),
        name="ai-applied-control-commit",
    ),
    path(
        "onboarding/evidence-findings/suggest/",
        AiEvidenceFindingSuggestionView.as_view(),
        name="ai-evidence-finding-suggestion",
    ),
    path(
        "onboarding/evidence-findings/commit/",
        AiEvidenceFindingCommitView.as_view(),
        name="ai-evidence-finding-commit",
    ),
    path(
        "onboarding/remediation-actions/suggest/",
        AiRemediationActionSuggestionView.as_view(),
        name="ai-remediation-action-suggestion",
    ),
    path(
        "onboarding/remediation-actions/commit/",
        AiRemediationActionCommitView.as_view(),
        name="ai-remediation-action-commit",
    ),
    path(
        "onboarding/framework-control-mappings/suggest/",
        AiFrameworkControlMappingSuggestionView.as_view(),
        name="ai-framework-control-mapping-suggestion",
    ),
    path(
        "onboarding/framework-control-mappings/commit/",
        AiFrameworkControlMappingCommitView.as_view(),
        name="ai-framework-control-mapping-commit",
    ),
    path(
        "onboarding/risk-scenarios/suggest/",
        AiRiskScenarioSuggestionView.as_view(),
        name="ai-risk-scenario-suggestion",
    ),
    path(
        "onboarding/risk-scenarios/commit/",
        AiRiskScenarioCommitView.as_view(),
        name="ai-risk-scenario-commit",
    ),
    path(
        "onboarding/control-effectiveness/suggest/",
        AiControlEffectivenessSuggestionView.as_view(),
        name="ai-control-effectiveness-suggestion",
    ),
    path(
        "onboarding/control-effectiveness/commit/",
        AiControlEffectivenessCommitView.as_view(),
        name="ai-control-effectiveness-commit",
    ),
    path(
        "onboarding/audit-readiness/suggest/",
        AiAuditReadinessSuggestionView.as_view(),
        name="ai-audit-readiness-suggestion",
    ),
    path(
        "onboarding/audit-readiness/commit/",
        AiAuditReadinessCommitView.as_view(),
        name="ai-audit-readiness-commit",
    ),
    path(
        "onboarding/audit-report/suggest/",
        AiAuditReportSuggestionView.as_view(),
        name="ai-audit-report-suggestion",
    ),
    path(
        "onboarding/audit-report/commit/",
        AiAuditReportCommitView.as_view(),
        name="ai-audit-report-commit",
    ),
    path(
        "onboarding/final-review/suggest/",
        AiFinalReviewSuggestionView.as_view(),
        name="ai-final-review-suggestion",
    ),
    path(
        "onboarding/final-review/commit/",
        AiFinalReviewCommitView.as_view(),
        name="ai-final-review-commit",
    ),
]
# SICO AI Workforce V1: read-only auditing and existing-matrix risk scoring.
urlpatterns += [
    path("workforce/audit-preview/", AiAssessmentAuditPreviewView.as_view(), name="sico-ai-audit-preview"),
    path("workforce/risk-score-preview/", AiRiskMatrixPreviewView.as_view(), name="sico-ai-risk-score-preview"),
]
# SICO AI Workforce: strictly read-only grounded database discovery.
urlpatterns += [path('workforce/discover/', AiWorkforceDiscoveryView.as_view(), name='sico-ai-workforce-discover')]

# SICO AI workforce V3: authenticated preflight ONLY; no create actions.
from .workforce_case_plan_views import AiWorkforceNewCasePlanView
urlpatterns += [path('workforce/new-case-plan/', AiWorkforceNewCasePlanView.as_view(), name='sico-ai-workforce-new-case-plan')]
