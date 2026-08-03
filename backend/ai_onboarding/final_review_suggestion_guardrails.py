from __future__ import annotations

from typing import Any

from .final_review_suggestion_serializers import DEMO_READINESS_STATUS_CHOICES


# Step 12A is advisory/no-write. These keys would imply a write, a committed record, an
# automatic approval, a workflow completion, an audit closure, or a compliance
# certification and are therefore forbidden anywhere in the request payload or the
# generated draft.
FORBIDDEN_KEYS = {
    "create_now",
    "auto_create",
    "auto_approve",
    "approve_automatically",
    "approve_handoff",
    "approved",
    "approved_by_user",
    "approved_fields",
    "create_records",
    "create_report",
    "mark_complete",
    "mark_workflow_complete",
    "mark_ready",
    "complete_workflow",
    "set_assessment_status",
    "assessment_status",
    "commit",
    "committed",
    "dry_run",
    "idempotency_key",
    "compliance_assessment_id",
    "requirement_assessment_id",
    "risk_assessment_id",
    "risk_scenario_id",
    "applied_control_id",
    "finding_id",
    "evidence_id",
    "asset_id",
    "report_id",
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
    "the audit is complete",
    "the assessment is complete",
)

REQUIRED_DRAFT_FIELDS = (
    "completion_summary",
    "completed_steps",
    "incomplete_steps",
    "created_or_reused_records_summary",
    "blocked_items",
    "human_review_required",
    "recommended_next_steps",
    "demo_readiness_status",
    "review_status",
)

REQUIRED_LIST_FIELDS = (
    "completed_steps",
    "incomplete_steps",
    "created_or_reused_records_summary",
    "blocked_items",
    "human_review_required",
    "recommended_next_steps",
)

REQUIRED_REVIEW_STATUS = "pending_review"


class FinalReviewSuggestionDraftValidationError(Exception):
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


def validate_final_review_suggestion_request_guardrails(
    payload: dict[str, Any],
) -> dict[str, list[str]]:
    errors: dict[str, list[str]] = {}
    for field in FORBIDDEN_KEYS:
        if field in payload:
            errors[field] = ["This field is not allowed in Step 12A."]
    return errors


def _walk_keys(value: Any):
    if isinstance(value, dict):
        for key, child in value.items():
            yield key
            yield from _walk_keys(child)
    elif isinstance(value, list):
        for item in value:
            yield from _walk_keys(item)


def validate_final_review_suggestion_guardrails(draft: dict[str, Any]) -> None:
    errors: list[str] = []

    for forbidden_key in FORBIDDEN_KEYS:
        if forbidden_key in draft:
            errors.append(f"Forbidden top-level key in Step 12A draft: {forbidden_key}")

    for key in _walk_keys(draft):
        if key in FORBIDDEN_KEYS:
            errors.append(f"Forbidden key found in Step 12A draft: {key}")

    overall_confidence = draft.get("overall_confidence")
    if not isinstance(overall_confidence, (int, float)) or isinstance(overall_confidence, bool):
        errors.append("overall_confidence must be a number between 0 and 1.")
    elif not 0.0 <= float(overall_confidence) <= 1.0:
        errors.append("overall_confidence must be between 0 and 1.")

    for field in REQUIRED_DRAFT_FIELDS:
        if field not in draft or draft.get(field) is None:
            errors.append(f"{field} is required in Step 12A.")

    demo_readiness_status = draft.get("demo_readiness_status")
    if (
        demo_readiness_status is not None
        and demo_readiness_status not in DEMO_READINESS_STATUS_CHOICES
    ):
        errors.append(
            "demo_readiness_status must be one of "
            f"{', '.join(DEMO_READINESS_STATUS_CHOICES)}."
        )

    completion_summary = draft.get("completion_summary")
    if completion_summary is not None and not isinstance(completion_summary, str):
        errors.append("completion_summary must be a string.")

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
        errors.append(f"review_status must be '{REQUIRED_REVIEW_STATUS}' in Step 12A.")

    combined = " ".join(
        [str(draft.get("completion_summary") or "")]
        + [
            str(entry)
            for field in REQUIRED_LIST_FIELDS
            for entry in (draft.get(field) or [])
            if isinstance(entry, str)
        ]
    ).lower()
    if any(token in combined for token in OUT_OF_SCOPE_TOKENS):
        errors.append(
            "The Step 12A final review summary contains out-of-scope completion, final "
            "audit opinion, certification, or closure language."
        )

    if errors:
        raise FinalReviewSuggestionDraftValidationError(
            "ai_final_review_suggestion_guardrails_failed",
            "Generated advisory final review draft violated Step 12A guardrails.",
            errors,
        )
