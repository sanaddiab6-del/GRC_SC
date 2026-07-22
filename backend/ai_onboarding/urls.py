from django.urls import path

from .views import (
    AiAppliedControlCommitView,
    AiAppliedControlSuggestionView,
    AiAssetCommitView,
    AiAssetSuggestionView,
    AiCaseIntakeView,
    AiCaseSetupView,
    AiEvidenceFindingCommitView,
    AiEvidenceFindingSuggestionView,
)


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
]