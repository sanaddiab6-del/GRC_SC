from __future__ import annotations

from typing import Any, Protocol

from .llm_config import (
    CAPABILITY_RISK_SCENARIO_SUGGESTION,
    resolve_advisory_capability_config,
)
from .llm_errors import AiProviderExecutionError
from .llm_prompts import get_system_prompt
from .llm_provider import get_advisory_provider_selection
from .risk_scenario_suggestion_guardrails import FORBIDDEN_KEYS
from .risk_scenario_suggestion_serializers import (
    IMPACT_CHOICES,
    LIKELIHOOD_CHOICES,
    MAX_RISK_SCENARIOS,
    RISK_LEVEL_CHOICES,
    SCHEMA_VERSION,
)


SCHEMA_NAME = "risk_scenario_suggestion_draft"

# Minimal contract requested from the local provider. The service normalizes harmless
# formatting issues and the Step 8A guardrails validate the substance of every scenario.
PROVIDER_OUTPUT_JSON_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": True,
    "required": ["risk_scenarios"],
    "properties": {
        "risk_scenarios": {
            "type": "array",
            "maxItems": MAX_RISK_SCENARIOS,
            "items": {
                "type": "object",
                "required": [
                    "title",
                    "description",
                    "threat",
                    "vulnerability",
                    "impact_description",
                    "likelihood",
                    "impact",
                    "risk_level",
                    "rationale",
                    "recommended_next_steps",
                    "confidence",
                    "review_status",
                ],
                "properties": {
                    "temporary_id": {"type": "string"},
                    "title": {"type": "string"},
                    "description": {"type": "string"},
                    "asset_reference": {"type": "string"},
                    "asset_title": {"type": "string"},
                    "linked_finding_reference": {"type": "string"},
                    "linked_finding_title": {"type": "string"},
                    "linked_applied_control_reference": {"type": "string"},
                    "linked_applied_control_title": {"type": "string"},
                    "linked_remediation_action_reference": {"type": "string"},
                    "linked_remediation_action_title": {"type": "string"},
                    "linked_framework_control_reference": {"type": "string"},
                    "linked_framework_control_code": {"type": "string"},
                    "linked_framework_control_title": {"type": "string"},
                    "threat": {"type": "string"},
                    "vulnerability": {"type": "string"},
                    "impact_description": {"type": "string"},
                    "likelihood": {"type": "string", "enum": list(LIKELIHOOD_CHOICES)},
                    "impact": {"type": "string", "enum": list(IMPACT_CHOICES)},
                    "risk_level": {"type": "string", "enum": list(RISK_LEVEL_CHOICES)},
                    "rationale": {"type": "string"},
                    "recommended_next_steps": {"type": "array", "items": {"type": "string"}},
                    "confidence": {"type": "number"},
                    "review_status": {"type": "string", "enum": ["pending_review"]},
                },
            },
        },
        "ambiguity_flags": {"type": "array"},
    },
}


class RiskScenarioSuggestionProviderError(Exception):
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


class RiskScenarioSuggestionProvider(Protocol):
    available: bool

    def build_risk_scenario_suggestion_draft(
        self, request_payload: dict[str, Any]
    ) -> dict[str, Any]:
        ...


def _build_prompt(request_payload: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    system_prompt = get_system_prompt(CAPABILITY_RISK_SCENARIO_SUGGESTION)
    payload = {
        "schema_version": SCHEMA_VERSION,
        "request": request_payload,
    }
    return system_prompt, payload


def _validate_provider_output(result: dict[str, Any]) -> None:
    """Reject provider output that would imply a write, an approval, or a risk decision.

    Shape and value validation (enums, confidence range, required fields, review_status)
    belongs to the Step 8A guardrails so every violation is reported through a single
    error contract.
    """

    def _walk(value: Any):
        if isinstance(value, dict):
            for child_key, child in value.items():
                yield child_key
                yield from _walk(child)
        elif isinstance(value, list):
            for item in value:
                yield from _walk(item)

    errors = [key for key in _walk(result) if key in FORBIDDEN_KEYS]
    if errors:
        raise RiskScenarioSuggestionProviderError(
            "local_ai_provider_invalid_output",
            "Configured local AI provider output failed Step 8A schema safety checks.",
            allow_fallback=False,
            provider_mode="local_provider_error_blocked",
        )


class AdvisoryRiskScenarioSuggestionProvider:
    def __init__(self):
        capability_config = resolve_advisory_capability_config(
            CAPABILITY_RISK_SCENARIO_SUGGESTION
        )
        selection = get_advisory_provider_selection(capability_config)
        self._provider = selection.provider
        self._config = selection.config
        self.available = self._provider is not None

    def build_risk_scenario_suggestion_draft(
        self, request_payload: dict[str, Any]
    ) -> dict[str, Any]:
        if self._provider is None:
            raise RiskScenarioSuggestionProviderError(
                "local_provider_not_configured",
                "The local AI provider is not configured for Step 8A.",
                allow_fallback=True,
            )

        system_prompt, payload = _build_prompt(request_payload)
        try:
            result = self._provider.generate_structured(
                capability=CAPABILITY_RISK_SCENARIO_SUGGESTION,
                model=self._config.model,
                system_prompt=system_prompt,
                user_payload=payload,
                json_schema=PROVIDER_OUTPUT_JSON_SCHEMA,
                timeout_seconds=self._config.timeout_seconds,
                max_output_tokens=self._config.max_output_tokens,
                temperature=self._config.temperature,
                schema_name=SCHEMA_NAME,
            )
        except AiProviderExecutionError as exc:
            if exc.error_code == "local_ai_provider_invalid_output":
                raise RiskScenarioSuggestionProviderError(
                    exc.error_code,
                    exc.detail,
                    allow_fallback=False,
                    provider_mode="local_provider_error_blocked",
                ) from exc
            raise RiskScenarioSuggestionProviderError(
                exc.error_code,
                exc.detail,
                allow_fallback=True,
                provider_mode="local_provider_error_fallback",
            ) from exc

        if not isinstance(result, dict):
            raise RiskScenarioSuggestionProviderError(
                "local_ai_provider_invalid_output",
                "The local AI provider did not return valid JSON output.",
                provider_mode="local_provider_error_blocked",
            )

        _validate_provider_output(result)
        return result


def get_risk_scenario_suggestion_provider() -> RiskScenarioSuggestionProvider | None:
    provider = AdvisoryRiskScenarioSuggestionProvider()
    return provider if provider.available else None
