from __future__ import annotations

from pathlib import Path
from typing import Any

from .framework_recommender import recommend_frameworks
from .scope_recommender import recommend_scope_selection


def _normalize_profile(profile: dict[str, Any]) -> dict[str, Any]:
    normalized = dict(profile)

    if not normalized.get("country") and normalized.get("region"):
        normalized["country"] = normalized["region"]

    if not normalized.get("size") and normalized.get("company_size"):
        normalized["size"] = normalized["company_size"]

    content_type = normalized.get("content_type")
    if isinstance(content_type, str) and content_type.strip():
        normalized["content_type"] = content_type.strip().upper()

    return normalized


def build_onboarding_recommendations(profile: dict[str, Any], *, base_dir: str | None = None) -> dict[str, Any]:
    resolved_base_dir = base_dir or str(Path(__file__).resolve().parents[1])
    safe_profile = _normalize_profile(profile if isinstance(profile, dict) else {})

    framework_result = recommend_frameworks(safe_profile, base_dir=resolved_base_dir)
    scope_result = recommend_scope_selection(safe_profile, base_dir=resolved_base_dir)

    return {
        "advisory_only": True,
        "frameworks": framework_result,
        "scope": scope_result,
    }