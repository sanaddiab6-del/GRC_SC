from __future__ import annotations

from typing import Any


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
    "applied_control_drafts",
    "vulnerability_drafts",
    "risk_scenario_drafts",
    "evidence_drafts",
    "evidence_revision_drafts",
    "finding_drafts",
    "findings_assessment_drafts",
    "remediation_drafts",
    "risk_acceptance",
    "risk_acceptance_decision",
    "workflow_case",
    "workflow_case_id",
    "requirement_assessment_updates",
    "compliance_result",
    "final_result",
    "final_compliance_result",
    "final_risk_decision",
    "audit_closure",
}

PROHIBITED_NESTED_KEYS = {
    "applied_control",
    "applied_controls",
    "control",
    "controls",
    "vulnerability",
    "vulnerabilities",
    "risk_scenario",
    "risk_scenarios",
    "evidence",
    "evidences",
    "evidence_revision",
    "evidence_revisions",
    "finding",
    "findings",
    "findings_assessment",
    "findings_assessments",
    "remediation",
    "remediations",
    "action_plan",
    "risk_acceptance",
    "workflow_case",
    "workflow_case_id",
    "requirement_assessment",
    "requirement_assessments",
}

PROHIBITED_APPROVED_FIELDS = {
    "criticality",
    "status",
    "tags",
    "perimeter_id",
    "compliance_assessment_id",
    "risk_assessment_id",
    "framework_id",
    "controls",
    "vulnerabilities",
    "evidence",
    "risks",
    "findings",
    "risk_acceptance",
    "compliance_result",
    "final_result",
    "audit_closure",
}


class AssetCommitValidationError(Exception):
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


def validate_asset_commit_guardrails(payload: dict[str, Any]) -> None:
    blocking_errors: list[dict[str, Any]] = []

    for field in PROHIBITED_TOP_LEVEL_FIELDS:
        if field in payload:
            blocking_errors.append(
                {
                    "code": "out_of_scope_field",
                    "detail": f"{field} is out of scope for Step 3B.",
                    "field": field,
                }
            )

    for path, node in _iter_nodes(payload):
        if not isinstance(node, dict):
            continue

        for key, value in node.items():
            lowered_key = key.lower()
            field_path = f"{path}.{key}" if path else key

            if lowered_key in PROHIBITED_NESTED_KEYS:
                blocking_errors.append(
                    {
                        "code": "out_of_scope_field",
                        "detail": f"{key} is out of scope for Step 3B.",
                        "field": field_path,
                    }
                )

            if path.endswith("approved_fields") and lowered_key in PROHIBITED_APPROVED_FIELDS:
                blocking_errors.append(
                    {
                        "code": "unsupported_asset_field",
                        "detail": f"{key} is not a supported Step 3B Asset field.",
                        "field": field_path,
                    }
                )

            if lowered_key in {"result", "final_result", "overall_result", "decision", "compliance_result"}:
                lowered_value = str(value or "").strip().lower()
                if lowered_value in FINAL_DECISION_VALUES:
                    blocking_errors.append(
                        {
                            "code": "final_decision_forbidden",
                            "detail": f"{key} must not set a final compliance or risk decision in Step 3B.",
                            "field": field_path,
                        }
                    )

            if lowered_key == "status":
                lowered_value = str(value or "").strip().lower()
                if lowered_value in FINAL_STATUS_VALUES:
                    blocking_errors.append(
                        {
                            "code": "final_status_forbidden",
                            "detail": f"{key} must not close or finalize any workflow in Step 3B.",
                            "field": field_path,
                        }
                    )

    if blocking_errors:
        raise AssetCommitValidationError(
            "ai_asset_commit_guardrails_failed",
            "The Step 3B payload contains out-of-scope or final-decision fields.",
            status_code=422,
            blocking_errors=blocking_errors,
        )