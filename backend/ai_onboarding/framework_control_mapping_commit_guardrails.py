from __future__ import annotations

from typing import Any


# Step 7B is a deterministic write step. It must never carry AI instructions, provider
# configuration, or final-decision instructions. These keys are forbidden anywhere in the
# payload.
PROHIBITED_TOP_LEVEL_FIELDS = {
    "use_ai",
    "run_ai",
    "ai_provider",
    "provider_mode",
    "llm",
    "model",
    "prompt",
    "system_prompt",
    "temperature",
    "overall_confidence",
    "create_framework",
    "create_requirement",
    "create_control",
    "create_reference_control",
    "create_framework_control",
    "create_mapping",
    "approve_mapping",
    "auto_approve",
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

PROHIBITED_NESTED_KEYS = {
    "use_ai",
    "run_ai",
    "ai_provider",
    "provider_mode",
    "llm",
    "model",
    "prompt",
    "system_prompt",
    "temperature",
    "create_framework",
    "create_requirement",
    "create_control",
    "create_reference_control",
    "create_framework_control",
    "create_mapping",
    "approve_mapping",
    "auto_approve",
    "compliance_result",
    "final_result",
    "risk_acceptance",
    "audit_closure",
    "close_audit",
    "accept_risk",
}

# Step 7B addresses platform records through the '*_reference' UUID pattern already used
# by Steps 2B/3B/4B/5B/6B. Raw '*_id' database identifiers are rejected so a caller cannot
# reach past the reference contract. 'temporary_id' is the Step 7A advisory handle, not a
# database identifier.
ALLOWED_ID_SUFFIX_KEYS = {"temporary_id"}


class FrameworkControlMappingCommitValidationError(Exception):
    def __init__(
        self,
        error_code: str,
        detail: str,
        *,
        status_code: int = 422,
        blocking_errors: list[dict[str, Any]] | None = None,
        warnings: list[dict[str, Any]] | None = None,
        response_payload: dict[str, Any] | None = None,
    ):
        super().__init__(detail)
        self.error_code = error_code
        self.detail = detail
        self.status_code = status_code
        self.blocking_errors = blocking_errors or []
        self.warnings = warnings or []
        self.response_payload = response_payload

    def to_response(self) -> dict[str, Any]:
        if self.response_payload is not None:
            return self.response_payload
        return {
            "error_code": self.error_code,
            "detail": self.detail,
            "blocking_errors": self.blocking_errors,
            "warnings": self.warnings,
        }


def _iter_nodes(value: Any, path: str = ""):
    if isinstance(value, dict):
        yield path, value
        for key, child in value.items():
            child_path = f"{path}.{key}" if path else key
            yield from _iter_nodes(child, child_path)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            child_path = f"{path}[{index}]"
            yield from _iter_nodes(child, child_path)


def validate_framework_control_mapping_commit_guardrails(payload: dict[str, Any]) -> None:
    blocking_errors: list[dict[str, Any]] = []

    for field in PROHIBITED_TOP_LEVEL_FIELDS:
        if field in payload:
            blocking_errors.append(
                {
                    "code": "out_of_scope_field",
                    "detail": f"{field} is out of scope for the deterministic Step 7B commit.",
                    "field": field,
                }
            )

    for path, node in _iter_nodes(payload):
        if not isinstance(node, dict):
            continue
        for key in node:
            lowered = key.lower()
            field_path = f"{path}.{key}" if path else key
            if lowered in PROHIBITED_NESTED_KEYS:
                blocking_errors.append(
                    {
                        "code": "out_of_scope_field",
                        "detail": f"{key} is out of scope for the deterministic Step 7B commit.",
                        "field": field_path,
                    }
                )
            elif lowered.endswith("_id") and lowered not in ALLOWED_ID_SUFFIX_KEYS:
                blocking_errors.append(
                    {
                        "code": "raw_database_identifier",
                        "detail": (
                            f"{key} is a raw database identifier; Step 7B addresses records "
                            "through the '*_reference' contract instead."
                        ),
                        "field": field_path,
                    }
                )

    if blocking_errors:
        raise FrameworkControlMappingCommitValidationError(
            "ai_framework_control_mapping_commit_guardrails_failed",
            "The Step 7B payload contains out-of-scope, AI, or raw-identifier fields.",
            status_code=422,
            blocking_errors=blocking_errors,
        )
