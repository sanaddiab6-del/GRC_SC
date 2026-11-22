from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Any

from .llm_config import LOCAL_AI_STYLE_OLLAMA, validate_local_base_url


def _extract_json(text: str) -> dict[str, Any] | None:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        cleaned = cleaned.replace("json\n", "", 1) if cleaned.startswith("json\n") else cleaned
    try:
        parsed = json.loads(cleaned)
    except json.JSONDecodeError:
        start = cleaned.find("{")
        end = cleaned.rfind("}")
        if start == -1 or end == -1 or end <= start:
            return None
        try:
            parsed = json.loads(cleaned[start : end + 1])
        except json.JSONDecodeError:
            return None
    return parsed if isinstance(parsed, dict) else None


def _configured_base_url() -> str:
    return os.environ.get("LOCAL_AI_BASE_URL", "").strip()


def _configured_api_style() -> str:
    return os.environ.get("LOCAL_AI_API_STYLE", LOCAL_AI_STYLE_OLLAMA).strip().lower()


def _configured_model() -> str:
    # Recommender path uses the onboarding/default local model if configured.
    return (
        os.environ.get("LOCAL_AI_MODEL_ONBOARDING", "").strip()
        or os.environ.get("LOCAL_AI_MODEL_DEFAULT", "").strip()
        or "qwen3:4b-instruct"
    )


def _configured_timeout() -> float:
    raw_timeout = os.environ.get("LOCAL_AI_TIMEOUT_SECONDS", "60")
    try:
        timeout = float(raw_timeout)
    except (TypeError, ValueError):
        return 20.0
    return timeout if timeout > 0 else 20.0


def is_configured() -> bool:
    if _configured_api_style() != LOCAL_AI_STYLE_OLLAMA:
        return False

    base_url = _configured_base_url()
    if not base_url:
        return False

    safe, _warning = validate_local_base_url(base_url)
    return safe


def query_qwen_json(system_prompt: str, user_payload: dict[str, Any]) -> dict[str, Any] | None:
    base_url = _configured_base_url()
    safe, _warning = validate_local_base_url(base_url)
    if not base_url or not safe or _configured_api_style() != LOCAL_AI_STYLE_OLLAMA:
        return None

    model = _configured_model()
    timeout = _configured_timeout()
    prompt = "\n\n".join(
        [
            system_prompt.strip(),
            "Return one JSON object only. No markdown. No explanations.",
            json.dumps(user_payload, ensure_ascii=False, default=str),
        ]
    )
    body = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "format": "json",
        "options": {
            "temperature": 0,
            "num_predict": 500,
        },
    }
    request = urllib.request.Request(
        f"{base_url.rstrip('/')}/api/generate",
        data=json.dumps(body, ensure_ascii=False).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (
        urllib.error.HTTPError,
        urllib.error.URLError,
        TimeoutError,
        ValueError,
        json.JSONDecodeError,
    ):
        return None

    content = None
    if isinstance(payload, dict):
        content = payload.get("response") or payload.get("content")

    if not isinstance(content, str):
        return None
    return _extract_json(content)