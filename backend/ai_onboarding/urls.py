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

# SICO AI Phase 2A: strictly read-only, folder-scoped relationship discovery.
from .risk_relationship_preview_views import AiRiskRelationshipPreviewView
urlpatterns += [path('onboarding/risk-scenarios/relationship-preview/', AiRiskRelationshipPreviewView.as_view(), name='ai-risk-relationship-preview')]
# SICO AI full Risk Scenario review: read-only, exact-folder catalog.
from .risk_scenario_full_context_views import AiRiskFullContextView
urlpatterns += [path('onboarding/risk-scenarios/full-context/', AiRiskFullContextView.as_view(), name='ai-risk-full-context')]

# SICO AI engagement coordination: durable execution receipts and protected reuse
# of existing multi-module GRC services. No legacy /onboarding routes changed.
from .engagement_views import (
    AiEngagementListCreateView, AiEngagementDetailView, AiEngagementOperationView,
)
urlpatterns += [
    path('workforce/engagements/', AiEngagementListCreateView.as_view(), name='sico-engagements'),
    path('workforce/engagements/<uuid:engagement_id>/', AiEngagementDetailView.as_view(), name='sico-engagement-detail'),
    path('workforce/engagements/<uuid:engagement_id>/operation/', AiEngagementOperationView.as_view(), name='sico-engagement-operation'),
]
from .engagement_views import AiEngagementPlanView
urlpatterns += [
    path('workforce/engagements/<uuid:engagement_id>/plan/', AiEngagementPlanView.as_view(), name='sico-engagement-plan'),
]

# SICO multi-module resume: read-only POST for the existing frontend proxy.
from .engagement_views import AiEngagementResumeView
urlpatterns += [path('workforce/engagements/resume/', AiEngagementResumeView.as_view(), name='sico-engagement-resume')]


# SICO AI: authenticated, review-only full-platform capability selection.
from .engagement_capability_views import AiEngagementCapabilitiesView

urlpatterns += [
    path(
        'workforce/engagements/<uuid:engagement_id>/capabilities/',
        AiEngagementCapabilitiesView.as_view(),
        name='sico-engagement-capabilities',
    ),
]

# SICO AI case-setup preparation: no commit or approval endpoint.
from .sico_case_setup_views import SicoCaseSetupPrepareView

urlpatterns += [
    path(
        'workforce/engagements/<uuid:engagement_id>/case-setup/prepare/',
        SicoCaseSetupPrepareView.as_view(),
        name='sico-engagement-case-setup-prepare',
    ),
]
# Automatic case-setup preparation from an authorized engagement.
# No AI approval or commit route is provided.
from .sico_case_setup_views import SicoCaseSetupAutoPrepareView

urlpatterns += [
    path(
        'workforce/engagements/<uuid:engagement_id>/case-setup/auto-prepare/',
        SicoCaseSetupAutoPrepareView.as_view(),
        name='sico-engagement-case-setup-auto-prepare',
    ),
]