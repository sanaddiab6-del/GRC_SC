from __future__ import annotations

from typing import Any

from django.utils import timezone

from core.models import AppliedControl, Asset, Threat, Vulnerability
from iam.models import Folder, RoleAssignment

from .risk_treatment_suggestion_guardrails import (
    RiskTreatmentSuggestionValidationError,
    validate_provider_output_guardrails,
)
from .risk_treatment_suggestion_provider import (
    RiskTreatmentSuggestionProviderError,
    get_risk_treatment_suggestion_provider,
)
from .risk_treatment_suggestion_serializers import (
    ADVISORY_NOTICE,
    MAX_CONTEXT_TEXT_LENGTH,
    MAX_LINKED_ITEMS_PER_RELATION,
    OUTCOME_INSUFFICIENT_CONTEXT,
    OUTCOME_PROVIDER_UNAVAILABLE,
    OUTCOME_SUGGESTED,
    ProviderTreatmentJudgementSerializer,
    RiskTreatmentSuggestionResultSerializer,
)


def _truncate(value: Any, *, max_length: int = MAX_CONTEXT_TEXT_LENGTH) -> str | None:
    text = str(value).strip() if value else ""
    if not text:
        return None
    return text if len(text) <= max_length else f"{text[: max_length - 1]}…"


def _rating_name(rating: dict[str, Any]) -> str | None:
    """Name of a rating from RiskScenario's own matrix helpers; None when not rated."""
    if not isinstance(rating, dict) or rating.get("value", -1) < 0:
        return None
    return _truncate(rating.get("name"), max_length=100)


def _visible(related_manager, model, user):
    """Linked objects of `model` the requesting user can actually view.

    A scenario can link assets, threats, or controls held in other folders. The UI masks those
    for a user who cannot see them, and the prompt must not reveal them either, so every linked
    relation is intersected with the user's own accessible ids before anything is read.
    """
    viewable_ids = RoleAssignment.get_accessible_object_ids(
        Folder.get_root_folder(), user, model
    )[0]
    return related_manager.filter(id__in=viewable_ids).order_by("name")


def build_risk_context(risk_scenario, user) -> dict[str, Any]:
    """Deterministic, bounded AI context for one RiskScenario, built only from that scenario and
    the linked objects the requesting user can view. Nothing is taken from client input and no
    other scenario, assessment, or folder is read."""
    assets = _visible(risk_scenario.assets, Asset, user)
    threats = _visible(risk_scenario.threats, Threat, user)
    vulnerabilities = _visible(risk_scenario.vulnerabilities, Vulnerability, user)
    existing_controls = _visible(risk_scenario.existing_applied_controls, AppliedControl, user)
    planned_controls = _visible(risk_scenario.applied_controls, AppliedControl, user)

    limit = MAX_LINKED_ITEMS_PER_RELATION
    risk_assessment = risk_scenario.risk_assessment
    tolerance = risk_assessment.risk_tolerance

    return {
        "name": _truncate(risk_scenario.name, max_length=200),
        "description": _truncate(risk_scenario.description),
        "current_treatment": risk_scenario.treatment,
        "justification": _truncate(risk_scenario.justification),
        "strength_of_knowledge": _truncate(
            risk_scenario.get_strength_of_knowledge().get("name"), max_length=50
        ),
        "risk_assessment": _truncate(risk_assessment.name, max_length=200),
        "ratings": {
            "inherent_level": _rating_name(risk_scenario.get_inherent_risk()),
            "current_probability": _rating_name(risk_scenario.get_current_proba()),
            "current_impact": _rating_name(risk_scenario.get_current_impact()),
            "current_level": _rating_name(risk_scenario.get_current_risk()),
            "residual_probability": _rating_name(risk_scenario.get_residual_proba()),
            "residual_impact": _rating_name(risk_scenario.get_residual_impact()),
            "residual_level": _rating_name(risk_scenario.get_residual_risk()),
            "risk_tolerance": _rating_name(risk_scenario._get_risk_data(tolerance, "risk")),
            "current_within_tolerance": risk_scenario.within_tolerance,
        },
        "threats": [_truncate(t.name, max_length=200) for t in threats[:limit]],
        "assets": [_truncate(a.name, max_length=200) for a in assets[:limit]],
        "vulnerabilities": [_truncate(v.name, max_length=200) for v in vulnerabilities[:limit]],
        "existing_controls": [
            {"name": _truncate(c.name, max_length=200), "status": c.status or ""}
            for c in existing_controls[:limit]
        ],
        "planned_controls": [
            {"name": _truncate(c.name, max_length=200), "status": c.status or ""}
            for c in planned_controls[:limit]
        ],
        "counts": {
            "assets": assets.count(),
            "threats": threats.count(),
            "vulnerabilities": vulnerabilities.count(),
            "existing_controls": existing_controls.count(),
            "planned_controls": planned_controls.count(),
        },
    }


def _has_reviewable_context(context: dict[str, Any]) -> bool:
    """Nothing to reason about: no description, no rating, and nothing linked."""
    return bool(
        context["description"]
        or context["ratings"]["current_level"]
        or any(context["counts"].values())
    )


def _no_suggestion(reason: str, consideration: str) -> dict[str, Any]:
    return {
        "suggested_treatment": None,
        "confidence": 0.0,
        "rationale": reason,
        "mitigating_actions": [],
        "considerations": [consideration],
    }


def _judge(context: dict[str, Any], *, provider=None) -> tuple[dict[str, Any], str, str, list]:
    """Returns (judgement, outcome, provider_mode, warnings). Never writes."""
    if not _has_reviewable_context(context):
        return (
            _no_suggestion(
                "This risk scenario has no description, no risk rating, and no linked "
                "threats, assets, vulnerabilities, or controls to base a suggestion on.",
                "Rate the current risk and link the relevant threats and assets first.",
            ),
            OUTCOME_INSUFFICIENT_CONTEXT,
            "not_called_insufficient_context",
            [],
        )

    resolved_provider = provider if provider is not None else get_risk_treatment_suggestion_provider()
    if resolved_provider is None:
        return (
            _no_suggestion(
                "No local AI provider is configured, so no treatment was suggested.",
                "Review the treatment manually.",
            ),
            OUTCOME_PROVIDER_UNAVAILABLE,
            "provider_not_configured_fallback",
            ["No local AI provider is configured."],
        )

    try:
        raw = resolved_provider.suggest_treatment(context)
    except RiskTreatmentSuggestionProviderError as exc:
        if not exc.allow_fallback:
            raise
        return (
            _no_suggestion(
                "The local AI provider could not be reached or timed out, so no treatment "
                "was suggested.",
                "Try again later, or review the treatment manually.",
            ),
            OUTCOME_PROVIDER_UNAVAILABLE,
            "local_provider_error_fallback",
            [f"AI suggestion could not be completed: {exc.detail}"],
        )

    serializer = ProviderTreatmentJudgementSerializer(data=raw)
    if not serializer.is_valid():
        raise RiskTreatmentSuggestionValidationError(
            "ai_risk_treatment_suggestion_draft_validation_failed",
            "Generated advisory risk treatment output did not pass contract validation.",
            serializer.errors,
        )
    judgement = {
        "suggested_treatment": serializer.validated_data["suggested_treatment"],
        "confidence": serializer.validated_data["confidence"],
        "rationale": serializer.validated_data["rationale"],
        "mitigating_actions": [
            dict(action) for action in serializer.validated_data.get("mitigating_actions", [])
        ],
        "considerations": list(serializer.validated_data.get("considerations", [])),
    }
    validate_provider_output_guardrails(judgement)
    return judgement, OUTCOME_SUGGESTED, "configured_local_provider", []


def suggest_risk_treatment(risk_scenario, user, *, provider=None) -> dict[str, Any]:
    """Advisory, read-only treatment suggestion for one existing RiskScenario.

    Never writes to the scenario, its ratings or treatment, or any control, assessment, or
    remediation. Identifiers, counts, and the timestamp are attached here from the real object,
    never taken from the model's output.
    """
    context = build_risk_context(risk_scenario, user)
    judgement, outcome, provider_mode, warnings = _judge(context, provider=provider)

    result = {
        "risk_scenario_id": str(risk_scenario.id),
        "risk_scenario_name": risk_scenario.name or "",
        "current_treatment": risk_scenario.treatment,
        "outcome": outcome,
        **judgement,
        "is_rated": context["ratings"]["current_level"] is not None,
        "linked_assets_count": context["counts"]["assets"],
        "linked_threats_count": context["counts"]["threats"],
        "existing_controls_count": context["counts"]["existing_controls"],
        "planned_controls_count": context["counts"]["planned_controls"],
        "provider_mode": provider_mode,
        "warnings": warnings,
        "advisory_notice": ADVISORY_NOTICE,
        "reviewed_at": timezone.now(),
    }

    serializer = RiskTreatmentSuggestionResultSerializer(data=result)
    if not serializer.is_valid():
        raise RiskTreatmentSuggestionValidationError(
            "ai_risk_treatment_suggestion_result_validation_failed",
            "Risk treatment suggestion result did not pass contract validation.",
            serializer.errors,
        )
    return serializer.data
