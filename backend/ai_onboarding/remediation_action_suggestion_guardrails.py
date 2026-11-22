from __future__ import annotations

from typing import Any

from .remediation_action_suggestion_serializers import PRIORITY_CHOICES


# Step 6A is advisory/no-write. These keys would imply a write, a committed record,
# an automatic approval, or a final decision and are therefore forbidden anywhere in
# the request payload or the generated draft.
FORBIDDEN_KEYS = {
    "create_now",
    "auto_create",
    "auto_approve",
    "approve_automatically",
    "approved",
    "approved_by_user",
    "approved_fields",
    "create_records",
    "commit",
    "committed",
    "dry_run",
    "idempotency_key",
    "remediation_id",
    "remediation_action_id",
    "action_id",
    "task_id",
    "finding_id",
    "evidence_id",
    "applied_control_id",
    "asset_id",
    "requirement_assessment_id",
    "requirement_assessment_updates",
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
)

REQUIRED_ACTION_FIELDS = (
    "temporary_id",
    "title",
    "description",
    "priority",
    "suggested_owner",
    "target_timeline",
    "success_criteria",
    "required_follow_up_evidence",
    "rationale",
    "confidence",
    "review_status",
)

REQUIRED_ACTION_LIST_FIELDS = (
    "success_criteria",
    "required_follow_up_evidence",
)

REQUIRED_ACTION_TEXT_FIELDS = (
    "temporary_id",
    "title",
    "description",
    "suggested_owner",
    "target_timeline",
    "rationale",
)

REQUIRED_REVIEW_STATUS = "pending_review"


class RemediationActionSuggestionDraftValidationError(Exception):
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


def validate_remediation_action_suggestion_request_guardrails(
    payload: dict[str, Any],
) -> dict[str, list[str]]:
    errors: dict[str, list[str]] = {}
    for field in FORBIDDEN_KEYS:
        if field in payload:
            errors[field] = ["This field is not allowed in Step 6A."]
    return errors


def _walk_keys(value: Any):
    if isinstance(value, dict):
        for key, child in value.items():
            yield key
            yield from _walk_keys(child)
    elif isinstance(value, list):
        for item in value:
            yield from _walk_keys(item)


def validate_remediation_action_suggestion_guardrails(draft: dict[str, Any]) -> None:
    errors: list[str] = []

    for forbidden_key in FORBIDDEN_KEYS:
        if forbidden_key in draft:
            errors.append(f"Forbidden top-level key in Step 6A draft: {forbidden_key}")

    for key in _walk_keys(draft):
        if key in FORBIDDEN_KEYS:
            errors.append(f"Forbidden key found in Step 6A draft: {key}")

    overall_confidence = draft.get("overall_confidence")
    if not isinstance(overall_confidence, (int, float)) or isinstance(overall_confidence, bool):
        errors.append("overall_confidence must be a number between 0 and 1.")
    elif not 0.0 <= float(overall_confidence) <= 1.0:
        errors.append("overall_confidence must be between 0 and 1.")

    remediation_actions = draft.get("remediation_actions")
    if not isinstance(remediation_actions, list):
        errors.append("remediation_actions must be a list.")
        raise RemediationActionSuggestionDraftValidationError(
            "ai_remediation_action_suggestion_guardrails_failed",
            "Generated advisory remediation action draft violated Step 6A guardrails.",
            errors,
        )

    for index, action in enumerate(remediation_actions):
        if not isinstance(action, dict):
            errors.append(f"remediation_actions[{index}] must be an object.")
            continue

        for field in REQUIRED_ACTION_FIELDS:
            if field not in action or action.get(field) is None:
                errors.append(f"remediation_actions[{index}].{field} is required in Step 6A.")

        for field in REQUIRED_ACTION_TEXT_FIELDS:
            value = action.get(field)
            if value is None:
                continue
            if not isinstance(value, str) or not value.strip():
                errors.append(
                    f"remediation_actions[{index}].{field} must be a non-empty string."
                )

        for field in REQUIRED_ACTION_LIST_FIELDS:
            value = action.get(field)
            if value is None:
                continue
            if not isinstance(value, list):
                errors.append(f"remediation_actions[{index}].{field} must be a list.")
                continue
            if any(not isinstance(entry, str) or not entry.strip() for entry in value):
                errors.append(
                    f"remediation_actions[{index}].{field} must only contain non-empty strings."
                )

        priority = action.get("priority")
        if priority is not None and priority not in PRIORITY_CHOICES:
            errors.append(
                f"remediation_actions[{index}].priority must be one of "
                f"{', '.join(PRIORITY_CHOICES)}."
            )

        confidence = action.get("confidence")
        if confidence is not None:
            if not isinstance(confidence, (int, float)) or isinstance(confidence, bool):
                errors.append(
                    f"remediation_actions[{index}].confidence must be a number between 0 and 1."
                )
            elif not 0.0 <= float(confidence) <= 1.0:
                errors.append(
                    f"remediation_actions[{index}].confidence must be between 0 and 1."
                )

        review_status = action.get("review_status")
        if review_status is not None and review_status != REQUIRED_REVIEW_STATUS:
            errors.append(
                f"remediation_actions[{index}].review_status must be "
                f"'{REQUIRED_REVIEW_STATUS}' in Step 6A."
            )

        combined = " ".join(
            str(action.get(field) or "")
            for field in ("title", "description", "rationale", "target_timeline")
        ).lower()
        if any(token in combined for token in OUT_OF_SCOPE_TOKENS):
            errors.append(
                f"remediation_actions[{index}] contains out-of-scope final-decision language."
            )

    if errors:
        raise RemediationActionSuggestionDraftValidationError(
            "ai_remediation_action_suggestion_guardrails_failed",
            "Generated advisory remediation action draft violated Step 6A guardrails.",
            errors,
        )
