from __future__ import annotations

from typing import Any


FRAMEWORK_SYSTEM_PROMPT = """
You are an advisory onboarding assistant for a GRC platform.
Return JSON only.
Do not invent frameworks that are not in the candidate list.
Choose the best framework recommendations from the provided candidates.
Output format:
{
  "frameworks": [
    {
      "ref_id": "candidate ref_id",
      "score": 0-100,
      "reason": "short justification"
    }
  ]
}
""".strip()


SCOPE_SYSTEM_PROMPT = """
You are an advisory onboarding assistant for a GRC platform.
Return JSON only.
Recommend only one scope option from the allowed content types.
If the profile already contains a manual content type, preserve it.
Output format:
{
  "scope": {
    "recommended_content_type": "DO or EN or GL",
    "recommended_create_iam_groups": true,
    "reason": "short justification"
  }
}
""".strip()


CASE_INTAKE_SYSTEM_PROMPT = """
You are an advisory-only GRC case intake assistant for the Sanadcom platform.
Return JSON only.
Follow the requested schema exactly.
Use only canonical platform entities such as Folder, Perimeter, ComplianceAssessment,
RequirementNode, RequirementAssessment, Asset, AppliedControl, Evidence,
EvidenceRevision, RiskAssessment, RiskScenario, Finding, and RiskAcceptance.
Do not invent database ids or claim records were created.
Do not emit final compliance decisions.
Do not emit final risk-acceptance decisions.
Do not emit audit closure decisions.
Every inferred draft object must include confidence, rationale, source_text_refs,
and needs_review.
If information is ambiguous, set needs_review to true and add blocking_questions.
""".strip()


def build_framework_prompt(
    profile: dict[str, Any], candidates: list[dict[str, Any]]
) -> tuple[str, dict[str, Any]]:
    payload = {
        "profile": profile,
        "candidates": [
            {
                "ref_id": item.get("ref_id"),
                "name": item.get("name"),
                "score": item.get("score"),
                "reason": item.get("reason"),
                "provider": item.get("provider"),
                "total_controls": item.get("total_controls"),
                "assessable_controls": item.get("assessable_controls"),
            }
            for item in candidates
        ],
    }
    return FRAMEWORK_SYSTEM_PROMPT, payload


def build_scope_prompt(
    profile: dict[str, Any],
    rule_recommendation: dict[str, Any],
    allowed_content_types: tuple[str, ...],
) -> tuple[str, dict[str, Any]]:
    payload = {
        "profile": profile,
        "allowed_content_types": list(allowed_content_types),
        "rule_recommendation": {
            "current_content_type": rule_recommendation.get("current_content_type"),
            "recommended_content_type": rule_recommendation.get(
                "recommended_content_type"
            ),
            "recommended_create_iam_groups": rule_recommendation.get(
                "recommended_create_iam_groups"
            ),
            "reason": rule_recommendation.get("reason"),
        },
    }
    return SCOPE_SYSTEM_PROMPT, payload


def build_case_intake_prompt(
    request_payload: dict[str, Any],
    *,
    schema_version: str,
    allowed_platform_entities: tuple[str, ...],
) -> tuple[str, dict[str, Any]]:
    payload = {
        "schema_version": schema_version,
        "allowed_platform_entities": list(allowed_platform_entities),
        "request": request_payload,
    }
    return CASE_INTAKE_SYSTEM_PROMPT, payload