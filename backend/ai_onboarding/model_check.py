"""Check that the local AI runtime serves the team-standard pinned model.

Warning-only by design: a mismatch is reported, never blocks the platform.
Run with `python manage.py check_ai_model` (also runs at backend startup).
"""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from dataclasses import dataclass

from .llm_config import (
    LOCAL_AI_STYLE_OLLAMA,
    LOCAL_PROVIDER,
    MODEL_ENV_BY_CAPABILITY,
    PINNED_MODEL,
    PINNED_MODEL_DIGEST,
    PINNED_OLLAMA_VERSION,
    validate_local_base_url,
)

OK = "OK"
WARN = "WARN"
REQUEST_TIMEOUT_SECONDS = 5
EXTRA_MODEL_ENVS = ("LOCAL_AI_MODEL_DEFAULT", "LOCAL_AI_MODEL_ONBOARDING")


@dataclass(frozen=True)
class CheckResult:
    level: str
    message: str


def _get_json(url: str) -> dict:
    with urllib.request.urlopen(url, timeout=REQUEST_TIMEOUT_SECONDS) as response:
        return json.loads(response.read().decode("utf-8"))


def _configured_models(environ) -> dict[str, str]:
    names = [*EXTRA_MODEL_ENVS, *MODEL_ENV_BY_CAPABILITY.values()]
    return {name: environ[name].strip() for name in names if environ.get(name, "").strip()}


def check_ai_model(environ=None, fetch_json=_get_json) -> list[CheckResult]:
    environ = os.environ if environ is None else environ
    results: list[CheckResult] = []

    provider = environ.get("AI_PROVIDER", "").strip().lower()
    if provider != LOCAL_PROVIDER:
        return [CheckResult(WARN, "AI is disabled (AI_PROVIDER is not 'local'); nothing to check.")]
    api_style = environ.get("LOCAL_AI_API_STYLE", LOCAL_AI_STYLE_OLLAMA).strip().lower()
    if api_style != LOCAL_AI_STYLE_OLLAMA:
        results.append(CheckResult(WARN, f"LOCAL_AI_API_STYLE is '{api_style}', expected 'ollama'."))

    for env_name, model in _configured_models(environ).items():
        if model != PINNED_MODEL:
            results.append(CheckResult(
                WARN, f"{env_name}={model} overrides the team model {PINNED_MODEL}."))

    base_url = environ.get("LOCAL_AI_BASE_URL", "").strip()
    safe, reason = validate_local_base_url(base_url)
    if not safe:
        results.append(CheckResult(WARN, f"Cannot check Ollama: {reason}"))
        return results
    base_url = base_url.rstrip("/")

    try:
        version = str(fetch_json(f"{base_url}/api/version").get("version", ""))
        tags = fetch_json(f"{base_url}/api/tags").get("models", [])
    except (urllib.error.URLError, OSError, ValueError) as exc:
        results.append(CheckResult(
            WARN, f"Ollama is not reachable at {base_url} ({type(exc).__name__}). "
                  "Start Ollama, then run: python manage.py check_ai_model"))
        return results

    if version == PINNED_OLLAMA_VERSION:
        results.append(CheckResult(OK, f"Ollama version {version}."))
    else:
        results.append(CheckResult(
            WARN, f"Ollama version is {version or 'unknown'}; the team standard is {PINNED_OLLAMA_VERSION}."))

    installed = {str(m.get("name", "")): str(m.get("digest", "")) for m in tags if isinstance(m, dict)}
    digest = installed.get(PINNED_MODEL)
    if digest is None:
        results.append(CheckResult(
            WARN, f"Model {PINNED_MODEL} is not installed. Fix: ollama pull {PINNED_MODEL}"))
    elif digest != PINNED_MODEL_DIGEST:
        results.append(CheckResult(
            WARN, f"Model {PINNED_MODEL} has digest {digest[:12]}, expected {PINNED_MODEL_DIGEST[:12]}. "
                  f"Fix: ollama rm {PINNED_MODEL} && ollama pull {PINNED_MODEL}"))
    else:
        results.append(CheckResult(OK, f"Model {PINNED_MODEL} ({PINNED_MODEL_DIGEST[:12]}) is installed."))
    return results
