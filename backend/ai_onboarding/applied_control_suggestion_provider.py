from __future__ import annotations

from typing import Any, Protocol

from .applied_control_suggestion_serializers import SCHEMA_VERSION
from .llm_config import (
    CAPABILITY_APPLIED_CONTROL_SUGGESTION,
    resolve_advisory_capability_config,
)
from .llm_errors import AiProviderExecutionError, AiProviderOutputValidationError
from .llm_prompts import get_system_prompt
from .llm_provider import get_advisory_provider_selection
from .llm_schemas import (
    get_capability_json_schema,
    get_capability_schema_name,
    validate_provider_output_schema,
)


class AppliedControlSuggestionProviderError(Exception):
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


class AppliedControlSuggestionProvider(Protocol):
    available: bool

    def build_applied_control_suggestion_draft(self, request_payload: dict[str, Any]) -> dict[str, Any]:
        ...


def _build_applied_control_suggestion_prompt(request_payload: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    system_prompt = get_system_prompt(CAPABILITY_APPLIED_CONTROL_SUGGESTION)
    payload = {
        "schema_version": SCHEMA_VERSION,
        "request": request_payload,
    }
    return system_prompt, payload


class AdvisoryAppliedControlSuggestionProvider:
    def __init__(self):
        capability_config = resolve_advisory_capability_config(
            CAPABILITY_APPLIED_CONTROL_SUGGESTION
        )
        selection = get_advisory_provider_selection(capability_config)
        self._provider = selection.provider
        self._config = selection.config
        self.available = self._provider is not None

    def build_applied_control_suggestion_draft(self, request_payload: dict[str, Any]) -> dict[str, Any]:
        if self._provider is None:
            raise AppliedControlSuggestionProviderError(
                "local_provider_not_configured",
                "The local AI provider is not configured for Step 4A.",
                allow_fallback=True,
            )

        system_prompt, payload = _build_applied_control_suggestion_prompt(request_payload)
        try:
            result = self._provider.generate_structured(
                capability=CAPABILITY_APPLIED_CONTROL_SUGGESTION,
                model=self._config.model,
                system_prompt=system_prompt,
                user_payload=payload,
                json_schema=get_capability_json_schema(CAPABILITY_APPLIED_CONTROL_SUGGESTION),
                timeout_seconds=self._config.timeout_seconds,
                max_output_tokens=self._config.max_output_tokens,
                temperature=self._config.temperature,
                schema_name=get_capability_schema_name(CAPABILITY_APPLIED_CONTROL_SUGGESTION),
            )
        except AiProviderExecutionError as exc:
            if exc.error_code == "local_ai_provider_invalid_output":
                raise AppliedControlSuggestionProviderError(
                    exc.error_code,
                    exc.detail,
                    allow_fallback=False,
                    provider_mode="local_provider_error_blocked",
                ) from exc
            raise AppliedControlSuggestionProviderError(
                exc.error_code,
                exc.detail,
                allow_fallback=True,
                provider_mode="local_provider_error_fallback",
            ) from exc

        if not isinstance(result, dict):
            raise AppliedControlSuggestionProviderError(
                "local_ai_provider_invalid_output",
                "The local AI provider did not return valid JSON output.",
                provider_mode="local_provider_error_blocked",
            )

        try:
            validate_provider_output_schema(
                CAPABILITY_APPLIED_CONTROL_SUGGESTION,
                result,
                strict_mode=bool(request_payload.get("strict_mode", True)),
            )
        except AiProviderOutputValidationError as exc:
            raise AppliedControlSuggestionProviderError(
                exc.error_code,
                exc.detail,
                provider_mode="local_provider_error_blocked",
            ) from exc

        return result


def get_applied_control_suggestion_provider() -> AppliedControlSuggestionProvider | None:
    provider = AdvisoryAppliedControlSuggestionProvider()
    return provider if provider.available else None