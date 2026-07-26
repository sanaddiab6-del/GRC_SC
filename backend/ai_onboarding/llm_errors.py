from __future__ import annotations

from typing import Any


class AiProviderError(Exception):
    """Base error for shared AI provider behavior."""

    def __init__(self, error_code: str, detail: str):
        super().__init__(detail)
        self.error_code = error_code
        self.detail = detail


class AiProviderExecutionError(AiProviderError):
    """Raised when the provider call fails due to runtime or transport issues."""


class AiProviderOutputValidationError(AiProviderError):
    """Raised when provider output fails schema-level safety checks."""

    def __init__(self, error_code: str, detail: str, *, errors: list[str] | None = None):
        super().__init__(error_code, detail)
        self.errors = errors or []


class AdvisoryProviderSelectionError(AiProviderError):
    """Raised when provider selection receives an unsupported capability or provider."""


def build_sanitized_provider_detail(exc: Exception) -> str:
    """
    Return a stable, non-secret-bearing provider error message.

    The original exception text is intentionally ignored to prevent leaking API keys,
    tokens, raw provider payloads, or transport internals.
    """

    if isinstance(exc, TimeoutError):
        return "The configured AI provider timed out before returning a response."
    return "The configured AI provider could not be reached or returned an unreadable response."


def to_serializable_errors(errors: list[str] | dict[str, Any] | None) -> list[str] | dict[str, Any]:
    if errors is None:
        return []
    return errors
