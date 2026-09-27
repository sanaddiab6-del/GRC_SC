from __future__ import annotations

from typing import Any

from .evidence_freshness_review_serializers import FRESHNESS_STATUS_CHOICES


# This review is advisory/no-write. These keys would imply a write, a committed record, an
# automatic approval, a compliance certification, or a deletion, and are therefore forbidden
# anywhere in the generated draft (and, defensively, in the request payload).
FORBIDDEN_KEYS = {
    "delete_evidence",
    "approve_requirement",
    "mark_compliant",
    "update_control",
    "create_record",
    "commit",
    "committed",
    "execute",
    "approve",
    "approved",
    "approved_by_user",
    "auto_approve",
    "approve_automatically",
    "create_now",
    "auto_create",
    "create_records",
    "dry_run",
    "idempotency_key",
    "evidence_id",
    "requirement_assessment_id",
    "applied_control_id",
    "finding_id",
    "compliance_assessment_id",
    "compliance_result",
    "final_result",
    "final_compliance_result",
    "risk_acceptance",
    "risk_decision",
    "audit_closure",
    "close_audit",
    "accept_risk",
    "certify_compliance",
    "certification",
    "status",
    "new_status",
    "expiry_date",
}

# Language that would read as a final decision rather than an advisory note, even inside an
# otherwise well-formed free-text field.
OUT_OF_SCOPE_TOKENS = (
    "requirement approved",
    "marked compliant",
    "evidence deleted",
    "control updated",
    "automatically approved",
    "certified compliant",
    "we certify",
    "audit closed",
    "risk accepted",
)


class EvidenceFreshnessReviewValidationError(Exception):
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


def _walk_keys(value: Any):
    if isinstance(value, dict):
        for key, child in value.items():
            yield key
            yield from _walk_keys(child)
    elif isinstance(value, list):
        for item in value:
            yield from _walk_keys(item)


def validate_evidence_freshness_review_request_guardrails(
    payload: dict[str, Any],
) -> dict[str, list[str]]:
    """Defensive check on the inbound request body (before it reaches a serializer)."""
    errors: dict[str, list[str]] = {}
    for field in FORBIDDEN_KEYS:
        if field in payload:
            errors[field] = ["This field is not allowed in the evidence freshness review."]
    return errors


def validate_provider_output_guardrails(result: dict[str, Any]) -> None:
    """Reject provider output that would imply a write, an approval, or a final opinion.

    Raised as a hard failure (never silently substituted with a fallback): safety-relevant
    output should fail loudly, not be quietly papered over.
    """
    errors: list[str] = []

    for key in _walk_keys(result):
        if key in FORBIDDEN_KEYS:
            errors.append(f"Forbidden key found in evidence freshness review output: {key}")

    if not isinstance(result, dict):
        errors.append("Evidence freshness review output must be a JSON object.")
        raise EvidenceFreshnessReviewValidationError(
            "ai_evidence_freshness_review_guardrails_failed",
            "Generated advisory evidence freshness output violated safety guardrails.",
            errors,
        )

    freshness_status = result.get("freshness_status")
    if freshness_status is not None and freshness_status not in FRESHNESS_STATUS_CHOICES:
        errors.append(
            "freshness_status must be one of: " + ", ".join(FRESHNESS_STATUS_CHOICES)
        )

    confidence = result.get("confidence")
    if confidence is not None:
        if not isinstance(confidence, (int, float)) or isinstance(confidence, bool):
            errors.append("confidence must be a number between 0 and 1.")
        elif not 0.0 <= float(confidence) <= 1.0:
            errors.append("confidence must be between 0 and 1.")

    combined_text = " ".join(
        str(result.get(field) or "")
        for field in ("explanation", "recommended_action")
    ).lower()
    combined_text += " " + " ".join(
        str(item) for item in (result.get("concerns") or []) if isinstance(item, str)
    ).lower()
    if any(token in combined_text for token in OUT_OF_SCOPE_TOKENS):
        errors.append(
            "Evidence freshness review output contains out-of-scope final-decision language."
        )

    if errors:
        raise EvidenceFreshnessReviewValidationError(
            "ai_evidence_freshness_review_guardrails_failed",
            "Generated advisory evidence freshness output violated safety guardrails.",
            errors,
        )
