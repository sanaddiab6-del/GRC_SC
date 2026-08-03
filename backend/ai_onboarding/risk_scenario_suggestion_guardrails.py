from __future__ import annotations

from typing import Any

from .risk_scenario_suggestion_serializers import (
    IMPACT_CHOICES,
    LIKELIHOOD_CHOICES,
    RISK_LEVEL_CHOICES,
)


# Step 8A is advisory/no-write. These keys would imply a write, a committed record, an
# automatic approval, a risk treatment decision, or a final risk decision and are therefore
# forbidden anywhere in the request payload or the generated draft.
FORBIDDEN_KEYS = {
    "create_now",
    "auto_create",
    "auto_approve",
    "approve_automatically",
    "approve_scenario",
    "approved",
    "approved_by_user",
    "approved_fields",
    "create_records",
    "create_risk",
    "create_risk_scenario",
    "create_risk_assessment",
    "create_risk_acceptance",
    "commit",
    "committed",
    "dry_run",
    "idempotency_key",
    "risk_id",
    "risk_scenario_id",
    "risk_assessment_id",
    "risk_matrix_id",
    "risk_acceptance_id",
    "compliance_assessment_id",
    "requirement_assessment_id",
    "finding_id",
    "evidence_id",
    "applied_control_id",
    "asset_id",
    "treatment",
    "risk_treatment",
    "treatment_decision",
    "risk_closure",
    "close_risk",
    "compliance_result",
    "final_result",
    "final_compliance_result",
    "final_risk_decision",
    "risk_acceptance",
    "risk_decision",
    "audit_closure",
    "close_audit",
    "accept_risk",
    "certify_compliance",
}

OUT_OF_SCOPE_TOKENS = (
    "risk acceptance",
    "accept the risk",
    "risk is accepted",
    "final result",
    "final decision",
    "close audit",
    "audit closure",
    "close this risk",
    "risk is closed",
    "certify compliance",
    "treatment decision",
)

REQUIRED_SCENARIO_FIELDS = (
    "temporary_id",
    "title",
    "description",
    "threat",
    "vulnerability",
    "impact_description",
    "likelihood",
    "impact",
    "risk_level",
    "rationale",
    "recommended_next_steps",
    "confidence",
    "review_status",
)

REQUIRED_SCENARIO_TEXT_FIELDS = (
    "temporary_id",
    "title",
    "description",
    "rationale",
)

REQUIRED_SCENARIO_LIST_FIELDS = ("recommended_next_steps",)

ENUM_FIELDS = (
    ("likelihood", LIKELIHOOD_CHOICES),
    ("impact", IMPACT_CHOICES),
    ("risk_level", RISK_LEVEL_CHOICES),
)

REQUIRED_REVIEW_STATUS = "pending_review"


class RiskScenarioSuggestionDraftValidationError(Exception):
    def __init__(self, error_code: str, detail: str, errors: list[str] | dict[str, Any]):
        super().__init__(detail)
        self.status_code = 422
        self.error_code = error_code
        self.detail = detail
        self.errors = errors

    def to_response(self) -> dict[str, Any]:
        return {
            "error_code": self.error_code,
            "detail": self.detail,
            "errors": self.errors,
        }


def validate_risk_scenario_suggestion_request_guardrails(
    payload: dict[str, Any],
) -> dict[str, list[str]]:
    errors: dict[str, list[str]] = {}
    for field in FORBIDDEN_KEYS:
        if field in payload:
            errors[field] = ["This field is not allowed in Step 8A."]
    return errors


def _walk_keys(value: Any):
    if isinstance(value, dict):
        for key, child in value.items():
            yield key
            yield from _walk_keys(child)
    elif isinstance(value, list):
        for item in value:
            yield from _walk_keys(item)


def validate_risk_scenario_suggestion_guardrails(draft: dict[str, Any]) -> None:
    errors: list[str] = []

    for forbidden_key in FORBIDDEN_KEYS:
        if forbidden_key in draft:
            errors.append(f"Forbidden top-level key in Step 8A draft: {forbidden_key}")

    for key in _walk_keys(draft):
        if key in FORBIDDEN_KEYS:
            errors.append(f"Forbidden key found in Step 8A draft: {key}")

    overall_confidence = draft.get("overall_confidence")
    if not isinstance(overall_confidence, (int, float)) or isinstance(overall_confidence, bool):
        errors.append("overall_confidence must be a number between 0 and 1.")
    elif not 0.0 <= float(overall_confidence) <= 1.0:
        errors.append("overall_confidence must be between 0 and 1.")

    risk_scenarios = draft.get("risk_scenarios")
    if not isinstance(risk_scenarios, list):
        errors.append("risk_scenarios must be a list.")
        raise RiskScenarioSuggestionDraftValidationError(
            "ai_risk_scenario_suggestion_guardrails_failed",
            "Generated advisory risk scenario draft violated Step 8A guardrails.",
            errors,
        )

    for index, scenario in enumerate(risk_scenarios):
        if not isinstance(scenario, dict):
            errors.append(f"risk_scenarios[{index}] must be an object.")
            continue

        for field in REQUIRED_SCENARIO_FIELDS:
            if field not in scenario or scenario.get(field) is None:
                errors.append(f"risk_scenarios[{index}].{field} is required in Step 8A.")

        for field in REQUIRED_SCENARIO_TEXT_FIELDS:
            value = scenario.get(field)
            if value is None:
                continue
            if not isinstance(value, str) or not value.strip():
                errors.append(f"risk_scenarios[{index}].{field} must be a non-empty string.")

        for field in REQUIRED_SCENARIO_LIST_FIELDS:
            value = scenario.get(field)
            if value is None:
                continue
            if not isinstance(value, list):
                errors.append(f"risk_scenarios[{index}].{field} must be a list.")
                continue
            if any(not isinstance(entry, str) or not entry.strip() for entry in value):
                errors.append(
                    f"risk_scenarios[{index}].{field} must only contain non-empty strings."
                )

        for field, choices in ENUM_FIELDS:
            value = scenario.get(field)
            if value is not None and value not in choices:
                errors.append(
                    f"risk_scenarios[{index}].{field} must be one of {', '.join(choices)}."
                )

        confidence = scenario.get("confidence")
        if confidence is not None:
            if not isinstance(confidence, (int, float)) or isinstance(confidence, bool):
                errors.append(
                    f"risk_scenarios[{index}].confidence must be a number between 0 and 1."
                )
            elif not 0.0 <= float(confidence) <= 1.0:
                errors.append(f"risk_scenarios[{index}].confidence must be between 0 and 1.")

        review_status = scenario.get("review_status")
        if review_status is not None and review_status != REQUIRED_REVIEW_STATUS:
            errors.append(
                f"risk_scenarios[{index}].review_status must be "
                f"'{REQUIRED_REVIEW_STATUS}' in Step 8A."
            )

        combined = " ".join(
            str(scenario.get(field) or "")
            for field in ("title", "description", "rationale", "impact_description")
        ).lower()
        if any(token in combined for token in OUT_OF_SCOPE_TOKENS):
            errors.append(
                f"risk_scenarios[{index}] contains out-of-scope final-decision or "
                "risk-treatment language."
            )

    if errors:
        raise RiskScenarioSuggestionDraftValidationError(
            "ai_risk_scenario_suggestion_guardrails_failed",
            "Generated advisory risk scenario draft violated Step 8A guardrails.",
            errors,
        )
