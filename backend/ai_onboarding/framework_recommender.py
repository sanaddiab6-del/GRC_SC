from __future__ import annotations

from typing import Any

from .data_loader import framework_source_files, load_framework_catalog
from .llm_engine import is_configured, query_qwen_json
from .prompt_builder import build_framework_prompt
from .rule_engine import rank_frameworks


def _validated_llm_frameworks(
    llm_result: dict[str, Any] | None, rule_rankings: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    if not isinstance(llm_result, dict):
        return []

    llm_rankings = llm_result.get("frameworks")
    if not isinstance(llm_rankings, list):
        return []

    candidate_lookup = {item["ref_id"]: item for item in rule_rankings}
    ordered: list[dict[str, Any]] = []
    seen_ref_ids: set[str] = set()

    for item in llm_rankings:
        if not isinstance(item, dict):
            continue

        ref_id = str(item.get("ref_id", "")).strip()
        if not ref_id or ref_id not in candidate_lookup or ref_id in seen_ref_ids:
            continue

        merged = dict(candidate_lookup[ref_id])
        score = item.get("score")
        if isinstance(score, (int, float)):
            merged["score"] = score

        reason = str(item.get("reason", "")).strip()
        if reason:
            merged["reason"] = reason

        merged["source"] = "llm"
        ordered.append(merged)
        seen_ref_ids.add(ref_id)

    return ordered


def recommend_frameworks(profile: dict[str, Any], *, base_dir: str) -> dict[str, Any]:
    catalog = load_framework_catalog(base_dir)
    rule_rankings = rank_frameworks(profile, catalog)

    llm_result = None
    if is_configured():
        system_prompt, llm_payload = build_framework_prompt(profile, rule_rankings)
        llm_result = query_qwen_json(system_prompt, llm_payload)

    ordered = _validated_llm_frameworks(llm_result, rule_rankings)
    if ordered:
        return {
            "source": "llm",
            "advisory_only": True,
            "recommendations": ordered,
            "candidate_count": len(catalog),
            "source_files": list(framework_source_files(base_dir)),
        }

    return {
        "source": "rule_engine",
        "advisory_only": True,
        "recommendations": rule_rankings,
        "candidate_count": len(catalog),
        "source_files": list(framework_source_files(base_dir)),
    }