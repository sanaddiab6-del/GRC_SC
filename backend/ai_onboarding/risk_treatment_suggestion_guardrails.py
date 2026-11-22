from __future__ import annotations

import re
from typing import Any

from .risk_treatment_suggestion_serializers import (
    ACTION_PRIORITY_CHOICES,
    SUGGESTABLE_TREATMENT_CHOICES,
)


# This capability is advisory/no-write. These keys would imply a write, an approval, a
# committed decision, or a model-supplied identifier the server must own, and are forbidden
# anywhere in the model output (including inside each mitigating action) and in the request.
FORBIDDEN_KEYS = {
    "commit",
    "committed",
    "execute",
    "approve",
    "approved",
    "accepted",
    "applied",
    "apply_all",
    "auto_apply",
    "auto_create",
    "create_now",
    "create_remediation",
    "create_control",
    "create_applied_control",
    "update_risk",
    "update_treatment",
    "set_treatment",
    "treatment",
    "change_residual_risk",
    "change_current_risk",
    "current_level",
    "residual_level",
    "close_risk",
    "mark_complete",
    "delete",
    "dry_run",
    "idempotency_key",
    "status",
    "risk_scenario_id",
    "risk_assessment_id",
    "folder_id",
    "user_id",
    "applied_control_id",
    "control_id",
    "remediation_id",
}

# Claimed-action language: the model asserting that something in the platform was already done.
# Deliberately narrow so advisory phrasing ("Recommend mitigating the risk", "Consider
# accepting", "The risk could be transferred") is never rejected just because it names a
# treatment; only past/perfect claims about the risk, its treatment, or new records match.
_CLAIM_PATTERNS = tuple(
    re.compile(pattern, re.IGNORECASE)
    for pattern in (
        # "I have applied ...", "we have created ...", "I set the treatment ...". "we" needs
        # the perfect tense so a conditional such as "if we accepted this risk" is not caught.
        r"\b((i|we)\s+have|i)\s+(accepted|applied|created|added|updated|changed|set|"
        r"closed|approved|marked|mitigated|transferred|avoided|recorded|saved)\b",
        # "the risk has been accepted", "treatment was applied", "risk scenario is now closed"
        r"\b(risk|risk\s+scenario|treatment)\s+(has\s+been|have\s+been|was|is\s+now)\s+"
        r"(accepted|applied|closed|approved|mitigated|transferred|avoided|set|changed|"
        r"updated|recorded)\b",
        # "remediation was created", "controls have been created", "new control has been added"
        r"\b(remediation(\s+actions?)?|(new\s+)?(applied\s+)?controls?)\s+"
        r"(has\s+been|have\s+been|was|were)\s+(created|added)\b",
        # "marked as complete", "marked accepted"
        r"\bmarked\s+(as\s+)?(complete|completed|done|closed|accepted|resolved)\b",
        # "automatically applied", "automatically accepted"
        r"\bautomatically\s+(applied|accepted|created|updated|closed|approved)\b",
    )
)


class RiskTreatmentSuggestionValidationError(Exception):
    def __init__(self, error_code: str, detail: str, errors: list[str] | dict[str, Any]):
        super().__init__(detail)
        self.status_code = 422
        self.error_code = error_code
        self.detail = detail
        self.errors = errors

    def to_response(self) -> dict[str, Any]:
        return {"error_code": self.error_code, "detail": self.detail, "errors": self.errors}


def _walk_keys(value: Any):
    if isinstance(value, dict):
        for key, child in value.items():
            yield key
            yield from _walk_keys(child)
    elif isinstance(value, list):
        for item in value:
            yield from _walk_keys(item)


def _free_text(result: dict[str, Any]) -> list[str]:
    texts = [str(result.get("rationale") or "")]
    for consideration in result.get("considerations") or []:
        if isinstance(consideration, str):
            texts.append(consideration)
    for action in result.get("mitigating_actions") or []:
        if isinstance(action, dict):
            texts.append(str(action.get("title") or ""))
            texts.append(str(action.get("description") or ""))
    return texts


def contains_claimed_action(text: str) -> bool:
    return any(pattern.search(text) for pattern in _CLAIM_PATTERNS)


def validate_risk_treatment_request_guardrails(payload: dict[str, Any]) -> dict[str, list[str]]:
    """Defensive check on the inbound request body, before it reaches a serializer."""
    return {
        field: ["This field is not allowed in the risk treatment suggestion."]
        for field in FORBIDDEN_KEYS
        if field in payload
    }


def validate_provider_output_guardrails(result: Any) -> None:
    """Reject model output that implies a write, claims an action, or tries to supply an
    identifier. Raised as a hard failure, never silently substituted with a fallback."""
    if not isinstance(result, dict):
        raise RiskTreatmentSuggestionValidationError(
            "ai_risk_treatment_suggestion_guardrails_failed",
            "Generated advisory risk treatment output violated safety guardrails.",
            ["Output must be a JSON object."],
        )

    errors: list[str] = [
        f"Forbidden key found in risk treatment output: {key}"
        for key in _walk_keys(result)
        if key in FORBIDDEN_KEYS
    ]

    treatment = result.get("suggested_treatment")
    if treatment is not None and treatment not in SUGGESTABLE_TREATMENT_CHOICES:
        errors.append(
            "suggested_treatment must be one of: " + ", ".join(SUGGESTABLE_TREATMENT_CHOICES)
        )

    confidence = result.get("confidence")
    if confidence is not None and (
        not isinstance(confidence, (int, float))
        or isinstance(confidence, bool)
        or not 0.0 <= float(confidence) <= 1.0
    ):
        errors.append("confidence must be a number between 0 and 1.")

    for index, action in enumerate(result.get("mitigating_actions") or []):
        priority = action.get("priority") if isinstance(action, dict) else None
        if priority is not None and priority not in ACTION_PRIORITY_CHOICES:
            errors.append(
                f"mitigating_actions[{index}].priority must be one of: "
                + ", ".join(ACTION_PRIORITY_CHOICES)
            )

    if any(contains_claimed_action(text) for text in _free_text(result)):
        errors.append(
            "Risk treatment output claims an action was taken; it may only recommend one."
        )

    if errors:
        raise RiskTreatmentSuggestionValidationError(
            "ai_risk_treatment_suggestion_guardrails_failed",
            "Generated advisory risk treatment output violated safety guardrails.",
            errors,
        )
