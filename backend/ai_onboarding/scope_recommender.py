from __future__ import annotations

from typing import Any

from .file_discovery import discover_scope_files
from .llm_engine import is_configured, query_qwen_json
from .prompt_builder import build_scope_prompt
from .rule_engine import recommend_scope


ALLOWED_CONTENT_TYPES = ("DO", "EN", "GL")


def _normalize_content_type(value: Any) -> str:
    normalized = str(value or "").upper().strip()
    if normalized == "DOMAIN":
        return "DO"
    if normalized == "ENCLAVE":
        return "EN"
    return normalized


def _validate_scope_recommendation(
    llm_result: dict[str, Any] | None,
    rule_recommendation: dict[str, Any],
    scope_source_count: int,
) -> dict[str, Any] | None:
    if not isinstance(llm_result, dict):
        return None

    raw_scope = llm_result.get("scope")
    if not isinstance(raw_scope, dict):
        raw_scope = llm_result

    recommended_content_type = _normalize_content_type(
        raw_scope.get("recommended_content_type")
    )
    current_content_type = rule_recommendation.get("current_content_type")
    if recommended_content_type not in ALLOWED_CONTENT_TYPES:
        return None

    if current_content_type and recommended_content_type != current_content_type:
        return None

    create_iam_groups = raw_scope.get("recommended_create_iam_groups")
    if not isinstance(create_iam_groups, bool):
        create_iam_groups = rule_recommendation.get("recommended_create_iam_groups")

    reason = str(raw_scope.get("reason", "")).strip() or rule_recommendation.get("reason")

    validated = dict(rule_recommendation)
    validated.update(
        {
            "recommended_content_type": recommended_content_type,
            "recommended_content_type_label": {
                "DO": "DOMAIN",
                "EN": "ENCLAVE",
                "GL": "GLOBAL",
            }.get(recommended_content_type, recommended_content_type),
            "recommended_create_iam_groups": bool(create_iam_groups),
            "reason": reason,
            "source": "llm",
            "scope_source_count": scope_source_count,
        }
    )
    return validated


def recommend_scope_selection(profile: dict[str, Any], *, base_dir: str) -> dict[str, Any]:
    scope_sources = discover_scope_files(base_dir)
    rule_recommendation = recommend_scope(profile, scope_sources=scope_sources)
    scope_source_count = len(scope_sources)

    if is_configured():
        system_prompt, llm_payload = build_scope_prompt(
            profile, rule_recommendation, ALLOWED_CONTENT_TYPES
        )
        llm_result = query_qwen_json(system_prompt, llm_payload)
        validated = _validate_scope_recommendation(
            llm_result, rule_recommendation, scope_source_count
        )
        if validated:
            return validated

    rule_recommendation["scope_source_count"] = scope_source_count
    return rule_recommendation