from __future__ import annotations

from typing import Any


FINAL_COMPLIANCE_VALUES = {
    "compliant",
    "non_compliant",
    "partially_compliant",
    "not_applicable",
    "approved",
    "final",
}
FINAL_AUDIT_STATUS_VALUES = {"done", "closed", "final", "approved"}
PROHIBITED_ENTITY_VALUES = {"RiskAcceptance"}


class CaseIntakeDraftValidationError(Exception):
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


def _iter_dicts(value: Any):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from _iter_dicts(child)
    elif isinstance(value, list):
        for item in value:
            yield from _iter_dicts(item)


def _collect_explainability_errors(value: Any, path: str, errors: list[str]) -> None:
    if isinstance(value, dict):
        if "platform_entity" in value and not path.startswith("canonical_mappings_used"):
            for required_key in ("confidence", "rationale", "source_text_refs", "needs_review"):
                if required_key not in value:
                    errors.append(f"{path}.{required_key} is required")
        for key, child in value.items():
            child_path = f"{path}.{key}" if path else key
            _collect_explainability_errors(child, child_path, errors)
    elif isinstance(value, list):
        for index, item in enumerate(value):
            _collect_explainability_errors(item, f"{path}[{index}]", errors)


def validate_case_intake_guardrails(
    draft: dict[str, Any],
    request_data: dict[str, Any],
    *,
    enforce_shape: bool = True,
) -> None:
    errors: list[str] = []

    if enforce_shape:
        if not draft.get("needs_human_review"):
            errors.append("needs_human_review must be true for Step 1.")

        _collect_explainability_errors(draft, "", errors)

    compliance_draft = draft.get("case_setup_draft", {}).get("compliance_assessment_draft", {})
    if str(compliance_draft.get("status") or "").strip().lower() in FINAL_AUDIT_STATUS_VALUES:
        errors.append("case_setup_draft.compliance_assessment_draft.status must not finalize or close an audit")

    for index, item in enumerate(draft.get("requirement_focus_drafts", [])):
        for key, value in item.items():
            if any(token in key.lower() for token in ("result", "status", "decision", "approval")):
                lowered = str(value or "").strip().lower()
                if lowered in FINAL_COMPLIANCE_VALUES:
                    errors.append(
                        f"requirement_focus_drafts[{index}].{key} must not set a final compliance decision"
                    )

    if enforce_shape:
        for index, action in enumerate(draft.get("next_system_actions", [])):
            if action.get("may_write_database"):
                errors.append(f"next_system_actions[{index}].may_write_database must be false")

    for item in _iter_dicts(draft):
        platform_entity = item.get("platform_entity") if isinstance(item, dict) else None
        if platform_entity in PROHIBITED_ENTITY_VALUES:
            errors.append(f"{platform_entity} must not be emitted by the advisory parser")
        if isinstance(item, dict) and str(item.get("treatment") or "").strip().lower() == "accept":
            errors.append("Risk treatment must not accept residual risk in the advisory parser")

    if (
        enforce_shape
        and request_data.get("strict_mode")
        and draft.get("overall_confidence", 0.0) < 0.75
    ):
        if not draft.get("blocking_questions"):
            errors.append("blocking_questions are required for low-confidence strict-mode drafts")

    if errors:
        raise CaseIntakeDraftValidationError(
            "ai_draft_guardrails_failed",
            "Generated advisory draft violated Step 1 guardrails.",
            errors,
        )