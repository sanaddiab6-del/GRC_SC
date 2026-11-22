from __future__ import annotations

from typing import Any, Protocol

from .audit_readiness_suggestion_guardrails import FORBIDDEN_KEYS
from .audit_readiness_suggestion_serializers import (
    MAX_READINESS_SCORE,
    MAX_SUMMARY_LIST_ITEMS,
    MIN_READINESS_SCORE,
    READINESS_STATUS_CHOICES,
    SCHEMA_VERSION,
)
from .llm_config import (
    CAPABILITY_AUDIT_READINESS_SUGGESTION,
    resolve_advisory_capability_config,
)
from .llm_errors import AiProviderExecutionError
from .llm_prompts import get_system_prompt
from .llm_provider import get_advisory_provider_selection


SCHEMA_NAME = "audit_readiness_suggestion_draft"


def _string_list_schema() -> dict[str, Any]:
    return {
        "type": "array",
        "maxItems": MAX_SUMMARY_LIST_ITEMS,
        "items": {"type": "string"},
    }


# Minimal contract requested from the local provider. The service normalizes harmless
# formatting issues and the Step 10A guardrails validate the substance of the summary.
PROVIDER_OUTPUT_JSON_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": True,
    "required": ["readiness_status", "readiness_score", "summary"],
    "properties": {
        "readiness_status": {"type": "string", "enum": list(READINESS_STATUS_CHOICES)},
        "readiness_score": {
            "type": "integer",
            "minimum": MIN_READINESS_SCORE,
            "maximum": MAX_READINESS_SCORE,
        },
        "summary": {"type": "string"},
        "ready_items": _string_list_schema(),
        "missing_evidence": _string_list_schema(),
        "open_findings": _string_list_schema(),
        "open_risks": _string_list_schema(),
        "blocked_controls": _string_list_schema(),
        "recommended_next_steps": _string_list_schema(),
        "priority_actions": _string_list_schema(),
        "ambiguity_flags": {"type": "array"},
        "review_status": {"type": "string", "enum": ["pending_review"]},
    },
}


class AuditReadinessSuggestionProviderError(Exception):
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


class AuditReadinessSuggestionProvider(Protocol):
    available: bool

    def build_audit_readiness_suggestion_draft(
        self, request_payload: dict[str, Any]
    ) -> dict[str, Any]:
        ...


def _build_prompt(request_payload: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    system_prompt = get_system_prompt(CAPABILITY_AUDIT_READINESS_SUGGESTION)
    payload = {
        "schema_version": SCHEMA_VERSION,
        "request": request_payload,
    }
    return system_prompt, payload


def _validate_provider_output(result: dict[str, Any]) -> None:
    """Reject provider output that would imply a write, an approval, or a closure."""

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
        raise AuditReadinessSuggestionProviderError(
            "local_ai_provider_invalid_output",
            "Configured local AI provider output failed Step 10A schema safety checks.",
            allow_fallback=False,
            provider_mode="local_provider_error_blocked",
        )


class AdvisoryAuditReadinessSuggestionProvider:
    def __init__(self):
        capability_config = resolve_advisory_capability_config(
            CAPABILITY_AUDIT_READINESS_SUGGESTION
        )
        selection = get_advisory_provider_selection(capability_config)
        self._provider = selection.provider
        self._config = selection.config
        self.available = self._provider is not None

    def build_audit_readiness_suggestion_draft(
        self, request_payload: dict[str, Any]
    ) -> dict[str, Any]:
        if self._provider is None:
            raise AuditReadinessSuggestionProviderError(
                "local_provider_not_configured",
                "The local AI provider is not configured for Step 10A.",
                allow_fallback=True,
            )

        system_prompt, payload = _build_prompt(request_payload)
        try:
            result = self._provider.generate_structured(
                capability=CAPABILITY_AUDIT_READINESS_SUGGESTION,
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
                raise AuditReadinessSuggestionProviderError(
                    exc.error_code,
                    exc.detail,
                    allow_fallback=False,
                    provider_mode="local_provider_error_blocked",
                ) from exc
            raise AuditReadinessSuggestionProviderError(
                exc.error_code,
                exc.detail,
                allow_fallback=True,
                provider_mode="local_provider_error_fallback",
            ) from exc

        if not isinstance(result, dict):
            raise AuditReadinessSuggestionProviderError(
                "local_ai_provider_invalid_output",
                "The local AI provider did not return valid JSON output.",
                provider_mode="local_provider_error_blocked",
            )

        _validate_provider_output(result)
        return result


def get_audit_readiness_suggestion_provider() -> AuditReadinessSuggestionProvider | None:
    provider = AdvisoryAuditReadinessSuggestionProvider()
    return provider if provider.available else None
