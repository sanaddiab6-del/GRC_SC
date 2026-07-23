from __future__ import annotations

import ipaddress
import os
from dataclasses import dataclass
from urllib.parse import urlparse

from .llm_errors import AdvisoryProviderSelectionError


CAPABILITY_CASE_INTAKE = "case_intake"
CAPABILITY_ASSET_SUGGESTION = "asset_suggestion"
CAPABILITY_APPLIED_CONTROL_SUGGESTION = "applied_control_suggestion"
CAPABILITY_EVIDENCE_FINDING_SUGGESTION = "evidence_finding_suggestion"

SUPPORTED_CAPABILITIES = {
    CAPABILITY_CASE_INTAKE,
    CAPABILITY_ASSET_SUGGESTION,
    CAPABILITY_APPLIED_CONTROL_SUGGESTION,
    CAPABILITY_EVIDENCE_FINDING_SUGGESTION,
}

MODEL_ENV_BY_CAPABILITY = {
    CAPABILITY_CASE_INTAKE: "LOCAL_AI_MODEL_CASE_INTAKE",
    CAPABILITY_ASSET_SUGGESTION: "LOCAL_AI_MODEL_ASSET_SUGGESTION",
    CAPABILITY_APPLIED_CONTROL_SUGGESTION: "LOCAL_AI_MODEL_APPLIED_CONTROL_SUGGESTION",
    CAPABILITY_EVIDENCE_FINDING_SUGGESTION: "LOCAL_AI_MODEL_EVIDENCE_FINDING_SUGGESTION",
}

DEFAULT_PROVIDER = ""
LOCAL_PROVIDER = "local"
LOCAL_AI_STYLE_OLLAMA = "ollama"
DEFAULT_MODEL = ""
DEFAULT_TIMEOUT_SECONDS = 60
DEFAULT_MAX_OUTPUT_TOKENS = 1200
DEFAULT_TEMPERATURE = 0.1

BLOCKED_CLOUD_AI_HOST_SUFFIXES = (
    "openai.com",
    "anthropic.com",
)

BLOCKED_CLOUD_AI_HOSTS = {
    "generativelanguage.googleapis.com",
}


def _is_local_or_private_host(host: str) -> bool:
    normalized = host.strip().lower()
    if normalized == "localhost":
        return True

    try:
        ip_addr = ipaddress.ip_address(normalized)
    except ValueError:
        return False

    return bool(ip_addr.is_loopback or ip_addr.is_private)


def validate_local_base_url(base_url: str) -> tuple[bool, str | None]:
    candidate = (base_url or "").strip()
    if not candidate:
        return False, "LOCAL_AI_BASE_URL is not configured."

    parsed = urlparse(candidate)
    if parsed.scheme not in {"http", "https"}:
        return False, "LOCAL_AI_BASE_URL must use http or https."

    host = (parsed.hostname or "").strip().lower()
    if not host:
        return False, "LOCAL_AI_BASE_URL must include a host."

    if host in BLOCKED_CLOUD_AI_HOSTS or any(
        host == suffix or host.endswith(f".{suffix}")
        for suffix in BLOCKED_CLOUD_AI_HOST_SUFFIXES
    ):
        return False, "LOCAL_AI_BASE_URL host is blocked by local AI safety policy."

    if _is_local_or_private_host(host):
        return True, None

    return False, "LOCAL_AI_BASE_URL must point to localhost or a private network address."


@dataclass(frozen=True)
class AdvisoryCapabilityConfig:
    capability: str
    provider: str
    api_style: str
    model: str
    timeout_seconds: int
    max_output_tokens: int
    temperature: float
    local_base_url: str
    local_base_url_safe: bool
    local_base_url_warning: str | None


def _read_positive_int(env_var_name: str, default: int) -> int:
    raw_value = os.environ.get(env_var_name, str(default)).strip()
    try:
        parsed = int(raw_value)
    except (TypeError, ValueError):
        return default
    return parsed if parsed > 0 else default


def _read_temperature(default: float = DEFAULT_TEMPERATURE) -> float:
    raw_value = os.environ.get("LOCAL_AI_TEMPERATURE", str(default)).strip()
    try:
        parsed = float(raw_value)
    except (TypeError, ValueError):
        return default
    if parsed < 0:
        return 0.0
    if parsed > 2:
        return 2.0
    return parsed


def _resolve_model(capability: str) -> str:
    capability_model_env = MODEL_ENV_BY_CAPABILITY.get(capability)
    if capability_model_env is None:
        raise AdvisoryProviderSelectionError(
            "unsupported_ai_capability",
            f"Unsupported AI capability '{capability}'.",
        )

    capability_model = os.environ.get(capability_model_env, "").strip()
    if capability_model:
        return capability_model

    default_model = os.environ.get("LOCAL_AI_MODEL_DEFAULT", "").strip()
    if default_model:
        return default_model

    return DEFAULT_MODEL


def resolve_advisory_capability_config(capability: str) -> AdvisoryCapabilityConfig:
    if capability not in SUPPORTED_CAPABILITIES:
        raise AdvisoryProviderSelectionError(
            "unsupported_ai_capability",
            f"Unsupported AI capability '{capability}'.",
        )

    provider = os.environ.get("AI_PROVIDER", DEFAULT_PROVIDER).strip().lower()
    api_style = os.environ.get("LOCAL_AI_API_STYLE", LOCAL_AI_STYLE_OLLAMA).strip().lower()
    model = _resolve_model(capability)
    timeout_seconds = _read_positive_int("LOCAL_AI_TIMEOUT_SECONDS", DEFAULT_TIMEOUT_SECONDS)
    max_output_tokens = _read_positive_int("LOCAL_AI_MAX_OUTPUT_TOKENS", DEFAULT_MAX_OUTPUT_TOKENS)
    temperature = _read_temperature(DEFAULT_TEMPERATURE)
    local_base_url = os.environ.get("LOCAL_AI_BASE_URL", "").strip()
    local_base_url_safe, local_base_url_warning = validate_local_base_url(local_base_url)

    return AdvisoryCapabilityConfig(
        capability=capability,
        provider=provider,
        api_style=api_style,
        model=model,
        timeout_seconds=timeout_seconds,
        max_output_tokens=max_output_tokens,
        temperature=temperature,
        local_base_url=local_base_url,
        local_base_url_safe=local_base_url_safe,
        local_base_url_warning=local_base_url_warning,
    )


def is_provider_configured(config: AdvisoryCapabilityConfig) -> bool:
    return (
        config.provider == LOCAL_PROVIDER
        and config.api_style == LOCAL_AI_STYLE_OLLAMA
        and bool(config.local_base_url)
        and bool(config.model)
    )
