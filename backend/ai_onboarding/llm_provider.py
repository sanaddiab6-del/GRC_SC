from __future__ import annotations

import json
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any, Protocol

from .llm_config import (
    CAPABILITY_APPLIED_CONTROL_SUGGESTION,
    CAPABILITY_ASSET_SUGGESTION,
    CAPABILITY_CASE_INTAKE,
    LOCAL_AI_STYLE_OLLAMA,
    LOCAL_PROVIDER,
    AdvisoryCapabilityConfig,
    is_provider_configured,
)
from .llm_errors import AiProviderExecutionError, build_sanitized_provider_detail


class AiProvider(Protocol):
    def generate_structured(
        self,
        *,
        capability: str,
        model: str,
        system_prompt: str,
        user_payload: dict[str, Any],
        json_schema: dict[str, Any],
        timeout_seconds: int,
        max_output_tokens: int,
        temperature: float,
        schema_name: str,
    ) -> dict[str, Any]:
        ...


@dataclass(frozen=True)
class AdvisoryProviderSelection:
    provider: AiProvider | None
    config: AdvisoryCapabilityConfig


class LocalAiProvider:
    def __init__(
        self,
        *,
        base_url: str,
        base_url_safe: bool,
        base_url_warning: str | None,
    ):
        self.base_url = base_url.rstrip("/")
        self.base_url_safe = base_url_safe
        self.base_url_warning = base_url_warning

    def generate_structured(
        self,
        *,
        capability: str,
        model: str,
        system_prompt: str,
        user_payload: dict[str, Any],
        json_schema: dict[str, Any],
        timeout_seconds: int,
        max_output_tokens: int,
        temperature: float,
        schema_name: str,
    ) -> dict[str, Any]:
        if not self.base_url_safe:
            raise AiProviderExecutionError(
                "unsafe_local_ai_base_url",
                self.base_url_warning
                or "LOCAL_AI_BASE_URL failed local safety validation.",
            )

        prompt = _build_ollama_prompt(
            capability=capability,
            system_prompt=system_prompt,
            user_payload=user_payload,
            json_schema=json_schema,
            schema_name=schema_name,
        )

        body = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "format": "json",
            "options": {
                "temperature": temperature,
                "num_predict": max_output_tokens,
            },
        }

        request = urllib.request.Request(
            f"{self.base_url}/api/generate",
            data=json.dumps(body, ensure_ascii=False).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
            },
            method="POST",
        )

        try:
            with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
                response_payload = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            raise AiProviderExecutionError(
                "ai_provider_request_failed",
                build_sanitized_provider_detail(exc),
            ) from exc
        except (urllib.error.URLError, TimeoutError, ValueError, json.JSONDecodeError) as exc:
            raise AiProviderExecutionError(
                "ai_provider_request_failed",
                build_sanitized_provider_detail(exc),
            ) from exc

        extracted = _extract_ollama_response_text(response_payload)
        if extracted is None:
            raise AiProviderExecutionError(
                "local_ai_provider_invalid_output",
                "The local AI provider returned an unreadable response payload.",
            )

        return _parse_single_json_object(extracted)


def _build_ollama_prompt(
    *,
    capability: str,
    system_prompt: str,
    user_payload: dict[str, Any],
    json_schema: dict[str, Any],
    schema_name: str,
) -> str:
    instruction: dict[str, Any] = {
        "capability": capability,
        "schema_name": schema_name,
        "input": user_payload,
        "output_contract": {
            "type": "object",
            "must_return_json_only": True,
            "reject_markdown_or_explanations": True,
        },
    }

    if capability != CAPABILITY_APPLIED_CONTROL_SUGGESTION:
        instruction["output_contract"]["required_top_level_keys"] = sorted(json_schema.get("required", []))

    if capability == CAPABILITY_CASE_INTAKE:
        instruction["output_contract"]["step1_compact_skeleton"] = {
            "draft_type": "AiCaseIntakeDraft",
            "schema_version": "0.2.0",
            "source_summary": {
                "detected_language": "en",
                "input_char_count": 0,
                "strict_mode_applied": True,
                "scenario_excerpt": "",
                "parser_notes": [],
            },
            "overall_confidence": 0.5,
            "needs_human_review": True,
            "blocking_questions": [],
            "warnings": [],
            "canonical_mappings_used": [],
            "case_context": {},
            "framework_resolution": {},
            "case_setup_draft": {},
            "asset_drafts": [],
            "applied_control_drafts": [],
            "vulnerability_drafts": [],
            "risk_assessment_draft": None,
            "risk_scenario_drafts": [],
            "requirement_focus_drafts": [],
            "evidence_expectation_drafts": [],
            "human_review_checklist": [],
            "next_system_actions": [],
        }
        instruction["output_contract"]["step1_hard_rules"] = [
            "No final compliance decision.",
            "No risk acceptance decision.",
            "No audit closure decision.",
            "Use short arrays and concise text.",
            "needs_human_review must be true.",
        ]
    elif capability == CAPABILITY_ASSET_SUGGESTION:
        instruction["output_contract"]["step3a_compact_skeleton"] = {
            "draft_type": "AiAssetSuggestionDraft",
            "schema_version": "0.1.0",
            "source_summary": {
                "detected_language": "en",
                "input_char_count": 0,
                "strict_mode_applied": True,
                "scenario_excerpt": "",
                "provider_mode": "configured_local_provider",
                "folder_id": "<folder_uuid>",
                "perimeter_id": "<perimeter_uuid>",
                "compliance_assessment_id": "<compliance_assessment_uuid>",
                "risk_assessment_id": "<risk_assessment_uuid_or_null>",
                "parser_notes": [],
            },
            "provider_mode": "configured_local_provider",
            "candidate_assets": [
                {
                    "temporary_id": "AST-CAND-001",
                    "proposed_name": "Core Banking Platform",
                    "proposed_description": "Primary in-scope banking application named in the scenario.",
                    "proposed_reference_id": None,
                    "proposed_asset_type": {"value": "PR", "label": "Primary"},
                    "proposed_asset_category": None,
                    "criticality": {
                        "value": "high",
                        "is_platform_writable": False,
                        "mapping_note": "Advisory only",
                    },
                    "folder_id": "<copy input.request.folder_id>",
                    "perimeter_id": "<copy input.request.perimeter_id>",
                    "compliance_assessment_id": "<copy input.request.compliance_assessment_id>",
                    "source_text_references": [
                        {
                            "ref_id": "T1",
                            "excerpt": "Core Banking Platform",
                            "char_start": 0,
                            "char_end": 21,
                        }
                    ],
                    "rationale": "Explicitly named as the assessment scope in the scenario.",
                    "confidence": 0.92,
                    "human_review_status": "pending_review",
                    "ambiguity_flags": [],
                    "allowed_next_actions": [
                        "accept_for_later_commit",
                        "edit_before_commit",
                        "reuse_existing_asset",
                        "reject",
                        "defer",
                    ],
                }
            ],
            "duplicate_candidates": [],
            "ambiguous_candidates": [],
            "rejected_candidates": [],
            "warnings": [],
            "blocking_questions": [],
            "needs_human_review": True,
            "overall_confidence": 0.5,
            "next_allowed_steps": ["review_candidate_assets", "prepare_asset_commit_dry_run"],
        }
        instruction["output_contract"]["step3a_hard_rules"] = [
            "Return exactly one JSON object matching AiAssetSuggestionDraft.",
            "candidate_assets must contain exactly 1 concrete asset: the primary named system, application, or platform in input.request.",
            "Do not add more than 1 candidate. Never return an empty candidate_assets when the input names a system, application, or platform.",
            "The single candidate must include temporary_id, proposed_name, folder_id, one source_text_reference (short excerpt), rationale, confidence, human_review_status='pending_review', ambiguity_flags, and allowed_next_actions.",
            "Copy folder_id, perimeter_id, and compliance_assessment_id from input.request into source_summary and the candidate.",
            "proposed_asset_type.value must be 'PR' or 'SP'.",
            "allowed_next_actions may only use: accept_for_later_commit, edit_before_commit, reuse_existing_asset, reject, defer.",
            "For an explicitly named concrete system or application use confidence between 0.85 and 0.95.",
            "Keep the whole response short: proposed_description under 10 words, rationale under 12 words, one source_text_reference with an excerpt under 6 words.",
            "Leave duplicate_candidates, ambiguous_candidates, rejected_candidates, warnings, and blocking_questions as empty arrays.",
            "Do not emit create_now or auto_create.",
            "Do not include controls, vulnerabilities, evidence, risk scenarios, or final decisions.",
            "Do not return wrapper keys capability, schema_name, input, output_contract.",
        ]
    elif capability == CAPABILITY_APPLIED_CONTROL_SUGGESTION:
        instruction["output_contract"]["required_top_level_keys"] = ["candidate_applied_controls"]
        instruction["output_contract"]["step4a_minimal_contract"] = {
            "candidate_applied_controls": [
                {
                    "temporary_id": "CTL-CAND-001",
                    "proposed_name": "Multi-Factor Authentication for Remote Access",
                    "proposed_description": "Require MFA for remote access.",
                    "rationale": "Addresses remote access weakness.",
                    "related_weaknesses": ["No MFA for remote access"],
                    "confidence": 0.9,
                },
            ]
        }
        instruction["output_contract"]["step4a_hard_rules"] = [
            "Return exactly one JSON object with only candidate_applied_controls.",
            "Return no more than 4 candidate_applied_controls.",
            "Each candidate may only use: temporary_id, proposed_name, proposed_description, rationale, related_weaknesses, confidence.",
            "Use short text. Do not include ids, asset ids, status fields, actions, source_summary, provider_mode, duplicate_candidates, warnings, or blocking_questions.",
            "Do not include compliance_result, final_result, result, risk_acceptance, risk_decision, audit_closure, close_audit, status, evidence, finding, vulnerability, remediation, risk_scenario, create_now, or auto_create.",
        ]
    else:
        instruction["output_contract"]["json_schema"] = json_schema

    return "\n\n".join(
        [
            system_prompt.strip(),
            "Return one JSON object only. Do not return markdown or explanatory text.",
            json.dumps(instruction, ensure_ascii=False, default=str),
        ]
    )


def _extract_ollama_response_text(response_payload: dict[str, Any]) -> str | None:
    if not isinstance(response_payload, dict):
        return None

    value = response_payload.get("response")
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        return json.dumps(value, ensure_ascii=False)
    if isinstance(value, list):
        return json.dumps(value, ensure_ascii=False)
    return None


def _parse_single_json_object(raw_text: str) -> dict[str, Any]:
    text = (raw_text or "").strip()
    if not text:
        raise AiProviderExecutionError(
            "local_ai_provider_invalid_output",
            "The local AI provider returned an empty response.",
        )

    decoder = json.JSONDecoder()
    try:
        parsed, consumed = decoder.raw_decode(text)
    except json.JSONDecodeError as exc:
        raise AiProviderExecutionError(
            "local_ai_provider_invalid_output",
            "The local AI provider did not return a valid JSON object.",
        ) from exc

    if not isinstance(parsed, dict):
        raise AiProviderExecutionError(
            "local_ai_provider_invalid_output",
            "The local AI provider returned a non-object JSON payload.",
        )

    trailing = text[consumed:].strip()
    if trailing:
        raise AiProviderExecutionError(
            "local_ai_provider_invalid_output",
            "The local AI provider returned extra non-JSON text.",
        )

    return parsed


def get_advisory_provider_selection(config: AdvisoryCapabilityConfig) -> AdvisoryProviderSelection:
    if not is_provider_configured(config):
        return AdvisoryProviderSelection(provider=None, config=config)

    if config.provider != LOCAL_PROVIDER:
        return AdvisoryProviderSelection(provider=None, config=config)

    if config.api_style != LOCAL_AI_STYLE_OLLAMA:
        return AdvisoryProviderSelection(provider=None, config=config)

    provider: AiProvider = LocalAiProvider(
        base_url=config.local_base_url,
        base_url_safe=config.local_base_url_safe,
        base_url_warning=config.local_base_url_warning,
    )
    return AdvisoryProviderSelection(provider=provider, config=config)
