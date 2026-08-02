from __future__ import annotations

import re
from typing import Any

from .data_loader import FrameworkRecord


STOPWORDS = {
    "and",
    "for",
    "the",
    "with",
    "new",
    "newly",
    "organization",
    "organisation",
    "company",
    "group",
    "project",
    "system",
    "platform",
    "solution",
    "please",
    "need",
    "create",
}


def _tokenize(*parts: str) -> set[str]:
    tokens: set[str] = set()
    for part in parts:
        for token in re.findall(r"[a-z0-9][a-z0-9_-]{1,}", (part or "").lower()):
            if token not in STOPWORDS:
                tokens.add(token)
    return tokens


def rank_frameworks(profile: dict[str, Any], catalog: tuple[FrameworkRecord, ...], *, limit: int = 5) -> list[dict[str, Any]]:
    query_parts = [
        str(profile.get("name", "")),
        str(profile.get("description", "")),
        str(profile.get("industry", "")),
        str(profile.get("country", "")),
        str(profile.get("size", "")),
        " ".join(profile.get("keywords", []) if isinstance(profile.get("keywords"), list) else []),
    ]
    query_tokens = _tokenize(*query_parts)

    rankings: list[dict[str, Any]] = []
    for framework in catalog:
        framework_tokens = _tokenize(framework.searchable_text)
        overlap = query_tokens & framework_tokens
        if not overlap:
            continue
        name_tokens = _tokenize(framework.name, framework.ref_id)
        score = len(overlap) * 2 + len(query_tokens & name_tokens) * 3
        if "privacy" in query_tokens and any(token in framework_tokens for token in {"gdpr", "privacy", "data", "personal"}):
            score += 5
        if "security" in query_tokens and any(token in framework_tokens for token in {"security", "secure", "cyber", "information"}):
            score += 4
        if "ai" in query_tokens and any(token in framework_tokens for token in {"ai", "llm", "artificial", "intelligence"}):
            score += 4
        if "health" in query_tokens and any(token in framework_tokens for token in {"health", "hospital", "medical", "pharma"}):
            score += 4
        reason_tokens = sorted(list(overlap))[:6]
        rankings.append(
            {
                "name": framework.name,
                "ref_id": framework.ref_id,
                "urn": framework.urn,
                "score": score,
                "reason": f"Matched keywords: {', '.join(reason_tokens)}" if reason_tokens else "Matched profile context",
                "source": "rule_engine",
                "total_controls": framework.total_controls,
                "assessable_controls": framework.assessable_controls,
            }
        )

    if not rankings and catalog:
        fallback_catalog = sorted(
            catalog,
            key=lambda item: (item.total_controls, item.assessable_controls, item.name.lower()),
            reverse=True,
        )
        for framework in fallback_catalog[:limit]:
            rankings.append(
                {
                    "name": framework.name,
                    "ref_id": framework.ref_id,
                    "urn": framework.urn,
                    "score": 1,
                    "reason": "Generic baseline recommendation from catalog coverage",
                    "source": "rule_engine",
                    "total_controls": framework.total_controls,
                    "assessable_controls": framework.assessable_controls,
                }
            )

    rankings.sort(key=lambda item: (-item["score"], item["name"].lower()))
    return rankings[:limit]


def recommend_scope(profile: dict[str, Any], *, scope_sources: tuple[str, ...]) -> dict[str, Any]:
    name = str(profile.get("name", ""))
    description = str(profile.get("description", ""))
    text = f"{name} {description}".lower()

    selected_content_type = str(profile.get("content_type", "")).upper().strip()
    if selected_content_type not in {"DO", "EN", "GL", "DOMAIN", "ENCLAVE"}:
        selected_content_type = ""

    if selected_content_type in {"DOMAIN"}:
        selected_content_type = "DO"
    elif selected_content_type in {"ENCLAVE"}:
        selected_content_type = "EN"

    enclave_keywords = {
        "sandbox",
        "pilot",
        "proof of concept",
        "poc",
        "third party",
        "supplier",
        "vendor",
        "lab",
        "temporary",
        "test",
        "migration",
    }
    domain_keywords = {
        "subsidiary",
        "department",
        "division",
        "branch",
        "region",
        "country",
        "office",
        "business unit",
        "team",
        "enterprise",
        "organization",
        "organisation",
    }

    if selected_content_type:
        recommended = selected_content_type
        reason = "Manual selection preserved from the creation payload"
    elif any(keyword in text for keyword in enclave_keywords):
        recommended = "EN"
        reason = "Detected enclave-style isolation terms in the organization draft"
    elif any(keyword in text for keyword in domain_keywords):
        recommended = "DO"
        reason = "Detected domain-style organization terms in the organization draft"
    else:
        recommended = "DO"
        reason = "Defaulting to a standard domain scope for a new organization"

    create_iam_groups = profile.get("create_iam_groups")
    if create_iam_groups is None:
        create_iam_groups = recommended == "DO"

    return {
        "current_content_type": selected_content_type or None,
        "recommended_content_type": recommended,
        "recommended_content_type_label": {
            "DO": "DOMAIN",
            "EN": "ENCLAVE",
            "GL": "GLOBAL",
        }.get(recommended, recommended),
        "recommended_create_iam_groups": bool(create_iam_groups),
        "reason": reason,
        "source": "rule_engine",
        "scope_sources": list(scope_sources[:10]),
    }