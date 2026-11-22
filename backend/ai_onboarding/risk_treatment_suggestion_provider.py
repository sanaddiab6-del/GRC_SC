from __future__ import annotations

from typing import Any, Protocol

from .llm_config import CAPABILITY_RISK_TREATMENT_SUGGESTION, resolve_advisory_capability_config
from .llm_errors import AiProviderExecutionError
from .llm_prompts import get_system_prompt
from .llm_provider import get_advisory_provider_selection
from .risk_treatment_suggestion_guardrails import (
    RiskTreatmentSuggestionValidationError,
    validate_provider_output_guardrails,
)
from .risk_treatment_suggestion_serializers import (
    ACTION_PRIORITY_CHOICES,
    MAX_CONSIDERATIONS,
    MAX_MITIGATING_ACTIONS,
    SCHEMA_VERSION,
    SUGGESTABLE_TREATMENT_CHOICES,
)


SCHEMA_NAME = "risk_treatment_suggestion"

# One risk scenario, one suggestion. No identifiers are requested: the server already knows
# which scenario it is reviewing and attaches that itself.
PROVIDER_OUTPUT_JSON_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "required": ["suggested_treatment", "confidence", "rationale"],
    "properties": {
        "suggested_treatment": {"type": "string", "enum": list(SUGGESTABLE_TREATMENT_CHOICES)},
        "confidence": {"type": "number"},
        "rationale": {"type": "string"},
        "mitigating_actions": {
            "type": "array",
            "maxItems": MAX_MITIGATING_ACTIONS,
            "items": {
                "type": "object",
                "required": ["title", "description", "priority"],
                "properties": {
                    "title": {"type": "string"},
                    "description": {"type": "string"},
                    "priority": {"type": "string", "enum": list(ACTION_PRIORITY_CHOICES)},
                },
            },
        },
        "considerations": {
            "type": "array",
            "maxItems": MAX_CONSIDERATIONS,
            "items": {"type": "string"},
        },
    },
}


class RiskTreatmentSuggestionProviderError(Exception):
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
        response = {"error_code": self.error_code, "detail": self.detail}
        if self.provider_mode:
            response["provider_mode"] = self.provider_mode
        return response


class RiskTreatmentSuggestionProvider(Protocol):
    available: bool

    def suggest_treatment(self, risk_context: dict[str, Any]) -> dict[str, Any]:
        ...


def _build_prompt(risk_context: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    system_prompt = get_system_prompt(CAPABILITY_RISK_TREATMENT_SUGGESTION)
    payload = {
        "schema_version": SCHEMA_VERSION,
        "request": {
            "allowed_treatments": list(SUGGESTABLE_TREATMENT_CHOICES),
            "allowed_action_priorities": list(ACTION_PRIORITY_CHOICES),
            "risk_scenario": risk_context,
        },
    }
    return system_prompt, payload


class AdvisoryRiskTreatmentSuggestionProvider:
    def __init__(self):
        capability_config = resolve_advisory_capability_config(
            CAPABILITY_RISK_TREATMENT_SUGGESTION
        )
        selection = get_advisory_provider_selection(capability_config)
        self._provider = selection.provider
        self._config = selection.config
        self.available = self._provider is not None

    def suggest_treatment(self, risk_context: dict[str, Any]) -> dict[str, Any]:
        if self._provider is None:
            raise RiskTreatmentSuggestionProviderError(
                "local_provider_not_configured",
                "The local AI provider is not configured for risk treatment suggestions.",
                allow_fallback=True,
            )

        system_prompt, payload = _build_prompt(risk_context)
        try:
            result = self._provider.generate_structured(
                capability=CAPABILITY_RISK_TREATMENT_SUGGESTION,
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
            # Unreadable output is treated as untrusted and blocked; transport failures
            # (unreachable, timeout, HTTP error) degrade to the safe fallback. Either way the
            # detail is the already-sanitized message from llm_errors, never the raw exception.
            blocked = exc.error_code == "local_ai_provider_invalid_output"
            raise RiskTreatmentSuggestionProviderError(
                exc.error_code,
                exc.detail,
                allow_fallback=not blocked,
                provider_mode=(
                    "local_provider_error_blocked" if blocked else "local_provider_error_fallback"
                ),
            ) from exc

        try:
            validate_provider_output_guardrails(result)
        except RiskTreatmentSuggestionValidationError as exc:
            raise RiskTreatmentSuggestionProviderError(
                exc.error_code,
                exc.detail,
                allow_fallback=False,
                provider_mode="local_provider_error_blocked",
            ) from exc

        return result


def get_risk_treatment_suggestion_provider() -> RiskTreatmentSuggestionProvider | None:
    provider = AdvisoryRiskTreatmentSuggestionProvider()
    return provider if provider.available else None
