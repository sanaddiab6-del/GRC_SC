from __future__ import annotations

from typing import Any

from .asset_suggestion_serializers import SAFE_NEXT_ACTIONS


AMBIGUOUS_EVIDENCE_TOKENS = (
    "record",
    "records",
    "policy",
    "policies",
    "procedure",
    "procedures",
)
AMBIGUOUS_CONTROL_TOKENS = ("mfa", "pam", "control")
AMBIGUOUS_ACCOUNT_TOKENS = ("accounts", "account")
OUT_OF_SCOPE_TOKENS = ("risk acceptance", "close audit", "final result")


class AssetSuggestionDraftValidationError(Exception):
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


def validate_asset_suggestion_guardrails(
    draft: dict[str, Any],
    request_data: dict[str, Any],
    *,
    enforce_shape: bool = True,
) -> None:
    errors: list[str] = []

    if enforce_shape and not draft.get("needs_human_review"):
        errors.append("needs_human_review must be true for Step 3A.")

    provider_mode = draft.get("provider_mode")
    source_summary = draft.get("source_summary", {})
    if provider_mode and source_summary.get("provider_mode") != provider_mode:
        errors.append("source_summary.provider_mode must match provider_mode")

    for index, candidate in enumerate(draft.get("candidate_assets", [])):
        allowed_next_actions = candidate.get("allowed_next_actions") or []
        for action in allowed_next_actions:
            if action not in SAFE_NEXT_ACTIONS:
                errors.append(
                    f"candidate_assets[{index}].allowed_next_actions contains unsupported action '{action}'"
                )

        if "create_now" in allowed_next_actions or "auto_create" in allowed_next_actions:
            errors.append(
                f"candidate_assets[{index}].allowed_next_actions must not contain direct write actions"
            )

        if enforce_shape and any(key in candidate for key in ("id", "asset_id", "created_asset_id")):
            errors.append(
                f"candidate_assets[{index}] must not expose created or primary asset ids in Step 3A"
            )

        lowered_name = str(candidate.get("proposed_name") or "").lower()
        lowered_desc = str(candidate.get("proposed_description") or "").lower()
        combined = f"{lowered_name} {lowered_desc}".strip()
        ambiguity_flags = candidate.get("ambiguity_flags") or []
        if any(token in combined for token in AMBIGUOUS_EVIDENCE_TOKENS + AMBIGUOUS_CONTROL_TOKENS):
            if not ambiguity_flags:
                errors.append(
                    f"candidate_assets[{index}].ambiguity_flags are required for ambiguous asset candidates"
                )

        if any(token in combined for token in OUT_OF_SCOPE_TOKENS):
            errors.append(
                f"candidate_assets[{index}] contains out-of-scope final-decision language"
            )

    if enforce_shape and request_data.get("strict_mode") and draft.get("overall_confidence", 0.0) < 0.75:
        if not draft.get("blocking_questions"):
            errors.append("blocking_questions are required for low-confidence strict-mode drafts")

    if errors:
        raise AssetSuggestionDraftValidationError(
            "ai_asset_suggestion_guardrails_failed",
            "Generated advisory asset suggestion draft violated Step 3A guardrails.",
            errors,
        )