from __future__ import annotations

from ai_onboarding import framework_recommender, scope_recommender, service
from ai_onboarding.service import build_onboarding_recommendations


def test_onboarding_recommendations_return_frameworks_and_scope():
    result = build_onboarding_recommendations(
        {
            "name": "Security and privacy platform for a new SaaS business unit",
            "description": "Need a practical baseline for security, privacy, and compliance",
            "industry": "software",
            "country": "france",
        }
    )

    assert result["advisory_only"] is True
    assert result["frameworks"]["recommendations"]
    assert result["frameworks"]["source"] in {"rule_engine", "llm"}
    assert result["scope"]["recommended_content_type"] == "DO"
    assert result["scope"]["recommended_create_iam_groups"] is True


def test_manual_scope_selection_is_preserved():
    result = build_onboarding_recommendations(
        {
            "name": "Partner sandbox",
            "description": "Temporary third-party pilot environment",
            "content_type": "EN",
            "create_iam_groups": False,
        }
    )

    assert result["scope"]["current_content_type"] == "EN"
    assert result["scope"]["recommended_content_type"] == "EN"
    assert result["scope"]["recommended_create_iam_groups"] is False


def test_service_normalizes_profile_aliases(monkeypatch):
    captured: dict[str, dict] = {}

    def fake_frameworks(profile, *, base_dir):
        captured["frameworks"] = profile
        return {"source": "rule_engine", "recommendations": []}

    def fake_scope(profile, *, base_dir):
        captured["scope"] = profile
        return {"source": "rule_engine", "recommended_content_type": "DO"}

    monkeypatch.setattr(service, "recommend_frameworks", fake_frameworks)
    monkeypatch.setattr(service, "recommend_scope_selection", fake_scope)

    build_onboarding_recommendations(
        {
            "region": "france",
            "company_size": "medium",
            "content_type": "en",
        }
    )

    assert captured["frameworks"]["country"] == "france"
    assert captured["frameworks"]["size"] == "medium"
    assert captured["frameworks"]["content_type"] == "EN"
    assert captured["scope"]["country"] == "france"


def test_framework_recommendations_use_qwen_when_output_is_valid(monkeypatch):
    monkeypatch.setattr(framework_recommender, "is_configured", lambda: True)

    def fake_qwen(system_prompt, payload):
        return {
            "frameworks": [
                {
                    "ref_id": payload["candidates"][1]["ref_id"],
                    "score": 97,
                    "reason": "Best fit for the onboarding profile",
                },
                {"ref_id": "invalid-framework", "score": 100, "reason": "ignore"},
            ]
        }

    monkeypatch.setattr(framework_recommender, "query_qwen_json", fake_qwen)

    result = build_onboarding_recommendations(
        {
            "name": "Security and privacy platform for a new SaaS business unit",
            "description": "Need a practical baseline for security, privacy, and compliance",
            "industry": "software",
            "country": "france",
        }
    )

    assert result["frameworks"]["source"] == "llm"
    assert result["frameworks"]["recommendations"]
    assert result["frameworks"]["recommendations"][0]["source"] == "llm"
    assert all(
        item["ref_id"] != "invalid-framework"
        for item in result["frameworks"]["recommendations"]
    )


def test_scope_recommendations_use_qwen_when_output_is_valid(monkeypatch):
    monkeypatch.setattr(scope_recommender, "is_configured", lambda: True)
    monkeypatch.setattr(
        scope_recommender,
        "query_qwen_json",
        lambda system_prompt, payload: {
            "scope": {
                "recommended_content_type": "EN",
                "recommended_create_iam_groups": False,
                "reason": "Temporary supplier environment should stay isolated",
            }
        },
    )

    result = build_onboarding_recommendations(
        {
            "name": "Partner sandbox",
            "description": "Temporary third-party pilot environment",
        }
    )

    assert result["scope"]["source"] == "llm"
    assert result["scope"]["recommended_content_type"] == "EN"
    assert result["scope"]["recommended_create_iam_groups"] is False


def test_scope_recommendations_fall_back_when_qwen_output_is_invalid(monkeypatch):
    monkeypatch.setattr(scope_recommender, "is_configured", lambda: True)
    monkeypatch.setattr(
        scope_recommender,
        "query_qwen_json",
        lambda system_prompt, payload: {
            "scope": {
                "recommended_content_type": "INVALID",
                "recommended_create_iam_groups": "yes",
                "reason": "unsupported",
            }
        },
    )

    result = build_onboarding_recommendations(
        {
            "name": "Regional business unit",
            "description": "Internal department rollout",
        }
    )

    assert result["scope"]["source"] == "rule_engine"
    assert result["scope"]["recommended_content_type"] == "DO"