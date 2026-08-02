from __future__ import annotations

from typing import Any

from .llm_config import (
    CAPABILITY_APPLIED_CONTROL_SUGGESTION,
    CAPABILITY_ASSET_SUGGESTION,
    CAPABILITY_CASE_INTAKE,
)
from .llm_errors import AdvisoryProviderSelectionError, AiProviderOutputValidationError


BASE_FORBIDDEN_KEYS = {
    "create_now",
    "auto_create",
    "approve_automatically",
    "create_records",
    "update_requirement_result",
    "close_audit",
    "accept_risk",
    "compliance_result",
    "final_compliance_result",
    "final_result",
    "risk_decision",
    "risk_acceptance",
    "audit_closure",
    "finding_drafts",
}

FORBIDDEN_KEYS_BY_CAPABILITY = {
    CAPABILITY_CASE_INTAKE: BASE_FORBIDDEN_KEYS
    | {
        "close_audit",
        "risk_decision",
    },
    CAPABILITY_ASSET_SUGGESTION: BASE_FORBIDDEN_KEYS
    | {
        "applied_control_drafts",
        "vulnerability_drafts",
        "risk_scenario_drafts",
        "evidence_drafts",
        "requirement_assessment_updates",
    },
    CAPABILITY_APPLIED_CONTROL_SUGGESTION: BASE_FORBIDDEN_KEYS
    | {
        "vulnerability_drafts",
        "risk_scenario_drafts",
        "evidence_drafts",
        "evidence",
        "finding",
        "findings",
        "vulnerability",
        "remediation",
        "risk_scenario",
        "requirement_assessment_updates",
        "result",
        "status",
    },
}

SCHEMA_NAME_BY_CAPABILITY = {
    CAPABILITY_CASE_INTAKE: "case_intake_draft",
    CAPABILITY_ASSET_SUGGESTION: "asset_suggestion_draft",
    CAPABILITY_APPLIED_CONTROL_SUGGESTION: "applied_control_suggestion_draft",
}

TOP_LEVEL_REQUIRED_KEYS = {
    CAPABILITY_CASE_INTAKE: {
        "draft_type",
        "schema_version",
        "source_summary",
        "overall_confidence",
        "needs_human_review",
        "blocking_questions",
        "warnings",
        "case_context",
        "framework_resolution",
        "case_setup_draft",
        "asset_drafts",
        "applied_control_drafts",
        "vulnerability_drafts",
        "risk_scenario_drafts",
        "requirement_focus_drafts",
        "evidence_expectation_drafts",
        "human_review_checklist",
        "next_system_actions",
    },
    CAPABILITY_ASSET_SUGGESTION: {
        "draft_type",
        "schema_version",
        "source_summary",
        "provider_mode",
        "candidate_assets",
        "duplicate_candidates",
        "ambiguous_candidates",
        "rejected_candidates",
        "warnings",
        "blocking_questions",
        "needs_human_review",
        "overall_confidence",
        "next_allowed_steps",
    },
    CAPABILITY_APPLIED_CONTROL_SUGGESTION: {
        "draft_type",
        "schema_version",
        "source_summary",
        "provider_mode",
        "candidate_applied_controls",
        "duplicate_candidates",
        "ambiguous_candidates",
        "rejected_candidates",
        "warnings",
        "blocking_questions",
        "needs_human_review",
        "overall_confidence",
        "next_allowed_steps",
    },
}

ALLOWED_TOP_LEVEL_KEYS = {
    CAPABILITY_CASE_INTAKE: TOP_LEVEL_REQUIRED_KEYS[CAPABILITY_CASE_INTAKE]
    | {"canonical_mappings_used", "risk_assessment_draft"},
    CAPABILITY_ASSET_SUGGESTION: TOP_LEVEL_REQUIRED_KEYS[CAPABILITY_ASSET_SUGGESTION],
    CAPABILITY_APPLIED_CONTROL_SUGGESTION: TOP_LEVEL_REQUIRED_KEYS[
        CAPABILITY_APPLIED_CONTROL_SUGGESTION
    ],
}

EXPECTED_DRAFT_TYPE = {
    CAPABILITY_CASE_INTAKE: "AiCaseIntakeDraft",
    CAPABILITY_ASSET_SUGGESTION: "AiAssetSuggestionDraft",
    CAPABILITY_APPLIED_CONTROL_SUGGESTION: "AiAppliedControlSuggestionDraft",
}

EXPECTED_SCHEMA_VERSION = {
    CAPABILITY_CASE_INTAKE: "0.2.0",
    CAPABILITY_ASSET_SUGGESTION: "0.1.0",
    CAPABILITY_APPLIED_CONTROL_SUGGESTION: "0.1.0",
}


CAPABILITY_JSON_SCHEMAS: dict[str, dict[str, Any]] = {
    CAPABILITY_CASE_INTAKE: {
        "type": "object",
        "additionalProperties": False,
        "required": sorted(TOP_LEVEL_REQUIRED_KEYS[CAPABILITY_CASE_INTAKE]),
        "properties": {
            "draft_type": {"type": "string", "const": "AiCaseIntakeDraft"},
            "schema_version": {"type": "string"},
            "source_summary": {"type": "object"},
            "overall_confidence": {"type": "number", "minimum": 0, "maximum": 1},
            "needs_human_review": {"type": "boolean", "const": True},
            "blocking_questions": {"type": "array"},
            "warnings": {"type": "array"},
            "canonical_mappings_used": {"type": "array"},
            "case_context": {"type": "object"},
            "framework_resolution": {"type": "object"},
            "case_setup_draft": {"type": "object"},
            "asset_drafts": {"type": "array"},
            "applied_control_drafts": {"type": "array"},
            "vulnerability_drafts": {"type": "array"},
            "risk_assessment_draft": {},
            "risk_scenario_drafts": {"type": "array"},
            "requirement_focus_drafts": {"type": "array"},
            "evidence_expectation_drafts": {"type": "array"},
            "human_review_checklist": {"type": "array"},
            "next_system_actions": {"type": "array"},
        },
    },
    CAPABILITY_ASSET_SUGGESTION: {
        "type": "object",
        "additionalProperties": False,
        "required": sorted(TOP_LEVEL_REQUIRED_KEYS[CAPABILITY_ASSET_SUGGESTION]),
        "properties": {
            "draft_type": {"type": "string", "const": "AiAssetSuggestionDraft"},
            "schema_version": {"type": "string"},
            "source_summary": {"type": "object"},
            "provider_mode": {"type": "string"},
            "candidate_assets": {"type": "array"},
            "duplicate_candidates": {"type": "array"},
            "ambiguous_candidates": {"type": "array"},
            "rejected_candidates": {"type": "array"},
            "warnings": {"type": "array"},
            "blocking_questions": {"type": "array"},
            "needs_human_review": {"type": "boolean", "const": True},
            "overall_confidence": {"type": "number", "minimum": 0, "maximum": 1},
            "next_allowed_steps": {"type": "array"},
        },
    },
    CAPABILITY_APPLIED_CONTROL_SUGGESTION: {
        "type": "object",
        "additionalProperties": False,
        "required": sorted(TOP_LEVEL_REQUIRED_KEYS[CAPABILITY_APPLIED_CONTROL_SUGGESTION]),
        "properties": {
            "draft_type": {
                "type": "string",
                "const": "AiAppliedControlSuggestionDraft",
            },
            "schema_version": {"type": "string"},
            "source_summary": {"type": "object"},
            "provider_mode": {"type": "string"},
            "candidate_applied_controls": {"type": "array"},
            "duplicate_candidates": {"type": "array"},
            "ambiguous_candidates": {"type": "array"},
            "rejected_candidates": {"type": "array"},
            "warnings": {"type": "array"},
            "blocking_questions": {"type": "array"},
            "needs_human_review": {"type": "boolean", "const": True},
            "overall_confidence": {"type": "number", "minimum": 0, "maximum": 1},
            "next_allowed_steps": {"type": "array"},
        },
    },
}


def get_capability_json_schema(capability: str) -> dict[str, Any]:
    schema = CAPABILITY_JSON_SCHEMAS.get(capability)
    if schema is None:
        raise AdvisoryProviderSelectionError(
            "unsupported_ai_capability",
            f"Unsupported AI capability '{capability}'.",
        )
    return schema


def get_capability_schema_name(capability: str) -> str:
    schema_name = SCHEMA_NAME_BY_CAPABILITY.get(capability)
    if schema_name is None:
        raise AdvisoryProviderSelectionError(
            "unsupported_ai_capability",
            f"Unsupported AI capability '{capability}'.",
        )
    return schema_name


def _walk_keys(value: Any, *, prefix: str = "") -> list[str]:
    seen_keys: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            current = f"{prefix}.{key}" if prefix else key
            seen_keys.append(current)
            seen_keys.extend(_walk_keys(child, prefix=current))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            current = f"{prefix}[{index}]"
            seen_keys.extend(_walk_keys(item, prefix=current))
    return seen_keys


def validate_provider_output_schema(
    capability: str,
    payload: dict[str, Any],
    *,
    strict_mode: bool,
) -> None:
    if capability not in TOP_LEVEL_REQUIRED_KEYS:
        raise AdvisoryProviderSelectionError(
            "unsupported_ai_capability",
            f"Unsupported AI capability '{capability}'.",
        )

    if not isinstance(payload, dict):
        raise AiProviderOutputValidationError(
            "ai_provider_invalid_output",
            "The configured AI provider did not return a JSON object.",
        )

    errors: list[str] = []

    if capability == CAPABILITY_APPLIED_CONTROL_SUGGESTION:
        candidates = payload.get("candidate_applied_controls")
        if not isinstance(candidates, list):
            errors.append("candidate_applied_controls must be an array.")
        if strict_mode:
            unknown_keys = sorted(set(payload.keys()) - ALLOWED_TOP_LEVEL_KEYS[capability])
            if unknown_keys:
                errors.append(
                    "Unknown top-level keys are not allowed in strict mode: "
                    + ", ".join(unknown_keys)
                )
        if "draft_type" in payload and payload.get("draft_type") != EXPECTED_DRAFT_TYPE[capability]:
            errors.append(f"draft_type must be '{EXPECTED_DRAFT_TYPE[capability]}'.")
        if "schema_version" in payload and payload.get("schema_version") != EXPECTED_SCHEMA_VERSION[capability]:
            errors.append(f"schema_version must be '{EXPECTED_SCHEMA_VERSION[capability]}'.")
        if "needs_human_review" in payload and payload.get("needs_human_review") is not True:
            errors.append("needs_human_review must be true.")
    else:
        required_keys = TOP_LEVEL_REQUIRED_KEYS[capability]
        missing_keys = sorted(required_keys - set(payload.keys()))
        if missing_keys:
            errors.append(
                "Missing required top-level keys: " + ", ".join(missing_keys)
            )

        if strict_mode:
            allowed_keys = ALLOWED_TOP_LEVEL_KEYS[capability]
            unknown_keys = sorted(set(payload.keys()) - allowed_keys)
            if unknown_keys:
                errors.append(
                    "Unknown top-level keys are not allowed in strict mode: "
                    + ", ".join(unknown_keys)
                )

        expected_draft_type = EXPECTED_DRAFT_TYPE[capability]
        if payload.get("draft_type") != expected_draft_type:
            errors.append(
                f"draft_type must be '{expected_draft_type}'."
            )

        expected_schema_version = EXPECTED_SCHEMA_VERSION[capability]
        if payload.get("schema_version") != expected_schema_version:
            errors.append(
                f"schema_version must be '{expected_schema_version}'."
            )

        if payload.get("needs_human_review") is not True:
            errors.append("needs_human_review must be true.")

    forbidden_keys = FORBIDDEN_KEYS_BY_CAPABILITY[capability]
    for key_path in _walk_keys(payload):
        key_name = key_path.rsplit(".", 1)[-1]
        if "[" in key_name:
            continue
        if key_name in forbidden_keys:
            errors.append(f"Forbidden key found in provider output: {key_path}")

    if errors:
        raise AiProviderOutputValidationError(
            "ai_provider_invalid_output",
            "Configured AI provider output failed schema safety checks.",
            errors=errors,
        )
