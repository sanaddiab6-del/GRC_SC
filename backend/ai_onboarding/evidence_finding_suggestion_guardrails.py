from __future__ import annotations

from typing import Any


# Step 5A is advisory/no-write. These keys would imply a write, a final decision,
# or a committed record and are therefore forbidden anywhere in the request or draft.
FORBIDDEN_KEYS = {
    "create_now",
    "auto_create",
    "approve_automatically",
    "create_records",
    "commit",
    "committed",
    "approved_by_user",
    "idempotency_key",
    "finding_id",
    "evidence_id",
    "task_id",
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


class EvidenceFindingSuggestionDraftValidationError(Exception):
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


def validate_evidence_finding_suggestion_request_guardrails(
    payload: dict[str, Any],
) -> dict[str, list[str]]:
    errors: dict[str, list[str]] = {}
    for field in FORBIDDEN_KEYS:
        if field in payload:
            errors[field] = ["This field is not allowed in Step 5A."]
    return errors


def _walk_keys(value: Any):
    if isinstance(value, dict):
        for key, child in value.items():
            yield key
            yield from _walk_keys(child)
    elif isinstance(value, list):
        for item in value:
            yield from _walk_keys(item)


def validate_evidence_finding_suggestion_guardrails(
    draft: dict[str, Any],
    *,
    allowed_asset_ids: set[str],
    allowed_applied_control_ids: set[str],
    enforce_shape: bool = True,
) -> None:
    errors: list[str] = []

    if enforce_shape and draft.get("no_write") is not True:
        errors.append("no_write must be true for Step 5A.")

    if enforce_shape and not draft.get("needs_human_review"):
        errors.append("needs_human_review must be true for Step 5A.")

    if enforce_shape and draft.get("review_status") != "pending_review":
        errors.append("review_status must be 'pending_review' for Step 5A.")

    provider_mode = draft.get("provider_mode")
    source_summary = draft.get("source_summary", {})
    if provider_mode and source_summary.get("provider_mode") != provider_mode:
        errors.append("source_summary.provider_mode must match provider_mode")

    for forbidden_key in FORBIDDEN_KEYS:
        if forbidden_key in draft:
            errors.append(f"Forbidden top-level key in Step 5A draft: {forbidden_key}")

    for key in _walk_keys(draft):
        if key in FORBIDDEN_KEYS:
            errors.append(f"Forbidden key found in Step 5A draft: {key}")

    suggestion_groups = (
        ("evidence_requests", draft.get("evidence_requests", [])),
        ("audit_questions", draft.get("audit_questions", [])),
        ("preliminary_findings", draft.get("preliminary_findings", [])),
    )
    for group_name, items in suggestion_groups:
        for index, item in enumerate(items):
            if not isinstance(item, dict):
                continue

            if item.get("review_status") != "pending_review":
                errors.append(
                    f"{group_name}[{index}].review_status must be 'pending_review' in Step 5A"
                )

            for key in ("id", "finding_id", "evidence_id", "task_id"):
                if key in item:
                    errors.append(
                        f"{group_name}[{index}] must not expose committed record ids in Step 5A"
                    )

            linked_asset_ids = {str(asset_id) for asset_id in item.get("linked_asset_ids") or []}
            if linked_asset_ids - allowed_asset_ids:
                errors.append(
                    f"{group_name}[{index}].linked_asset_ids references an asset outside the approved asset set"
                )

            linked_control_ids = {
                str(control_id) for control_id in item.get("linked_applied_control_ids") or []
            }
            if linked_control_ids - allowed_applied_control_ids:
                errors.append(
                    f"{group_name}[{index}].linked_applied_control_ids references a control outside the approved control set"
                )

            combined = " ".join(
                str(item.get(field) or "")
                for field in ("title", "question_text", "summary", "description", "rationale")
            ).lower()
            if any(token in combined for token in OUT_OF_SCOPE_TOKENS):
                errors.append(
                    f"{group_name}[{index}] contains out-of-scope final-decision language"
                )

    if errors:
        raise EvidenceFindingSuggestionDraftValidationError(
            "ai_evidence_finding_suggestion_guardrails_failed",
            "Generated advisory evidence/finding suggestion draft violated Step 5A guardrails.",
            errors,
        )
