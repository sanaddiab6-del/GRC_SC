from __future__ import annotations

import copy
from typing import Any, Protocol

from .asset_suggestion_serializers import (
    HUMAN_REVIEW_STATUS_CHOICES,
    SAFE_NEXT_ACTIONS,
    SCHEMA_VERSION,
)
from .llm_config import CAPABILITY_ASSET_SUGGESTION, resolve_advisory_capability_config
from .llm_errors import AiProviderExecutionError, AiProviderOutputValidationError
from .llm_prompts import get_system_prompt
from .llm_provider import get_advisory_provider_selection
from .llm_schemas import (
    ALLOWED_TOP_LEVEL_KEYS,
    TOP_LEVEL_REQUIRED_KEYS,
    get_capability_json_schema,
    get_capability_schema_name,
    validate_provider_output_schema,
)


class AssetSuggestionProviderError(Exception):
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


class AssetSuggestionProvider(Protocol):
    available: bool

    def build_asset_suggestion_draft(self, request_payload: dict[str, Any]) -> dict[str, Any]:
        ...


def _build_asset_suggestion_prompt(request_payload: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    system_prompt = get_system_prompt(CAPABILITY_ASSET_SUGGESTION)
    payload = {
        "schema_version": SCHEMA_VERSION,
        "request": request_payload,
        "response_requirements": {
            "draft_type": "AiAssetSuggestionDraft",
            "needs_human_review": True,
            "advisory_only": True,
            "allowed_next_actions": list(SAFE_NEXT_ACTIONS),
        },
    }
    return system_prompt, payload


class AdvisoryAssetSuggestionProvider:
    def __init__(self):
        capability_config = resolve_advisory_capability_config(CAPABILITY_ASSET_SUGGESTION)
        selection = get_advisory_provider_selection(capability_config)
        self._provider = selection.provider
        self._config = selection.config
        self.available = self._provider is not None

    def build_asset_suggestion_draft(self, request_payload: dict[str, Any]) -> dict[str, Any]:
        if self._provider is None:
            raise AssetSuggestionProviderError(
                "local_provider_not_configured",
                "The local AI provider is not configured for Step 3A.",
                allow_fallback=True,
            )

        system_prompt, payload = _build_asset_suggestion_prompt(request_payload)
        try:
            result = self._provider.generate_structured(
                capability=CAPABILITY_ASSET_SUGGESTION,
                model=self._config.model,
                system_prompt=system_prompt,
                user_payload=payload,
                json_schema=get_capability_json_schema(CAPABILITY_ASSET_SUGGESTION),
                timeout_seconds=self._config.timeout_seconds,
                max_output_tokens=self._config.max_output_tokens,
                temperature=self._config.temperature,
                schema_name=get_capability_schema_name(CAPABILITY_ASSET_SUGGESTION),
            )
        except AiProviderExecutionError as exc:
            if exc.error_code == "local_ai_provider_invalid_output":
                raise AssetSuggestionProviderError(
                    exc.error_code,
                    exc.detail,
                    allow_fallback=True,
                    provider_mode="local_provider_error_fallback",
                ) from exc
            raise AssetSuggestionProviderError(
                exc.error_code,
                exc.detail,
                allow_fallback=True,
                provider_mode="local_provider_error_fallback",
            ) from exc

        if not isinstance(result, dict):
            raise AssetSuggestionProviderError(
                "local_ai_provider_invalid_output",
                "The local AI provider did not return valid JSON output.",
                allow_fallback=True,
                provider_mode="local_provider_error_fallback",
            )

        result = _normalize_asset_suggestion_shape(result, request_payload)

        try:
            validate_provider_output_schema(
                CAPABILITY_ASSET_SUGGESTION,
                result,
                strict_mode=bool(request_payload.get("strict_mode", True)),
            )
        except AiProviderOutputValidationError as exc:
            raise AssetSuggestionProviderError(
                exc.error_code,
                exc.detail,
                provider_mode="local_provider_error_blocked",
            ) from exc

        return result


def get_asset_suggestion_provider() -> AssetSuggestionProvider | None:
    provider = AdvisoryAssetSuggestionProvider()
    return provider if provider.available else None


def _normalize_asset_suggestion_shape(
    payload: dict[str, Any],
    request_payload: dict[str, Any],
) -> dict[str, Any]:
    if isinstance(payload.get("draft"), dict):
        payload = payload["draft"]
    elif isinstance(payload.get("asset_suggestion_draft"), dict):
        payload = payload["asset_suggestion_draft"]

    allowed = ALLOWED_TOP_LEVEL_KEYS[CAPABILITY_ASSET_SUGGESTION]
    normalized: dict[str, Any] = {key: payload[key] for key in allowed if key in payload}

    defaults: dict[str, Any] = {
        "draft_type": "AiAssetSuggestionDraft",
        "schema_version": SCHEMA_VERSION,
        "source_summary": {
            "detected_language": request_payload.get("user_locale", "en"),
            "input_char_count": len(request_payload.get("scenario_text") or ""),
            "strict_mode_applied": bool(request_payload.get("strict_mode", True)),
            "scenario_excerpt": (
                request_payload.get("scenario_text")
                or request_payload.get("scope_summary")
                or ""
            )[:160],
            "provider_mode": "configured_local_provider",
            "folder_id": request_payload.get("folder_id"),
            "perimeter_id": request_payload.get("perimeter_id"),
            "compliance_assessment_id": request_payload.get("compliance_assessment_id"),
            "risk_assessment_id": request_payload.get("risk_assessment_id"),
            "parser_notes": [],
        },
        "provider_mode": "configured_local_provider",
        "candidate_assets": [],
        "duplicate_candidates": [],
        "ambiguous_candidates": [],
        "rejected_candidates": [],
        "warnings": [],
        "blocking_questions": [],
        "needs_human_review": True,
        "overall_confidence": 0.5,
        "next_allowed_steps": [
            "review_candidate_assets",
            "resolve_duplicates",
            "prepare_asset_commit_dry_run",
        ],
    }

    for key in TOP_LEVEL_REQUIRED_KEYS[CAPABILITY_ASSET_SUGGESTION]:
        if key not in normalized:
            normalized[key] = copy.deepcopy(defaults[key])

    normalized["draft_type"] = "AiAssetSuggestionDraft"
    normalized["schema_version"] = SCHEMA_VERSION
    normalized["needs_human_review"] = True
    normalized["provider_mode"] = str(normalized.get("provider_mode") or "configured_local_provider")

    source_summary = normalized.get("source_summary")
    if not isinstance(source_summary, dict):
        source_summary = copy.deepcopy(defaults["source_summary"])
    if not (
        isinstance(source_summary.get("detected_language"), str)
        and source_summary.get("detected_language").strip()
    ):
        source_summary["detected_language"] = defaults["source_summary"]["detected_language"]
    try:
        char_count = int(source_summary.get("input_char_count"))
    except (TypeError, ValueError):
        char_count = defaults["source_summary"]["input_char_count"]
    source_summary["input_char_count"] = char_count if char_count >= 0 else defaults["source_summary"]["input_char_count"]
    if not isinstance(source_summary.get("strict_mode_applied"), bool):
        source_summary["strict_mode_applied"] = defaults["source_summary"]["strict_mode_applied"]
    excerpt = source_summary.get("scenario_excerpt")
    if not (isinstance(excerpt, str) and excerpt.strip()):
        excerpt = defaults["source_summary"]["scenario_excerpt"]
    if not (isinstance(excerpt, str) and excerpt.strip()):
        excerpt = "Advisory Step 3A asset suggestion context."
    source_summary["scenario_excerpt"] = excerpt
    source_summary["provider_mode"] = normalized["provider_mode"]
    source_summary.setdefault("folder_id", defaults["source_summary"]["folder_id"])
    source_summary.setdefault("perimeter_id", defaults["source_summary"]["perimeter_id"])
    source_summary.setdefault(
        "compliance_assessment_id",
        defaults["source_summary"]["compliance_assessment_id"],
    )
    source_summary.setdefault("risk_assessment_id", defaults["source_summary"]["risk_assessment_id"])
    if not isinstance(source_summary.get("parser_notes"), list):
        source_summary["parser_notes"] = []
    normalized["source_summary"] = source_summary

    for array_key in (
        "duplicate_candidates",
        "ambiguous_candidates",
        "rejected_candidates",
        "warnings",
        "blocking_questions",
        "next_allowed_steps",
    ):
        value = normalized.get(array_key)
        if value is None:
            normalized[array_key] = []
        elif not isinstance(value, list):
            normalized[array_key] = [value]

    candidate_assets = normalized.get("candidate_assets")
    if isinstance(candidate_assets, dict):
        candidate_assets = [candidate_assets]
    elif not isinstance(candidate_assets, list):
        candidate_assets = []

    safe_default_actions = [
        "accept_for_later_commit",
        "edit_before_commit",
        "reuse_existing_asset",
        "reject",
        "defer",
    ]
    valid_actions = set(SAFE_NEXT_ACTIONS)
    ambiguity_trigger_tokens = (
        "record",
        "records",
        "policy",
        "policies",
        "procedure",
        "procedures",
        "mfa",
        "pam",
        "control",
    )

    normalized_candidates: list[dict[str, Any]] = []
    for index, item in enumerate(candidate_assets):
        if not isinstance(item, dict):
            continue

        candidate = dict(item)

        name = candidate.get("proposed_name")
        if not (isinstance(name, str) and name.strip()):
            alt = candidate.get("name")
            name = alt if isinstance(alt, str) and alt.strip() else None
        if not name:
            # Never invent a candidate that the model did not name.
            continue
        candidate["proposed_name"] = name.strip()[:200]

        description = candidate.get("proposed_description")
        if description is None and isinstance(candidate.get("description"), str):
            description = candidate.get("description")
        if description is not None and not isinstance(description, str):
            description = None
        candidate["proposed_description"] = description

        candidate["temporary_id"] = str(candidate.get("temporary_id") or f"AST-CAND-{index + 1:03d}")[:64]
        candidate["folder_id"] = candidate.get("folder_id") or request_payload.get("folder_id")
        candidate.setdefault("perimeter_id", request_payload.get("perimeter_id"))
        candidate.setdefault(
            "compliance_assessment_id",
            request_payload.get("compliance_assessment_id"),
        )

        rationale = candidate.get("rationale")
        if not (isinstance(rationale, str) and rationale.strip()):
            rationale = "Candidate extracted from Step 3A advisory context."
        candidate["rationale"] = rationale

        try:
            confidence = float(candidate.get("confidence"))
        except (TypeError, ValueError):
            confidence = 0.5
        candidate["confidence"] = min(1.0, max(0.0, confidence))

        if candidate.get("human_review_status") not in HUMAN_REVIEW_STATUS_CHOICES:
            candidate["human_review_status"] = "pending_review"

        candidate["proposed_asset_type"] = _sanitize_asset_type(candidate.get("proposed_asset_type"))
        candidate["criticality"] = _sanitize_criticality(candidate.get("criticality"))

        for optional_key in ("proposed_reference_id", "proposed_asset_category"):
            value = candidate.get(optional_key)
            if value is not None and not isinstance(value, str):
                candidate[optional_key] = None

        candidate["source_text_references"] = _sanitize_source_refs(
            candidate.get("source_text_references")
        )

        flags = _sanitize_ambiguity_flags(candidate.get("ambiguity_flags"))
        combined_text = f"{candidate['proposed_name']} {candidate.get('proposed_description') or ''}".lower()
        if not flags and any(token in combined_text for token in ambiguity_trigger_tokens):
            flags = [
                {
                    "code": "classification_requires_human_review",
                    "message": (
                        "This candidate references records, policies, or control terms and "
                        "may be an asset, evidence, or control; a human must confirm the classification."
                    ),
                }
            ]
        candidate["ambiguity_flags"] = flags

        actions = candidate.get("allowed_next_actions")
        if isinstance(actions, str):
            actions = [actions]
        if not isinstance(actions, list):
            actions = []
        actions = [action for action in actions if action in valid_actions]
        if not actions:
            actions = list(safe_default_actions)
        candidate["allowed_next_actions"] = actions

        candidate = {
            key: value for key, value in candidate.items() if key in _CANDIDATE_ALLOWED_KEYS
        }
        normalized_candidates.append(candidate)

    normalized["candidate_assets"] = normalized_candidates
    normalized["rejected_candidates"] = _sanitize_rejected_candidates(
        normalized.get("rejected_candidates")
    )
    normalized["warnings"] = _sanitize_warnings(normalized.get("warnings"))
    normalized["blocking_questions"] = _sanitize_blocking_questions(
        normalized.get("blocking_questions")
    )
    return normalized


_CANDIDATE_ALLOWED_KEYS = frozenset(
    {
        "temporary_id",
        "proposed_name",
        "proposed_description",
        "proposed_reference_id",
        "proposed_asset_type",
        "proposed_asset_category",
        "criticality",
        "folder_id",
        "perimeter_id",
        "compliance_assessment_id",
        "source_text_references",
        "rationale",
        "confidence",
        "human_review_status",
        "ambiguity_flags",
        "allowed_next_actions",
    }
)


def _sanitize_asset_type(value: Any) -> dict[str, Any] | None:
    if isinstance(value, str):
        upper = value.strip().upper()
        if upper in ("PR", "SP"):
            return {"value": upper, "label": "Primary" if upper == "PR" else "Support"}
        if "PRIMARY" in upper:
            return {"value": "PR", "label": "Primary"}
        if "SUPPORT" in upper or "SECONDARY" in upper:
            return {"value": "SP", "label": "Support"}
        return None
    if not isinstance(value, dict):
        return None
    raw_value = value.get("value")
    if not isinstance(raw_value, str):
        return None
    upper = raw_value.strip().upper()
    if upper not in ("PR", "SP"):
        return None
    label = value.get("label")
    if not (isinstance(label, str) and label.strip()):
        label = "Primary" if upper == "PR" else "Support"
    return {"value": upper, "label": label.strip()[:32]}


def _sanitize_criticality(value: Any) -> dict[str, Any] | None:
    if not isinstance(value, dict):
        return None
    raw_value = value.get("value")
    if not (isinstance(raw_value, str) and raw_value.strip()):
        return None
    note = value.get("mapping_note")
    if not (isinstance(note, str) and note.strip()):
        note = "Criticality is advisory only in Step 3A."
    return {
        "value": raw_value.strip()[:32],
        "is_platform_writable": False,
        "mapping_note": note,
    }


def _sanitize_source_refs(value: Any) -> list[dict[str, Any]]:
    if isinstance(value, dict):
        value = [value]
    if not isinstance(value, list):
        return []
    result: list[dict[str, Any]] = []
    for ref in value:
        if not isinstance(ref, dict):
            continue
        excerpt = ref.get("excerpt")
        if not (isinstance(excerpt, str) and excerpt.strip()):
            continue
        ref_id = ref.get("ref_id")
        if not (isinstance(ref_id, str) and ref_id.strip()):
            ref_id = f"T{len(result) + 1}"
        try:
            char_start = int(ref.get("char_start", 0))
        except (TypeError, ValueError):
            char_start = 0
        try:
            char_end = int(ref.get("char_end", 0))
        except (TypeError, ValueError):
            char_end = 0
        if char_start < 0:
            char_start = 0
        if char_end < char_start:
            char_end = char_start
        result.append(
            {
                "ref_id": ref_id.strip()[:32],
                "excerpt": excerpt,
                "char_start": char_start,
                "char_end": char_end,
            }
        )
    return result


def _sanitize_ambiguity_flags(value: Any) -> list[dict[str, Any]]:
    if isinstance(value, dict):
        value = [value]
    if not isinstance(value, list):
        return []
    result: list[dict[str, Any]] = []
    for flag in value:
        if not isinstance(flag, dict):
            continue
        code = flag.get("code")
        if not (isinstance(code, str) and code.strip()):
            continue
        message = flag.get("message")
        if not (isinstance(message, str) and message.strip()):
            message = "Ambiguity flagged; human review required."
        result.append({"code": code.strip()[:64], "message": message})
    return result


def _sanitize_rejected_candidates(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    result: list[dict[str, Any]] = []
    for entry in value:
        if not isinstance(entry, dict):
            continue
        label = entry.get("source_label")
        reclass = entry.get("recommended_reclassification")
        reason = entry.get("reason")
        if not all(isinstance(field, str) and field.strip() for field in (label, reclass, reason)):
            continue
        try:
            confidence = float(entry.get("confidence"))
        except (TypeError, ValueError):
            confidence = 0.5
        result.append(
            {
                "source_label": label.strip()[:200],
                "recommended_reclassification": reclass.strip()[:64],
                "reason": reason,
                "confidence": min(1.0, max(0.0, confidence)),
            }
        )
    return result


def _sanitize_warnings(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    result: list[dict[str, Any]] = []
    for entry in value:
        if not isinstance(entry, dict):
            continue
        code = entry.get("code")
        message = entry.get("message")
        if not (isinstance(code, str) and code.strip()):
            continue
        if not (isinstance(message, str) and message.strip()):
            continue
        affected = entry.get("affected_fields")
        if not isinstance(affected, list):
            affected = []
        affected = [field for field in affected if isinstance(field, str)]
        result.append(
            {
                "code": code.strip()[:64],
                "message": message,
                "affected_fields": affected,
                "needs_review": bool(entry.get("needs_review", True)),
            }
        )
    return result


def _sanitize_blocking_questions(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    result: list[dict[str, Any]] = []
    for entry in value:
        if not isinstance(entry, dict):
            continue
        question_id = entry.get("question_id")
        question_text = entry.get("question_text")
        reason = entry.get("reason")
        if not all(
            isinstance(field, str) and field.strip()
            for field in (question_id, question_text, reason)
        ):
            continue
        affected = entry.get("affected_fields")
        if not isinstance(affected, list):
            affected = []
        affected = [field for field in affected if isinstance(field, str)]
        if not affected:
            affected = ["candidate_assets"]
        result.append(
            {
                "question_id": question_id.strip()[:64],
                "question_text": question_text,
                "reason": reason,
                "affected_fields": affected,
                "severity": "blocking",
            }
        )
    return result