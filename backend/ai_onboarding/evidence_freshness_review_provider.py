from __future__ import annotations

from typing import Any, Protocol

from .evidence_freshness_review_guardrails import validate_provider_output_guardrails
from .evidence_freshness_review_serializers import SCHEMA_VERSION
from .llm_config import CAPABILITY_EVIDENCE_FRESHNESS_REVIEW, resolve_advisory_capability_config
from .llm_errors import AiProviderExecutionError
from .llm_prompts import get_system_prompt
from .llm_provider import get_advisory_provider_selection


SCHEMA_NAME = "evidence_freshness_review_judgement"

# One evidence item, one judgement: no array indices to keep in sync, so there is nothing
# for the model to reorder, drop, or misattribute.
PROVIDER_OUTPUT_JSON_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": True,
    "required": ["freshness_status", "confidence", "explanation", "recommended_action"],
    "properties": {
        "freshness_status": {
            "type": "string",
            "enum": [
                "CURRENT",
                "REVIEW_RECOMMENDED",
                "POSSIBLY_OUTDATED",
                "INSUFFICIENT_CONTEXT",
            ],
        },
        "confidence": {"type": "number"},
        "explanation": {"type": "string"},
        "concerns": {"type": "array", "items": {"type": "string"}},
        "recommended_action": {"type": "string"},
    },
}


class EvidenceFreshnessReviewProviderError(Exception):
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


class EvidenceFreshnessReviewProvider(Protocol):
    available: bool

    def judge_evidence_freshness(self, evidence_context: dict[str, Any]) -> dict[str, Any]:
        ...


def _build_prompt(evidence_context: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    system_prompt = get_system_prompt(CAPABILITY_EVIDENCE_FRESHNESS_REVIEW)
    payload = {
        "schema_version": SCHEMA_VERSION,
        "request": {"evidence": evidence_context},
    }
    return system_prompt, payload


class AdvisoryEvidenceFreshnessReviewProvider:
    def __init__(self):
        capability_config = resolve_advisory_capability_config(
            CAPABILITY_EVIDENCE_FRESHNESS_REVIEW
        )
        selection = get_advisory_provider_selection(capability_config)
        self._provider = selection.provider
        self._config = selection.config
        self.available = self._provider is not None

    def judge_evidence_freshness(self, evidence_context: dict[str, Any]) -> dict[str, Any]:
        if self._provider is None:
            raise EvidenceFreshnessReviewProviderError(
                "local_provider_not_configured",
                "The local AI provider is not configured for evidence freshness review.",
                allow_fallback=True,
            )

        system_prompt, payload = _build_prompt(evidence_context)
        try:
            result = self._provider.generate_structured(
                capability=CAPABILITY_EVIDENCE_FRESHNESS_REVIEW,
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
                raise EvidenceFreshnessReviewProviderError(
                    exc.error_code,
                    exc.detail,
                    allow_fallback=False,
                    provider_mode="local_provider_error_blocked",
                ) from exc
            raise EvidenceFreshnessReviewProviderError(
                exc.error_code,
                exc.detail,
                allow_fallback=True,
                provider_mode="local_provider_error_fallback",
            ) from exc

        if not isinstance(result, dict):
            raise EvidenceFreshnessReviewProviderError(
                "local_ai_provider_invalid_output",
                "The local AI provider did not return valid JSON output.",
                allow_fallback=False,
                provider_mode="local_provider_error_blocked",
            )

        # Safety-relevant: never silently substituted with a fallback (allow_fallback=False
        # is not requested here), so write-implying or out-of-scope output fails loudly.
        try:
            validate_provider_output_guardrails(result)
        except Exception as exc:  # EvidenceFreshnessReviewValidationError
            raise EvidenceFreshnessReviewProviderError(
                getattr(exc, "error_code", "ai_evidence_freshness_review_guardrails_failed"),
                getattr(exc, "detail", str(exc)),
                allow_fallback=False,
                provider_mode="local_provider_error_blocked",
            ) from exc

        return result


def get_evidence_freshness_review_provider() -> EvidenceFreshnessReviewProvider | None:
    provider = AdvisoryEvidenceFreshnessReviewProvider()
    return provider if provider.available else None
