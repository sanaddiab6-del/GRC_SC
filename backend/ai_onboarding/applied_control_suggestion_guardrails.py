from __future__ import annotations

from typing import Any

from .applied_control_suggestion_serializers import SAFE_NEXT_ACTIONS


FINAL_DECISION_VALUES = {
    "compliant",
    "non_compliant",
    "partially_compliant",
    "not_applicable",
    "approved",
    "accepted",
    "closed",
    "done",
    "final",
}

FINAL_STATUS_VALUES = {"done", "closed", "final", "approved"}

PROHIBITED_TOP_LEVEL_FIELDS = {
    "approved_by_user",
    "idempotency_key",
    "create_records",
    "controls_to_create",
    "applied_control_commit",
    "vulnerabilities",
    "vulnerability_drafts",
    "risk_scenarios",
    "risk_scenario_drafts",
    "evidence",
    "evidence_drafts",
    "findings",
    "remediation",
    "risk_acceptance",
    "compliance_result",
    "final_result",
    "audit_closure",
    "requirement_assessment_updates",
    "result",
}

OUT_OF_SCOPE_TOKENS = (
    "risk acceptance",
    "final result",
    "final decision",
    "close audit",
    "audit closure",
)


class AppliedControlSuggestionDraftValidationError(Exception):
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


def validate_applied_control_suggestion_request_guardrails(payload: dict[str, Any]) -> dict[str, list[str]]:
    errors: dict[str, list[str]] = {}

    for field in PROHIBITED_TOP_LEVEL_FIELDS:
        if field in payload:
            errors[field] = ["This field is not allowed in Step 4A."]

    for field_name in ("status", "result"):
        if field_name in payload:
            errors[field_name] = ["This field is not allowed in Step 4A."]

    return errors


def validate_applied_control_suggestion_guardrails(
    draft: dict[str, Any],
    request_data: dict[str, Any],
    *,
    allowed_asset_ids: set[str],
    enforce_shape: bool = True,
) -> None:
    errors: list[str] = []

    if enforce_shape and not draft.get("needs_human_review"):
        errors.append("needs_human_review must be true for Step 4A.")

    provider_mode = draft.get("provider_mode")
    source_summary = draft.get("source_summary", {})
    if provider_mode and source_summary.get("provider_mode") != provider_mode:
        errors.append("source_summary.provider_mode must match provider_mode")

    if enforce_shape and request_data.get("strict_mode") and draft.get("overall_confidence", 0.0) < 0.75:
        if not draft.get("blocking_questions"):
            errors.append("blocking_questions are required for low-confidence strict-mode drafts")

    for index, candidate in enumerate(draft.get("candidate_applied_controls", [])):
        allowed_next_actions = candidate.get("allowed_next_actions") or []
        for action in allowed_next_actions:
            if action not in SAFE_NEXT_ACTIONS:
                errors.append(
                    f"candidate_applied_controls[{index}].allowed_next_actions contains unsupported action '{action}'"
                )

        if any(
            action in {"create_now", "auto_create", "approve_automatically", "update_requirement_result", "close_audit", "accept_risk"}
            for action in allowed_next_actions
        ):
            errors.append(
                f"candidate_applied_controls[{index}].allowed_next_actions must not contain direct write or final-decision actions"
            )

        if enforce_shape and any(
            key in candidate for key in ("id", "applied_control_id", "created_applied_control_id")
        ):
            errors.append(
                f"candidate_applied_controls[{index}] must not expose created or primary applied-control ids in Step 4A"
            )

        linked_asset_ids = {str(asset_id) for asset_id in candidate.get("linked_asset_ids") or []}
        if not linked_asset_ids:
            errors.append(
                f"candidate_applied_controls[{index}].linked_asset_ids must not be empty in Step 4A when approved asset references were supplied"
            )
        if linked_asset_ids - allowed_asset_ids:
            errors.append(
                f"candidate_applied_controls[{index}].linked_asset_ids contains assets outside the approved asset reference set"
            )

        combined = " ".join(
            [
                str(candidate.get("proposed_name") or ""),
                str(candidate.get("proposed_description") or ""),
                str(candidate.get("rationale") or ""),
            ]
        ).lower()
        if any(token in combined for token in OUT_OF_SCOPE_TOKENS):
            errors.append(
                f"candidate_applied_controls[{index}] contains out-of-scope final-decision language"
            )

    for index, duplicate in enumerate(draft.get("duplicate_candidates", [])):
        matches = duplicate.get("matches") or []
        if not matches:
            errors.append(f"duplicate_candidates[{index}].matches must not be empty")

    for index, ambiguous in enumerate(draft.get("ambiguous_candidates", [])):
        recommended_actions = ambiguous.get("recommended_actions") or []
        for action in recommended_actions:
            if action not in SAFE_NEXT_ACTIONS:
                errors.append(
                    f"ambiguous_candidates[{index}].recommended_actions contains unsupported action '{action}'"
                )

    if errors:
        raise AppliedControlSuggestionDraftValidationError(
            "ai_applied_control_suggestion_guardrails_failed",
            "Generated advisory applied-control suggestion draft violated Step 4A guardrails.",
            errors,
        )