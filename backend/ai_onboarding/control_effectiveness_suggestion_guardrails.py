from __future__ import annotations

import re
from typing import Any

from .control_effectiveness_suggestion_serializers import (
    COMPLIANCE_STATUS_CHOICES,
    EFFECTIVENESS_CHOICES,
)


# Step 9A is advisory/no-write. These keys would imply a write, a committed record, an
# automatic approval, an audit closure, or a compliance certification and are therefore
# forbidden anywhere in the request payload or the generated draft.
FORBIDDEN_KEYS = {
    "create_now",
    "auto_create",
    "auto_approve",
    "approve_automatically",
    "approve_result",
    "approved",
    "approved_by_user",
    "approved_fields",
    "create_records",
    "create_framework",
    "create_requirement",
    "create_control",
    "create_reference_control",
    "create_framework_control",
    "create_requirement_assessment",
    "update_requirement_assessment",
    "requirement_assessment_updates",
    "commit",
    "committed",
    "dry_run",
    "idempotency_key",
    "requirement_assessment_id",
    "compliance_assessment_id",
    "framework_id",
    "framework_control_id",
    "requirement_id",
    "requirement_node_id",
    "reference_control_id",
    "applied_control_id",
    "finding_id",
    "evidence_id",
    "asset_id",
    "risk_scenario_id",
    "compliance_result",
    "final_result",
    "final_compliance_result",
    "final_audit_opinion",
    "audit_opinion",
    "final_risk_decision",
    "risk_acceptance",
    "risk_decision",
    "audit_closure",
    "close_audit",
    "accept_risk",
    "certify_compliance",
    "certification",
}

OUT_OF_SCOPE_TOKENS = (
    "final audit opinion",
    "final result",
    "final decision",
    "close audit",
    "audit closure",
    "we certify",
    "certify compliance",
    "certified compliant",
    "risk acceptance",
    "accept the risk",
    "regulator approved",
)

REQUIRED_SUGGESTION_FIELDS = (
    "temporary_id",
    "framework_control_reference",
    "framework_control_title",
    "suggested_effectiveness",
    "suggested_compliance_status",
    "gaps",
    "rationale",
    "confidence",
    "review_status",
)

REQUIRED_SUGGESTION_TEXT_FIELDS = (
    "temporary_id",
    "framework_control_reference",
    "framework_control_title",
    "rationale",
)

REQUIRED_SUGGESTION_LIST_FIELDS = ("gaps",)

ENUM_FIELDS = (
    ("suggested_effectiveness", EFFECTIVENESS_CHOICES),
    ("suggested_compliance_status", COMPLIANCE_STATUS_CHOICES),
)

REQUIRED_REVIEW_STATUS = "pending_review"

_WHITESPACE_RE = re.compile(r"\s+")


class ControlEffectivenessSuggestionDraftValidationError(Exception):
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


def normalize_control_key(value: Any) -> str:
    """Case/whitespace-insensitive key used to match a suggestion to a known control."""
    if not isinstance(value, str):
        return ""
    return _WHITESPACE_RE.sub(" ", value).strip().lower()


def build_known_control_registry(request_data: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Map every safe identifier of a supplied existing control to that control.

    The registry is the closed set Step 9A is allowed to judge. Anything outside it is
    treated as an invented framework control and rejected.
    """
    registry: dict[str, dict[str, Any]] = {}

    for mapping in request_data.get("framework_mappings") or []:
        if not isinstance(mapping, dict):
            continue
        entry = {
            "reference": mapping.get("reference"),
            "code": mapping.get("code"),
            "title": mapping.get("title"),
            "requirement_assessment_reference": mapping.get("requirement_assessment_reference"),
        }
        for field in ("reference", "code", "title"):
            key = normalize_control_key(mapping.get(field))
            if key and key not in registry:
                registry[key] = entry

    for assessment in request_data.get("requirement_assessments") or []:
        if not isinstance(assessment, dict):
            continue
        entry = {
            "reference": assessment.get("framework_control_reference"),
            "code": assessment.get("framework_control_code"),
            "title": assessment.get("framework_control_title"),
            "requirement_assessment_reference": assessment.get("reference"),
        }
        for field in (
            "framework_control_reference",
            "framework_control_code",
            "framework_control_title",
        ):
            key = normalize_control_key(assessment.get(field))
            if key and key not in registry:
                registry[key] = entry

    return registry


def resolve_known_control(
    suggestion: dict[str, Any], registry: dict[str, dict[str, Any]]
) -> dict[str, Any] | None:
    for field in (
        "framework_control_reference",
        "framework_control_code",
        "framework_control_title",
    ):
        candidate = registry.get(normalize_control_key(suggestion.get(field)))
        if candidate is not None:
            return candidate
    return None


def validate_control_effectiveness_suggestion_request_guardrails(
    payload: dict[str, Any],
) -> dict[str, list[str]]:
    errors: dict[str, list[str]] = {}
    for field in FORBIDDEN_KEYS:
        if field in payload:
            errors[field] = ["This field is not allowed in Step 9A."]
    return errors


def _walk_keys(value: Any):
    if isinstance(value, dict):
        for key, child in value.items():
            yield key
            yield from _walk_keys(child)
    elif isinstance(value, list):
        for item in value:
            yield from _walk_keys(item)


def validate_control_effectiveness_suggestion_guardrails(
    draft: dict[str, Any],
    known_control_registry: dict[str, dict[str, Any]] | None = None,
) -> None:
    registry = known_control_registry or {}
    errors: list[str] = []

    for forbidden_key in FORBIDDEN_KEYS:
        if forbidden_key in draft:
            errors.append(f"Forbidden top-level key in Step 9A draft: {forbidden_key}")

    for key in _walk_keys(draft):
        if key in FORBIDDEN_KEYS:
            errors.append(f"Forbidden key found in Step 9A draft: {key}")

    overall_confidence = draft.get("overall_confidence")
    if not isinstance(overall_confidence, (int, float)) or isinstance(overall_confidence, bool):
        errors.append("overall_confidence must be a number between 0 and 1.")
    elif not 0.0 <= float(overall_confidence) <= 1.0:
        errors.append("overall_confidence must be between 0 and 1.")

    suggestions = draft.get("control_effectiveness_suggestions")
    if not isinstance(suggestions, list):
        errors.append("control_effectiveness_suggestions must be a list.")
        raise ControlEffectivenessSuggestionDraftValidationError(
            "ai_control_effectiveness_suggestion_guardrails_failed",
            "Generated advisory control effectiveness draft violated Step 9A guardrails.",
            errors,
        )

    for index, suggestion in enumerate(suggestions):
        if not isinstance(suggestion, dict):
            errors.append(f"control_effectiveness_suggestions[{index}] must be an object.")
            continue

        for field in REQUIRED_SUGGESTION_FIELDS:
            if field not in suggestion or suggestion.get(field) is None:
                errors.append(
                    f"control_effectiveness_suggestions[{index}].{field} is required in Step 9A."
                )

        for field in REQUIRED_SUGGESTION_TEXT_FIELDS:
            value = suggestion.get(field)
            if value is None:
                continue
            if not isinstance(value, str) or not value.strip():
                errors.append(
                    f"control_effectiveness_suggestions[{index}].{field} must be a "
                    "non-empty string."
                )

        for field in REQUIRED_SUGGESTION_LIST_FIELDS:
            value = suggestion.get(field)
            if value is None:
                continue
            if not isinstance(value, list):
                errors.append(
                    f"control_effectiveness_suggestions[{index}].{field} must be a list."
                )
                continue
            if any(not isinstance(entry, str) or not entry.strip() for entry in value):
                errors.append(
                    f"control_effectiveness_suggestions[{index}].{field} must only contain "
                    "non-empty strings."
                )

        for field, choices in ENUM_FIELDS:
            value = suggestion.get(field)
            if value is not None and value not in choices:
                errors.append(
                    f"control_effectiveness_suggestions[{index}].{field} must be one of "
                    f"{', '.join(choices)}."
                )

        confidence = suggestion.get("confidence")
        if confidence is not None:
            if not isinstance(confidence, (int, float)) or isinstance(confidence, bool):
                errors.append(
                    f"control_effectiveness_suggestions[{index}].confidence must be a number "
                    "between 0 and 1."
                )
            elif not 0.0 <= float(confidence) <= 1.0:
                errors.append(
                    f"control_effectiveness_suggestions[{index}].confidence must be between "
                    "0 and 1."
                )

        review_status = suggestion.get("review_status")
        if review_status is not None and review_status != REQUIRED_REVIEW_STATUS:
            errors.append(
                f"control_effectiveness_suggestions[{index}].review_status must be "
                f"'{REQUIRED_REVIEW_STATUS}' in Step 9A."
            )

        errors.extend(_validate_known_control_restriction(index, suggestion, registry))

        combined = " ".join(
            str(suggestion.get(field) or "")
            for field in (
                "evidence_summary",
                "recommended_auditor_action",
                "rationale",
                "framework_control_title",
            )
        ).lower()
        if any(token in combined for token in OUT_OF_SCOPE_TOKENS):
            errors.append(
                f"control_effectiveness_suggestions[{index}] contains out-of-scope final "
                "audit opinion, certification, or closure language."
            )

    if errors:
        raise ControlEffectivenessSuggestionDraftValidationError(
            "ai_control_effectiveness_suggestion_guardrails_failed",
            "Generated advisory control effectiveness draft violated Step 9A guardrails.",
            errors,
        )


def _validate_known_control_restriction(
    index: int, suggestion: dict[str, Any], registry: dict[str, dict[str, Any]]
) -> list[str]:
    """Step 9A may only judge framework controls that were supplied as context."""
    errors: list[str] = []

    reference = suggestion.get("framework_control_reference")
    if not isinstance(reference, str) or not reference.strip():
        # Already reported as a missing required field.
        return errors

    if resolve_known_control(suggestion, registry) is None:
        errors.append(
            f"control_effectiveness_suggestions[{index}].framework_control_reference "
            f"'{reference.strip()}' is not a supplied framework control. Step 9A may only "
            "judge framework controls carried over from the reviewed onboarding context."
        )

    return errors
