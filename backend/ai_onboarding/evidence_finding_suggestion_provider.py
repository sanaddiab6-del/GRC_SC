from __future__ import annotations

from typing import Any, Protocol

from .evidence_finding_suggestion_guardrails import FORBIDDEN_KEYS
from .evidence_finding_suggestion_serializers import SCHEMA_VERSION
from .llm_config import (
    CAPABILITY_EVIDENCE_FINDING_SUGGESTION,
    resolve_advisory_capability_config,
)
from .llm_errors import AiProviderExecutionError
from .llm_prompts import get_system_prompt
from .llm_provider import get_advisory_provider_selection


SCHEMA_NAME = "evidence_finding_suggestion_draft"

# Minimal contract requested from the local provider. The service enriches any
# missing per-item and top-level fields before contract validation.
PROVIDER_OUTPUT_JSON_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": True,
    "required": [
        "evidence_requests",
        "audit_questions",
        "preliminary_findings",
    ],
    "properties": {
        "evidence_requests": {"type": "array"},
        "audit_questions": {"type": "array"},
        "preliminary_findings": {"type": "array"},
    },
}


class EvidenceFindingSuggestionProviderError(Exception):
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


class EvidenceFindingSuggestionProvider(Protocol):
    available: bool

    def build_evidence_finding_suggestion_draft(
        self, request_payload: dict[str, Any]
    ) -> dict[str, Any]:
        ...


def _build_prompt(request_payload: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    system_prompt = get_system_prompt(CAPABILITY_EVIDENCE_FINDING_SUGGESTION)
    payload = {
        "schema_version": SCHEMA_VERSION,
        "request": request_payload,
    }
    return system_prompt, payload


def _validate_provider_output(result: dict[str, Any]) -> None:
    errors: list[str] = []
    for key in ("evidence_requests", "audit_questions", "preliminary_findings"):
        if not isinstance(result.get(key), list):
            errors.append(f"{key} must be an array.")

    def _walk(value: Any):
        if isinstance(value, dict):
            for child_key, child in value.items():
                yield child_key
                yield from _walk(child)
        elif isinstance(value, list):
            for item in value:
                yield from _walk(item)

    for key in _walk(result):
        if key in FORBIDDEN_KEYS:
            errors.append(f"Forbidden key found in provider output: {key}")

    if errors:
        raise EvidenceFindingSuggestionProviderError(
            "local_ai_provider_invalid_output",
            "Configured local AI provider output failed Step 5A schema safety checks.",
            allow_fallback=False,
            provider_mode="local_provider_error_blocked",
        )


class AdvisoryEvidenceFindingSuggestionProvider:
    def __init__(self):
        capability_config = resolve_advisory_capability_config(
            CAPABILITY_EVIDENCE_FINDING_SUGGESTION
        )
        selection = get_advisory_provider_selection(capability_config)
        self._provider = selection.provider
        self._config = selection.config
        self.available = self._provider is not None

    def build_evidence_finding_suggestion_draft(
        self, request_payload: dict[str, Any]
    ) -> dict[str, Any]:
        if self._provider is None:
            raise EvidenceFindingSuggestionProviderError(
                "local_provider_not_configured",
                "The local AI provider is not configured for Step 5A.",
                allow_fallback=True,
            )

        system_prompt, payload = _build_prompt(request_payload)
        try:
            result = self._provider.generate_structured(
                capability=CAPABILITY_EVIDENCE_FINDING_SUGGESTION,
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
                raise EvidenceFindingSuggestionProviderError(
                    exc.error_code,
                    exc.detail,
                    allow_fallback=False,
                    provider_mode="local_provider_error_blocked",
                ) from exc
            raise EvidenceFindingSuggestionProviderError(
                exc.error_code,
                exc.detail,
                allow_fallback=True,
                provider_mode="local_provider_error_fallback",
            ) from exc

        if not isinstance(result, dict):
            raise EvidenceFindingSuggestionProviderError(
                "local_ai_provider_invalid_output",
                "The local AI provider did not return valid JSON output.",
                provider_mode="local_provider_error_blocked",
            )

        _validate_provider_output(result)
        return result


def get_evidence_finding_suggestion_provider() -> EvidenceFindingSuggestionProvider | None:
    provider = AdvisoryEvidenceFindingSuggestionProvider()
    return provider if provider.available else None
