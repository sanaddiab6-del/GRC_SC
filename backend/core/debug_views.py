from __future__ import annotations

from typing import Any

from django.conf import settings
from rest_framework import permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from ai_onboarding.data_loader import load_framework_catalog
from ai_onboarding.file_discovery import discover_scope_files
from ai_onboarding.framework_recommender import recommend_frameworks
from ai_onboarding.rule_engine import rank_frameworks, recommend_scope
from ai_onboarding.scope_recommender import recommend_scope_selection
from ai_onboarding.service import build_onboarding_recommendations


@api_view(["GET"])
@permission_classes([permissions.AllowAny])
def recommendation_test_view(request):
    """Return a browser-readable smoke test for recommendation behavior."""

    payload: dict[str, Any] = {
        "industry": request.query_params.get("industry", "SaaS"),
        "region": request.query_params.get("region", "EU"),
        "company_size": request.query_params.get("company_size", "medium"),
        "name": request.query_params.get("name", "EU SaaS platform"),
        "description": request.query_params.get(
            "description", "Local recommendation smoke test"
        ),
    }

    base_dir = settings.BASE_DIR.parent
    service_result = build_onboarding_recommendations(payload, base_dir=str(base_dir))
    rule_catalog = load_framework_catalog(base_dir)
    rule_frameworks = rank_frameworks(payload, rule_catalog)
    scope_sources = discover_scope_files(base_dir)
    rule_scope = recommend_scope(payload, scope_sources=scope_sources)

    framework_mode = service_result["frameworks"]["source"]
    scope_mode = service_result["scope"]["source"]
    ai_mode = "active" if framework_mode == "llm" else "fallback_only"

    issues: list[str] = []
    if not service_result["frameworks"]["recommendations"]:
        issues.append("framework recommendations missing")
    if not service_result["scope"]:
        issues.append("scope recommendations missing")
    if ai_mode == "fallback_only":
        issues.append("AI reranking unavailable; rule-based fallback used")

    report = {
        "test_status": "passed" if service_result["frameworks"]["recommendations"] else "failed",
        "mode_used": "ai" if framework_mode == "llm" else "rule-based",
        "framework_recommendation": {
            "mode": framework_mode,
            "sample_outputs": service_result["frameworks"]["recommendations"][:3],
            "rule_based_sample": rule_frameworks[:3],
        },
        "scope_recommendation": {
            "mode": scope_mode,
            "sample_output": service_result["scope"],
            "rule_based_sample": rule_scope,
        },
        "ai_layer": ai_mode,
        "detected_issues": issues,
        "system_readiness": "ready" if not issues or issues == ["AI reranking unavailable; rule-based fallback used"] else "partial",
        "service_layer": "working" if service_result["frameworks"]["recommendations"] else "failed",
        "data_layer": {
            "framework_sources": service_result["frameworks"]["source_files"],
            "scope_source_count": service_result["scope"]["scope_source_count"],
        },
        "repro": {
            "framework_endpoint": "/debug/recommendation-test/",
            "type": "API response",
            "browser_friendly": True,
        },
        "recommendation_details": {
            "framework_service": service_result["frameworks"],
            "scope_service": service_result["scope"],
        },
    }
    return Response(report)
