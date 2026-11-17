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

# SICO AI: independent review and approval of prepared operations.
from .engagement_approval_views import AiEngagementApprovalView

urlpatterns += [
    path(
        'workforce/engagements/<uuid:engagement_id>/approval/',
        AiEngagementApprovalView.as_view(),
        name='sico-engagement-approval',
    ),
]

# SICO AI Next read-only, authenticated coordinator planning endpoint.
from .sico_ai_plan_views import SicoAiPlanView
urlpatterns += [
    path("workforce/assistant/plan/", SicoAiPlanView.as_view(), name="sico-ai-coordinator-plan"),
]

# sico-ai-platform-hub-v1: 11 reviewed stages, commits off unless independently enabled.
from .sico_ai_tool_hub_views import (
    SicoAiToolCatalogView, SicoAiToolPrepareView, SicoAiToolCommitView,
)
urlpatterns += [
    path('workforce/assistant/tools/catalog/', SicoAiToolCatalogView.as_view(), name='sico-ai-tool-catalog'),
    path('workforce/assistant/tools/prepare/', SicoAiToolPrepareView.as_view(), name='sico-ai-tool-prepare'),
    path('workforce/assistant/tools/commit/', SicoAiToolCommitView.as_view(), name='sico-ai-tool-commit'),
]
# sico-ai-router-phase2: AI-selected REVIEWED stages; read-only and no GRC writes.
from .sico_ai_router_views import SicoAiCapabilityRouterView
urlpatterns += [
    path('workforce/assistant/route/', SicoAiCapabilityRouterView.as_view(), name='sico-ai-capability-router'),
]

# Model-driven read-only execution; no approval/commit dispatch is registered.
from .sico_ai_agent_views import SicoAiAgentView
urlpatterns += [
    path('workforce/assistant/execute/', SicoAiAgentView.as_view(), name='sico-ai-agent-execute'),
]

# SICO AI Next — approval-controlled, resumable GRC workflow.
# Preparation creates metadata/review only. Business commits OFF by default.
from .sico_ai_workflow_views import (
    WorkflowOptionsView, WorkflowPrepareView, WorkflowReviewView,
    WorkflowApproveView, WorkflowCommitView, WorkflowResumeView,
)
urlpatterns += [
    path('workforce/assistant/workflow/options/', WorkflowOptionsView.as_view(), name='sico-ai-workflow-options'),
    path('workforce/assistant/workflow/prepare/', WorkflowPrepareView.as_view(), name='sico-ai-workflow-prepare'),
    path('workforce/assistant/workflow/review/', WorkflowReviewView.as_view(), name='sico-ai-workflow-review'),
    path('workforce/assistant/workflow/approve/', WorkflowApproveView.as_view(), name='sico-ai-workflow-approve'),
    path('workforce/assistant/workflow/commit/', WorkflowCommitView.as_view(), name='sico-ai-workflow-commit'),
    path('workforce/assistant/workflow/resume/', WorkflowResumeView.as_view(), name='sico-ai-workflow-resume'),
]

# Full one-prompt SICO lifecycle: selected human scope, reviewed GRC writers.
from .sico_ai_lifecycle_views import (
    LifecycleStartView, LifecycleStatusView, LifecycleDraftNextView,
    LifecycleStageReviewView, LifecycleStageApproveView, LifecycleStageCommitView,
)
urlpatterns += [
    path('workforce/assistant/lifecycle/start/', LifecycleStartView.as_view(), name='sico-ai-lifecycle-start'),
    path('workforce/assistant/lifecycle/status/', LifecycleStatusView.as_view(), name='sico-ai-lifecycle-status'),
    path('workforce/assistant/lifecycle/next/', LifecycleDraftNextView.as_view(), name='sico-ai-lifecycle-next'),
    path('workforce/assistant/lifecycle/review/', LifecycleStageReviewView.as_view(), name='sico-ai-lifecycle-review'),
    path('workforce/assistant/lifecycle/approve/', LifecycleStageApproveView.as_view(), name='sico-ai-lifecycle-approve'),
    path('workforce/assistant/lifecycle/commit/', LifecycleStageCommitView.as_view(), name='sico-ai-lifecycle-commit'),
]

# Three-input SICO AI intake — verified human-selected organization, framework and goal.
from .sico_ai_lifecycle_views import LifecycleThreeInputView
urlpatterns += [
    path('workforce/assistant/lifecycle/intake/', LifecycleThreeInputView.as_view(), name='sico-ai-three-input-intake'),
]


# SICO AI genuine model-generated, permission-scoped assessment draft.
# This route cannot approve or write GRC business records.
from .sico_ai_generated_assessment_views import SicoAiGeneratedAssessmentView
urlpatterns += [
    path('workforce/assistant/lifecycle/generate/', SicoAiGeneratedAssessmentView.as_view(),
         name='sico-ai-generated-assessment'),
]

# Four bounded batches generate 16 real AI draft work products from three inputs,
# including a brand-new company name. No domain or business record is created here.
from .sico_ai_sixteen_generate_views import SicoSixteenGenerateBatchView
urlpatterns += [
    path('workforce/assistant/lifecycle/generate-four/', SicoSixteenGenerateBatchView.as_view(),
         name='sico-ai-generate-four-activities'),
]

# Incremental Qwen generation: one validated activity per call.
from .sico_ai_sixteen_generate_views import SicoSixteenGenerateItemView
urlpatterns += [
    path('workforce/assistant/lifecycle/generate-one/', SicoSixteenGenerateItemView.as_view(),
         name='sico-ai-generate-one-activity'),
]

# SICO AI: save and verify Qwen-generated preliminary observations on the
# existing RequirementAssessment table. No automatic compliance verdicts.
from .sico_ai_requirement_review_views import SicoAiRequirementReviewView
urlpatterns += [
    path('workforce/assistant/lifecycle/requirements/review/',
         SicoAiRequirementReviewView.as_view(),
         name='sico-ai-requirement-initial-review'),
]

# SICO AI creation-first: NEW structured drafts, no GRC writes or case IDs.
from .sico_ai_case_draft_views import SicoCaseDraftPhaseView
urlpatterns += [path('workforce/assistant/case-draft/phase/', SicoCaseDraftPhaseView.as_view(),
                    name='sico-case-draft-phase')]

# Authorized framework requirements for the existing SICO AI workflow. Read-only; RBAC rechecked on every page.
from .authorized_framework_source import AuthorizedFrameworkSourcePageView
urlpatterns += [path("workforce/assistant/framework-source/page/", AuthorizedFrameworkSourcePageView.as_view(),
                    name="sico-ai-framework-source-page")]

# Single-record quality-gated Qwen generation, with authenticated SICO framework
# grounding. This keeps the existing HTML runner strategy inside SICO AI Next.
from .sico_ai_case_quality_views import SicoQualityDraftOneView
urlpatterns += [path('workforce/assistant/case-draft/quality-one/', SicoQualityDraftOneView.as_view(),
                    name='sico-ai-quality-draft-one')]
