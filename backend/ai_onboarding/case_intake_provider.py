from __future__ import annotations

import copy
from typing import Any, Protocol

from .case_intake_serializers import CANONICAL_PLATFORM_ENTITIES, SCHEMA_VERSION
from .llm_config import CAPABILITY_CASE_INTAKE, resolve_advisory_capability_config
from .llm_errors import AiProviderExecutionError, AiProviderOutputValidationError
from .llm_prompts import get_system_prompt
from .llm_provider import get_advisory_provider_selection
from .llm_schemas import (
    ALLOWED_TOP_LEVEL_KEYS,
    TOP_LEVEL_REQUIRED_KEYS,
    get_capability_json_schema,
    get_capability_schema_name,
    validate_provider_output_schema,
)


class CaseIntakeProviderError(Exception):
    def __init__(
        self,
        error_code: str,
        detail: str,
        *,
        allow_fallback: bool = False,
        provider_mode: str | None = None,
    ):
        super().__init__(detail)
        self.status_code = 422
        self.error_code = error_code
        self.detail = detail
        self.allow_fallback = allow_fallback
        self.provider_mode = provider_mode

    def to_response(self) -> dict[str, Any]:
        response = {
            "error_code": self.error_code,
            "detail": self.detail,
        }
        if self.provider_mode:
            response["provider_mode"] = self.provider_mode
        return response


class CaseIntakeProvider(Protocol):
    available: bool

    def build_case_intake_draft(self, request_payload: dict[str, Any]) -> dict[str, Any]:
        ...


class AdvisoryCaseIntakeProvider:
    def __init__(self):
        capability_config = resolve_advisory_capability_config(CAPABILITY_CASE_INTAKE)
        selection = get_advisory_provider_selection(capability_config)
        self._provider = selection.provider
        self._config = selection.config
        self.available = self._provider is not None

    def build_case_intake_draft(self, request_payload: dict[str, Any]) -> dict[str, Any]:
        if self._provider is None:
            raise CaseIntakeProviderError(
                "local_provider_not_configured",
                "The local AI provider is not configured for Step 1.",
                allow_fallback=True,
            )

        payload = {
            "schema_version": SCHEMA_VERSION,
            "allowed_platform_entities": list(CANONICAL_PLATFORM_ENTITIES),
            "request": request_payload,
            "response_requirements": {
                "draft_type": "AiCaseIntakeDraft",
                "needs_human_review": True,
                "advisory_only": True,
            },
        }

        try:
            result = self._provider.generate_structured(
                capability=CAPABILITY_CASE_INTAKE,
                model=self._config.model,
                system_prompt=get_system_prompt(CAPABILITY_CASE_INTAKE),
                user_payload=payload,
                json_schema=get_capability_json_schema(CAPABILITY_CASE_INTAKE),
                timeout_seconds=self._config.timeout_seconds,
                max_output_tokens=self._config.max_output_tokens,
                temperature=self._config.temperature,
                schema_name=get_capability_schema_name(CAPABILITY_CASE_INTAKE),
            )
        except AiProviderExecutionError as exc:
            if exc.error_code == "local_ai_provider_invalid_output":
                raise CaseIntakeProviderError(
                    exc.error_code,
                    exc.detail,
                    allow_fallback=False,
                    provider_mode="local_provider_error_blocked",
                ) from exc
            raise CaseIntakeProviderError(
                exc.error_code,
                exc.detail,
                allow_fallback=True,
                provider_mode="local_provider_error_fallback",
            ) from exc

        if not isinstance(result, dict):
            raise CaseIntakeProviderError(
                "local_ai_provider_invalid_output",
                "The local AI provider did not return valid JSON output.",
                provider_mode="local_provider_error_blocked",
            )

        result = _normalize_case_intake_top_level_shape(result)

        try:
            validate_provider_output_schema(
                CAPABILITY_CASE_INTAKE,
                result,
                strict_mode=bool(request_payload.get("strict_mode", True)),
            )
        except AiProviderOutputValidationError as exc:
            raise CaseIntakeProviderError(
                exc.error_code,
                exc.detail,
                provider_mode="local_provider_error_blocked",
            ) from exc

        return result


def get_case_intake_provider() -> CaseIntakeProvider | None:
    provider = AdvisoryCaseIntakeProvider()
    return provider if provider.available else None


def _normalize_case_intake_top_level_shape(payload: dict[str, Any]) -> dict[str, Any]:
    allowed = ALLOWED_TOP_LEVEL_KEYS[CAPABILITY_CASE_INTAKE]
    normalized: dict[str, Any] = {
        key: payload[key]
        for key in allowed
        if key in payload
    }

    defaults: dict[str, Any] = {
        "draft_type": "AiCaseIntakeDraft",
        "schema_version": SCHEMA_VERSION,
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

    for key in TOP_LEVEL_REQUIRED_KEYS[CAPABILITY_CASE_INTAKE]:
        if key not in normalized:
            normalized[key] = copy.deepcopy(defaults[key])

    normalized["draft_type"] = "AiCaseIntakeDraft"
    normalized["schema_version"] = SCHEMA_VERSION
    normalized["needs_human_review"] = True

    source_summary = normalized.get("source_summary")
    if not isinstance(source_summary, dict):
        source_summary = copy.deepcopy(defaults["source_summary"])
    parser_notes = source_summary.get("parser_notes")
    if not isinstance(parser_notes, list):
        source_summary["parser_notes"] = []
    normalized["source_summary"] = source_summary

    return normalized