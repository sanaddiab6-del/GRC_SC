from __future__ import annotations

from typing import Any

from .audit_readiness_suggestion_serializers import (
    MAX_READINESS_SCORE,
    MIN_READINESS_SCORE,
    READINESS_STATUS_CHOICES,
)


# Step 10A is advisory/no-write. These keys would imply a write, a committed record, an
# automatic approval, an audit closure, or a compliance certification and are therefore
# forbidden anywhere in the request payload or the generated draft.
FORBIDDEN_KEYS = {
    "create_now",
    "auto_create",
    "auto_approve",
    "approve_automatically",
    "approve_readiness",
    "approved",
    "approved_by_user",
    "approved_fields",
    "create_records",
    "create_report",
    "create_requirement_assessment",
    "update_requirement_assessment",
    "requirement_assessment_updates",
    "mark_ready",
    "mark_assessment_ready",
    "set_assessment_status",
    "assessment_status",
    "commit",
    "committed",
    "dry_run",
    "idempotency_key",
    "requirement_assessment_id",
    "compliance_assessment_id",
    "risk_assessment_id",
    "framework_id",
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
    "regulator approved",
    "risk acceptance",
    "accept the risk",
)

REQUIRED_DRAFT_FIELDS = (
    "readiness_status",
    "readiness_score",
    "summary",
    "ready_items",
    "missing_evidence",
    "open_findings",
    "open_risks",
    "blocked_controls",
    "recommended_next_steps",
    "priority_actions",
    "review_status",
)

REQUIRED_LIST_FIELDS = (
    "ready_items",
    "missing_evidence",
    "open_findings",
    "open_risks",
    "blocked_controls",
    "recommended_next_steps",
    "priority_actions",
)

REQUIRED_REVIEW_STATUS = "pending_review"


class AuditReadinessSuggestionDraftValidationError(Exception):
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


def validate_audit_readiness_suggestion_request_guardrails(
    payload: dict[str, Any],
) -> dict[str, list[str]]:
    errors: dict[str, list[str]] = {}
    for field in FORBIDDEN_KEYS:
        if field in payload:
            errors[field] = ["This field is not allowed in Step 10A."]
    return errors


def _walk_keys(value: Any):
    if isinstance(value, dict):
        for key, child in value.items():
            yield key
            yield from _walk_keys(child)
    elif isinstance(value, list):
        for item in value:
            yield from _walk_keys(item)


def validate_audit_readiness_suggestion_guardrails(draft: dict[str, Any]) -> None:
    errors: list[str] = []

    for forbidden_key in FORBIDDEN_KEYS:
        if forbidden_key in draft:
            errors.append(f"Forbidden top-level key in Step 10A draft: {forbidden_key}")

    for key in _walk_keys(draft):
        if key in FORBIDDEN_KEYS:
            errors.append(f"Forbidden key found in Step 10A draft: {key}")

    overall_confidence = draft.get("overall_confidence")
    if not isinstance(overall_confidence, (int, float)) or isinstance(overall_confidence, bool):
        errors.append("overall_confidence must be a number between 0 and 1.")
    elif not 0.0 <= float(overall_confidence) <= 1.0:
        errors.append("overall_confidence must be between 0 and 1.")

    for field in REQUIRED_DRAFT_FIELDS:
        if field not in draft or draft.get(field) is None:
            errors.append(f"{field} is required in Step 10A.")

    readiness_status = draft.get("readiness_status")
    if readiness_status is not None and readiness_status not in READINESS_STATUS_CHOICES:
        errors.append(
            f"readiness_status must be one of {', '.join(READINESS_STATUS_CHOICES)}."
        )

    readiness_score = draft.get("readiness_score")
    if readiness_score is not None:
        if not isinstance(readiness_score, int) or isinstance(readiness_score, bool):
            errors.append(
                f"readiness_score must be an integer between {MIN_READINESS_SCORE} and "
                f"{MAX_READINESS_SCORE}."
            )
        elif not MIN_READINESS_SCORE <= readiness_score <= MAX_READINESS_SCORE:
            errors.append(
                f"readiness_score must be between {MIN_READINESS_SCORE} and "
                f"{MAX_READINESS_SCORE}."
            )

    summary = draft.get("summary")
    if summary is not None and not isinstance(summary, str):
        errors.append("summary must be a string.")

    for field in REQUIRED_LIST_FIELDS:
        value = draft.get(field)
        if value is None:
            continue
        if not isinstance(value, list):
            errors.append(f"{field} must be a list.")
            continue
        if any(not isinstance(entry, str) or not entry.strip() for entry in value):
            errors.append(f"{field} must only contain non-empty strings.")

    review_status = draft.get("review_status")
    if review_status is not None and review_status != REQUIRED_REVIEW_STATUS:
        errors.append(
            f"review_status must be '{REQUIRED_REVIEW_STATUS}' in Step 10A."
        )

    combined = " ".join(
        [str(draft.get("summary") or "")]
        + [
            str(entry)
            for field in REQUIRED_LIST_FIELDS
            for entry in (draft.get(field) or [])
            if isinstance(entry, str)
        ]
    ).lower()
    if any(token in combined for token in OUT_OF_SCOPE_TOKENS):
        errors.append(
            "The Step 10A readiness summary contains out-of-scope final audit opinion, "
            "certification, or closure language."
        )

    if errors:
        raise AuditReadinessSuggestionDraftValidationError(
            "ai_audit_readiness_suggestion_guardrails_failed",
            "Generated advisory audit readiness draft violated Step 10A guardrails.",
            errors,
        )
