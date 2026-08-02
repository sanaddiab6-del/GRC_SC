from __future__ import annotations

import re
from typing import Any

from .framework_control_mapping_suggestion_serializers import MAPPING_TYPE_CHOICES


# Step 7A is advisory/no-write. These keys would imply a write, a committed record,
# an automatic approval, or a final decision and are therefore forbidden anywhere in
# the request payload or the generated draft.
FORBIDDEN_KEYS = {
    "create_now",
    "auto_create",
    "auto_approve",
    "approve_automatically",
    "approve_mapping",
    "approved",
    "approved_by_user",
    "approved_fields",
    "create_records",
    "create_control",
    "create_framework",
    "create_requirement",
    "create_mapping",
    "commit",
    "committed",
    "dry_run",
    "idempotency_key",
    "mapping_id",
    "framework_id",
    "framework_control_id",
    "requirement_id",
    "requirement_node_id",
    "reference_control_id",
    "compliance_assessment_id",
    "requirement_assessment_id",
    "requirement_assessment_updates",
    "loaded_library_id",
    "stored_library_id",
    "remediation_id",
    "remediation_action_id",
    "action_id",
    "task_id",
    "finding_id",
    "evidence_id",
    "applied_control_id",
    "asset_id",
    "compliance_result",
    "final_result",
    "final_compliance_result",
    "final_risk_decision",
    "risk_acceptance",
    "risk_decision",
    "audit_closure",
    "close_audit",
    "accept_risk",
}

OUT_OF_SCOPE_TOKENS = (
    "risk acceptance",
    "final result",
    "final decision",
    "close audit",
    "audit closure",
    "accept the risk",
    "approve mapping",
    "approve this mapping",
    "create a new framework",
    "create a new control",
    "create a new requirement",
)

REQUIRED_MAPPING_FIELDS = (
    "temporary_id",
    "framework_control_reference",
    "framework_control_title",
    "mapping_type",
    "rationale",
    "evidence_needed",
    "confidence",
    "review_status",
)

REQUIRED_MAPPING_TEXT_FIELDS = (
    "temporary_id",
    "framework_control_reference",
    "framework_control_title",
    "rationale",
)

REQUIRED_MAPPING_LIST_FIELDS = ("evidence_needed",)

REQUIRED_REVIEW_STATUS = "pending_review"

_WHITESPACE_RE = re.compile(r"\s+")


class FrameworkControlMappingSuggestionDraftValidationError(Exception):
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
    """Case/whitespace-insensitive key used to match a mapping to a candidate control."""
    if not isinstance(value, str):
        return ""
    return _WHITESPACE_RE.sub(" ", value).strip().lower()


def normalize_control_text(value: Any) -> str:
    """Comparison form for candidate-owned text (title/description)."""
    return normalize_control_key(value).rstrip(".;:, ")


def build_allowed_control_registry(candidates: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    """Map every safe identifier of an existing candidate control to that candidate.

    The registry is the closed set Step 7A is allowed to map to. Anything outside it is
    treated as an invented framework control and rejected.
    """
    registry: dict[str, dict[str, Any]] = {}
    for candidate in candidates or []:
        if not isinstance(candidate, dict):
            continue
        for field in ("reference", "code", "title"):
            key = normalize_control_key(candidate.get(field))
            if key and key not in registry:
                registry[key] = candidate
    return registry


def resolve_allowed_control(
    mapping: dict[str, Any], registry: dict[str, dict[str, Any]]
) -> dict[str, Any] | None:
    for field in ("framework_control_reference", "framework_control_code", "framework_control_title"):
        candidate = registry.get(normalize_control_key(mapping.get(field)))
        if candidate is not None:
            return candidate
    return None


def validate_framework_control_mapping_suggestion_request_guardrails(
    payload: dict[str, Any],
) -> dict[str, list[str]]:
    errors: dict[str, list[str]] = {}
    for field in FORBIDDEN_KEYS:
        if field in payload:
            errors[field] = ["This field is not allowed in Step 7A."]
    return errors


def _walk_keys(value: Any):
    if isinstance(value, dict):
        for key, child in value.items():
            yield key
            yield from _walk_keys(child)
    elif isinstance(value, list):
        for item in value:
            yield from _walk_keys(item)


def validate_framework_control_mapping_suggestion_guardrails(
    draft: dict[str, Any],
    allowed_control_registry: dict[str, dict[str, Any]] | None = None,
) -> None:
    registry = allowed_control_registry or {}
    errors: list[str] = []

    for forbidden_key in FORBIDDEN_KEYS:
        if forbidden_key in draft:
            errors.append(f"Forbidden top-level key in Step 7A draft: {forbidden_key}")

    for key in _walk_keys(draft):
        if key in FORBIDDEN_KEYS:
            errors.append(f"Forbidden key found in Step 7A draft: {key}")

    overall_confidence = draft.get("overall_confidence")
    if not isinstance(overall_confidence, (int, float)) or isinstance(overall_confidence, bool):
        errors.append("overall_confidence must be a number between 0 and 1.")
    elif not 0.0 <= float(overall_confidence) <= 1.0:
        errors.append("overall_confidence must be between 0 and 1.")

    mappings = draft.get("framework_control_mappings")
    if not isinstance(mappings, list):
        errors.append("framework_control_mappings must be a list.")
        raise FrameworkControlMappingSuggestionDraftValidationError(
            "ai_framework_control_mapping_suggestion_guardrails_failed",
            "Generated advisory framework control mapping draft violated Step 7A guardrails.",
            errors,
        )

    for index, mapping in enumerate(mappings):
        if not isinstance(mapping, dict):
            errors.append(f"framework_control_mappings[{index}] must be an object.")
            continue

        for field in REQUIRED_MAPPING_FIELDS:
            if field not in mapping or mapping.get(field) is None:
                errors.append(
                    f"framework_control_mappings[{index}].{field} is required in Step 7A."
                )

        for field in REQUIRED_MAPPING_TEXT_FIELDS:
            value = mapping.get(field)
            if value is None:
                continue
            if not isinstance(value, str) or not value.strip():
                errors.append(
                    f"framework_control_mappings[{index}].{field} must be a non-empty string."
                )

        for field in REQUIRED_MAPPING_LIST_FIELDS:
            value = mapping.get(field)
            if value is None:
                continue
            if not isinstance(value, list):
                errors.append(f"framework_control_mappings[{index}].{field} must be a list.")
                continue
            if any(not isinstance(entry, str) or not entry.strip() for entry in value):
                errors.append(
                    f"framework_control_mappings[{index}].{field} must only contain non-empty strings."
                )

        mapping_type = mapping.get("mapping_type")
        if mapping_type is not None and mapping_type not in MAPPING_TYPE_CHOICES:
            errors.append(
                f"framework_control_mappings[{index}].mapping_type must be one of "
                f"{', '.join(MAPPING_TYPE_CHOICES)}."
            )

        confidence = mapping.get("confidence")
        if confidence is not None:
            if not isinstance(confidence, (int, float)) or isinstance(confidence, bool):
                errors.append(
                    f"framework_control_mappings[{index}].confidence must be a number between 0 and 1."
                )
            elif not 0.0 <= float(confidence) <= 1.0:
                errors.append(
                    f"framework_control_mappings[{index}].confidence must be between 0 and 1."
                )

        review_status = mapping.get("review_status")
        if review_status is not None and review_status != REQUIRED_REVIEW_STATUS:
            errors.append(
                f"framework_control_mappings[{index}].review_status must be "
                f"'{REQUIRED_REVIEW_STATUS}' in Step 7A."
            )

        errors.extend(_validate_candidate_restriction(index, mapping, registry))

        combined = " ".join(
            str(mapping.get(field) or "")
            for field in ("framework_control_title", "framework_control_description", "rationale")
        ).lower()
        if any(token in combined for token in OUT_OF_SCOPE_TOKENS):
            errors.append(
                f"framework_control_mappings[{index}] contains out-of-scope final-decision language."
            )

    if errors:
        raise FrameworkControlMappingSuggestionDraftValidationError(
            "ai_framework_control_mapping_suggestion_guardrails_failed",
            "Generated advisory framework control mapping draft violated Step 7A guardrails.",
            errors,
        )


def _validate_candidate_restriction(
    index: int, mapping: dict[str, Any], registry: dict[str, dict[str, Any]]
) -> list[str]:
    """Step 7A must only map to framework controls that already exist.

    A mapping is accepted only when its reference/code/title resolves to a supplied or
    safely discovered candidate, and its title and description are the candidate's own
    text. Anything else is an invented framework control or an invented clause.
    """
    errors: list[str] = []

    reference = mapping.get("framework_control_reference")
    if not isinstance(reference, str) or not reference.strip():
        # Already reported as a missing required field.
        return errors

    candidate = resolve_allowed_control(mapping, registry)
    if candidate is None:
        errors.append(
            f"framework_control_mappings[{index}].framework_control_reference "
            f"'{reference.strip()}' is not an existing candidate framework control. "
            "Step 7A may only map to supplied or safely discovered framework controls."
        )
        return errors

    title = mapping.get("framework_control_title")
    # Export rows whose control name is blank carry a generated placeholder title. That
    # title is not official clause text, so a provider-proposed label is not treated as an
    # invention: the service backfills the candidate's own title instead.
    if (
        isinstance(title, str)
        and title.strip()
        and not candidate.get("title_is_generated")
        and normalize_control_text(title) != normalize_control_text(candidate.get("title"))
    ):
        errors.append(
            f"framework_control_mappings[{index}].framework_control_title does not match the "
            "existing framework control text. Step 7A may not invent framework clause text."
        )

    description = mapping.get("framework_control_description")
    if isinstance(description, str) and description.strip():
        provided = normalize_control_text(description)
        candidate_description = normalize_control_text(candidate.get("description") or "")
        # An exact copy or a truncated prefix/excerpt of the real clause is real clause
        # text; anything else is authored by the model and is rejected.
        if not candidate_description or provided not in candidate_description:
            errors.append(
                f"framework_control_mappings[{index}].framework_control_description does not match "
                "the existing framework control text. Step 7A may not invent framework clause text."
            )

    return errors
