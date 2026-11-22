from __future__ import annotations

from typing import Any


# Step 5B is a deterministic write step. It must never carry AI or final-decision
# instructions. These keys are forbidden anywhere in the request payload.
PROHIBITED_TOP_LEVEL_FIELDS = {
    "use_ai",
    "ai_provider",
    "provider_mode",
    "run_ai",
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
    "compliance_result",
    "final_result",
    "risk_acceptance",
    "audit_closure",
    "close_audit",
    "accept_risk",
}


class EvidenceFindingCommitValidationError(Exception):
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


def validate_evidence_finding_commit_guardrails(payload: dict[str, Any]) -> None:
    blocking_errors: list[dict[str, Any]] = []

    for field in PROHIBITED_TOP_LEVEL_FIELDS:
        if field in payload:
            blocking_errors.append(
                {
                    "code": "out_of_scope_field",
                    "detail": f"{field} is out of scope for the deterministic Step 5B commit.",
                    "field": field,
                }
            )

    for path, node in _iter_nodes(payload):
        if not isinstance(node, dict):
            continue
        for key in node:
            lowered = key.lower()
            if lowered in PROHIBITED_NESTED_KEYS:
                blocking_errors.append(
                    {
                        "code": "out_of_scope_field",
                        "detail": f"{key} is out of scope for the deterministic Step 5B commit.",
                        "field": f"{path}.{key}" if path else key,
                    }
                )

    if blocking_errors:
        raise EvidenceFindingCommitValidationError(
            "ai_evidence_finding_commit_guardrails_failed",
            "The Step 5B payload contains out-of-scope or AI/final-decision fields.",
            status_code=422,
            blocking_errors=blocking_errors,
        )
