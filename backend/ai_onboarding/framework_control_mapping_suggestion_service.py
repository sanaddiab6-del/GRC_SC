from __future__ import annotations

import csv
import re
from pathlib import Path
from typing import Any

from django.core.exceptions import ValidationError as DjangoValidationError

from core.models import Framework, LoadedLibrary, RequirementNode
from iam.models import Folder, RoleAssignment

from .framework_control_mapping_suggestion_guardrails import (
    FrameworkControlMappingSuggestionDraftValidationError,
    build_allowed_control_registry,
    normalize_control_key,
    resolve_allowed_control,
    validate_framework_control_mapping_suggestion_guardrails,
)
from .framework_control_mapping_suggestion_provider import (
    FrameworkControlMappingSuggestionProviderError,
    get_framework_control_mapping_suggestion_provider,
)
from .framework_control_mapping_suggestion_serializers import (
    AiFrameworkControlMappingSuggestionDraftSerializer,
    DEFAULT_USER_LOCALE,
    MAPPING_TYPE_CHOICES,
    MAX_FRAMEWORK_CONTROL_MAPPINGS,
)


# Step 7A is advisory-only: the response carries no ids, no write flags, and no approval
# flags. Every mapping stays at review_status 'pending_review'.
REVIEW_STATUS = "pending_review"

# Safe read-only discovery caps. Discovery only ever reads; it never writes. The cap covers a
# whole framework (SAMA CSF has 250 assessable requirements) so the relevance ranking below can
# reach clauses that sit late in the document, such as the third-party clauses.
MAX_DISCOVERED_CANDIDATES = 500
# Only a slice of the candidate set is handed to the local model so the prompt fits a small
# context window and the JSON answer stays small. The slice is the candidates most relevant to
# the case; the full set is still what the guardrails validate against.
MAX_PROVIDER_CANDIDATES = 20

# Read-only export of the framework libraries kept at the repository root. It is the last
# resort for candidate controls when the database holds no assessable requirement nodes.
FRAMEWORKS_CSV_FILENAME = "all_frameworks_export.csv"
CSV_SOURCE_LABEL = FRAMEWORKS_CSV_FILENAME
# The export holds hundreds of assessable rows per framework. Only the most relevant few
# become candidates so the local model receives a small prompt and answers within its
# timeout. The guardrail registry is built from exactly this set.
MAX_CSV_CANDIDATES = 12
# Upper bound on relevant rows collected before ranking, so the strongest matches further
# down the file are still considered.
MAX_CSV_SCAN_ROWS = 400
# When a framework matches but nothing matches the context terms, only a small head slice
# of its assessable controls is offered for review.
MAX_CSV_UNMATCHED_ROWS = 10

# Context terms used to prefer the framework controls that are relevant to the identity,
# authentication, and access findings this onboarding flow produces.
CSV_CONTEXT_TERMS = (
    "mfa",
    "multi-factor",
    "multifactor",
    "authentication",
    "remote access",
    "access control",
    "identity",
    "privileged",
    "password",
    "user access",
)

# Strongest-first phrases used to rank the relevant export rows. Earlier phrases win, so
# the remote-access / MFA / IAM controls reach the model even when the framework has
# hundreds of assessable rows.
CSV_PRIORITY_PHRASES = (
    "multi-factor authentication should be used for all remote access",
    "remote access",
    "multi-factor",
    "mfa",
    "identity and access management",
    # The export also words the IAM clauses as "identity and access policy".
    "identity and access",
    "privileged",
    "access control",
)

# Internal-only candidate keys: they drive normalization and guardrails but are never sent
# to the model and never appear in the response.
INTERNAL_CANDIDATE_KEYS = ("title_is_generated",)

# Prompt-size guards. The registry always keeps the full candidate text; only the copy
# handed to the model is shortened.
MAX_PROVIDER_DESCRIPTION_CHARS = 700
MAX_PROVIDER_TYPICAL_EVIDENCE_CHARS = 300

MAX_MAPPINGS = MAX_FRAMEWORK_CONTROL_MAPPINGS
MAX_FALLBACK_MAPPINGS = MAX_MAPPINGS
MAX_CANDIDATES_PER_SOURCE = 2

ALLOWED_MAPPING_KEYS = {
    "temporary_id",
    "framework_control_reference",
    "framework_control_code",
    "framework_control_title",
    "framework_control_description",
    "framework_name",
    "mapping_type",
    "linked_finding_reference",
    "linked_finding_title",
    "linked_applied_control_reference",
    "linked_applied_control_title",
    "linked_remediation_action_reference",
    "linked_remediation_action_title",
    "rationale",
    "evidence_needed",
    "confidence",
    "review_status",
}

OPTIONAL_LINK_KEYS = (
    "linked_finding_reference",
    "linked_finding_title",
    "linked_applied_control_reference",
    "linked_applied_control_title",
    "linked_remediation_action_reference",
    "linked_remediation_action_title",
)

TEXT_MAPPING_KEYS = (
    "temporary_id",
    "framework_control_reference",
    "framework_control_code",
    "framework_control_title",
    "framework_control_description",
    "framework_name",
    "rationale",
    *OPTIONAL_LINK_KEYS,
)

_TOKEN_RE = re.compile(r"[a-z0-9]+")

_STOPWORDS = {
    "and",
    "are",
    "for",
    "not",
    "the",
    "that",
    "this",
    "with",
    "from",
    "was",
    "were",
    "has",
    "have",
    "its",
    "into",
    "must",
    "shall",
    "should",
    "all",
    "any",
    "our",
    "their",
    "there",
    "when",
    "where",
    "which",
    "been",
    "being",
    "over",
    "per",
    "via",
}

# Deterministic advisory synonym families. They only widen keyword overlap between the
# supplied context and the existing candidate controls; they never create controls.
_SYNONYM_EXPANSIONS = {
    "mfa": {"multi", "factor", "authentication", "strong", "identity", "access"},
    "multifactor": {"multi", "factor", "authentication"},
    "authentication": {"authentication", "identity", "access", "mfa"},
    "remote": {"remote", "vpn", "teleworking", "external"},
    "access": {"access", "identity", "authorization"},
    "pam": {"privileged", "access", "identity"},
    "privileged": {"privileged", "access", "identity"},
    "password": {"authentication", "identity", "access"},
    "identity": {"identity", "access"},
    "review": {"review", "recertification"},
}

_GENERIC_EVIDENCE_NEEDED = (
    "Policy or procedure document covering the control",
    "Configuration or implementation evidence",
    "Operational records covering the review period",
)


class AiFrameworkControlMappingSuggestionService:
    def __init__(self, *, base_dir: str | None = None, provider=None):
        self.base_dir = base_dir or str(Path(__file__).resolve().parents[1])
        self.provider = provider

    def build_framework_control_mapping_suggestion_draft(
        self, request, request_data: dict[str, Any]
    ) -> dict[str, Any]:
        normalized = _normalize_request_data(request_data)
        user = getattr(request, "user", None)

        candidates, discovery_warnings, discovered_framework_name = _resolve_candidate_controls(
            user, normalized, self.base_dir
        )
        registry = build_allowed_control_registry(candidates)
        framework_name = normalized.get("framework_name") or discovered_framework_name or ""

        if not candidates:
            # Nothing existing to map to: Step 7A refuses rather than inventing controls.
            return _finalize(
                _build_blocked_draft(discovery_warnings), registry
            )

        provider_payload = _build_provider_payload(normalized, candidates)

        provider = (
            self.provider
            if self.provider is not None
            else get_framework_control_mapping_suggestion_provider()
        )

        if provider is None:
            draft = build_framework_control_mapping_suggestion_fallback_draft(
                normalized, candidates, framework_name
            )
            _annotate_provider_mode(
                draft,
                provider_mode="provider_not_configured_fallback",
                warning={
                    "code": "provider_not_configured_fallback",
                    "message": (
                        "No AI provider is configured; the advisory framework control mapping "
                        "draft was generated by the deterministic fallback."
                    ),
                    "affected_fields": ["framework_control_mappings"],
                    "needs_review": True,
                },
            )
        else:
            try:
                draft = provider.build_framework_control_mapping_suggestion_draft(
                    provider_payload
                )
                _annotate_provider_mode(draft, provider_mode="configured_local_provider")
            except FrameworkControlMappingSuggestionProviderError as exc:
                if not exc.allow_fallback:
                    raise
                draft = build_framework_control_mapping_suggestion_fallback_draft(
                    normalized, candidates, framework_name
                )
                _annotate_provider_mode(
                    draft,
                    provider_mode="local_provider_error_fallback",
                    warning={
                        "code": "local_provider_error_fallback",
                        "message": exc.detail,
                        "affected_fields": ["framework_control_mappings"],
                        "needs_review": True,
                    },
                )

        for warning in discovery_warnings:
            _annotate_provider_mode(draft, provider_mode=draft["provider_mode"], warning=warning)

        _enrich_draft(draft, registry, framework_name)
        return _finalize(draft, registry)


def build_framework_control_mapping_suggestion_draft(
    request,
    request_data: dict[str, Any],
    *,
    base_dir: str | None = None,
    provider=None,
) -> dict[str, Any]:
    service = AiFrameworkControlMappingSuggestionService(base_dir=base_dir, provider=provider)
    return service.build_framework_control_mapping_suggestion_draft(request, request_data)


def _finalize(draft: dict[str, Any], registry: dict[str, dict[str, Any]]) -> dict[str, Any]:
    validate_framework_control_mapping_suggestion_guardrails(draft, registry)

    # Only after the model's own text has been validated is it replaced by the candidate's
    # authoritative text, so an invented clause can never be masked by the restore.
    _restore_candidate_text(draft, registry)
    _refresh_overall_confidence(draft)

    serializer = AiFrameworkControlMappingSuggestionDraftSerializer(data=draft)
    if not serializer.is_valid():
        raise FrameworkControlMappingSuggestionDraftValidationError(
            "ai_framework_control_mapping_suggestion_draft_validation_failed",
            "Generated advisory framework control mapping draft did not pass contract validation.",
            serializer.errors,
        )

    validated_draft = serializer.data
    validate_framework_control_mapping_suggestion_guardrails(validated_draft, registry)
    return validated_draft


def _build_blocked_draft(discovery_warnings: list[dict[str, Any]]) -> dict[str, Any]:
    warnings = [
        {
            "code": "no_candidate_framework_controls",
            "message": (
                "No existing framework controls were supplied and none could be discovered "
                "read-only, so Step 7A produced no mappings. Framework controls are never "
                "created or invented in this step."
            ),
            "affected_fields": ["candidate_framework_controls", "framework_reference"],
            "needs_review": True,
        },
        *discovery_warnings,
    ]
    return {
        "provider_mode": "candidate_controls_missing_blocked",
        "overall_confidence": 0.0,
        "framework_control_mappings": [],
        "warnings": warnings,
        "ambiguity_flags": [
            {
                "code": "no_candidate_framework_controls",
                "message": (
                    "Provide candidate_framework_controls or a resolvable framework_reference "
                    "before Step 7A can suggest framework control mappings."
                ),
            }
        ],
    }


# ---- Candidate framework controls ----------------------------------------------------


def _resolve_candidate_controls(
    user, request_data: dict[str, Any], base_dir: str
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], str]:
    """Return the closed set of existing framework controls Step 7A may map to.

    Precedence: supplied candidates, then a best-effort read-only lookup of the referenced
    Framework's requirement nodes, then a read-only lookup in the repository-root framework
    export CSV. Nothing here writes, and nothing here invents a control: every candidate is
    an existing framework control. Any failure is downgraded to a warning.
    """
    supplied = [
        candidate
        for candidate in request_data.get("candidate_framework_controls") or []
        if isinstance(candidate, dict) and (candidate.get("title") or "").strip()
    ]
    if supplied:
        return supplied, [], ""

    try:
        candidates, warnings, framework_name = _discover_candidate_controls(user, request_data)
    except Exception:  # pragma: no cover - discovery is strictly best effort
        candidates, framework_name = [], ""
        warnings = [
            {
                "code": "framework_control_discovery_unavailable",
                "message": (
                    "Read-only framework control discovery could not be completed; supply "
                    "candidate_framework_controls instead."
                ),
                "affected_fields": ["framework_reference", "candidate_framework_controls"],
                "needs_review": True,
            }
        ]

    if candidates:
        return candidates, warnings, framework_name

    csv_candidates = _load_csv_candidate_controls(
        base_dir, _framework_match_terms(request_data, framework_name)
    )
    if not csv_candidates:
        return [], warnings, framework_name

    warnings.append(
        {
            "code": "framework_controls_loaded_from_csv_export",
            "message": (
                "Framework control candidates were loaded read-only from "
                f"{FRAMEWORKS_CSV_FILENAME} because database discovery returned no assessable "
                "requirement nodes."
            ),
            "affected_fields": ["candidate_framework_controls"],
            "needs_review": True,
        }
    )
    return csv_candidates, warnings, framework_name


def _discover_candidate_controls(
    user, request_data: dict[str, Any]
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], str]:
    warnings: list[dict[str, Any]] = []
    framework = _resolve_framework(request_data)

    if framework is None:
        return [], warnings, ""

    if not _is_visible_to_user(user, framework):
        warnings.append(
            {
                "code": "framework_not_visible",
                "message": (
                    "The referenced framework is not visible to the current user, so no "
                    "framework controls were discovered."
                ),
                "affected_fields": ["framework_reference"],
                "needs_review": True,
            }
        )
        return [], warnings, ""

    framework_name = framework.name or ""
    nodes = (
        RequirementNode.objects.filter(framework=framework, assessable=True)
        .only("urn", "ref_id", "name", "description", "parent_urn")
        .order_by("order_id")[:MAX_DISCOVERED_CANDIDATES]
    )

    candidates: list[dict[str, Any]] = []
    for node in nodes:
        title = (node.name or node.ref_id or "").strip()
        reference = (node.urn or node.ref_id or "").strip()
        if not title or not reference:
            continue
        candidates.append(
            {
                "reference": reference,
                "code": (node.ref_id or "").strip(),
                "title": title,
                "description": (node.description or "").strip(),
                "domain": framework_name,
                "section": (node.parent_urn or "").strip(),
                "source": "discovered_framework_requirement",
            }
        )

    if not candidates:
        warnings.append(
            {
                "code": "no_discovered_framework_controls",
                "message": (
                    "The referenced framework has no assessable requirement nodes to map to."
                ),
                "affected_fields": ["framework_reference"],
                "needs_review": True,
            }
        )

    return candidates, warnings, framework_name


def _resolve_framework(request_data: dict[str, Any]):
    reference = request_data.get("framework_reference") or {}

    framework_id = (reference.get("framework_id") or "").strip()
    if framework_id:
        framework = _first_or_none(Framework.objects.filter(id=framework_id))
        if framework is not None:
            return framework

    framework_urn = (reference.get("framework_urn") or "").strip()
    if framework_urn:
        framework = _first_or_none(Framework.objects.filter(urn=framework_urn))
        if framework is not None:
            return framework

    library = _resolve_loaded_library(request_data)
    if library is not None:
        framework = _first_or_none(Framework.objects.filter(library=library))
        if framework is not None:
            return framework

    name = (reference.get("framework_name") or request_data.get("framework_name") or "").strip()
    if name:
        return _first_or_none(Framework.objects.filter(name__iexact=name))

    return None


def _resolve_loaded_library(request_data: dict[str, Any]):
    reference = request_data.get("loaded_library_reference") or {}

    library_id = (reference.get("library_id") or "").strip()
    if library_id:
        library = _first_or_none(LoadedLibrary.objects.filter(id=library_id))
        if library is not None:
            return library

    library_urn = (reference.get("library_urn") or "").strip()
    if library_urn:
        library = _first_or_none(LoadedLibrary.objects.filter(urn=library_urn))
        if library is not None:
            return library

    library_name = (reference.get("library_name") or "").strip()
    if library_name:
        return _first_or_none(LoadedLibrary.objects.filter(name__iexact=library_name))

    return None


def _first_or_none(queryset):
    # Django raises ValidationError for a malformed UUID lookup value.
    try:
        return queryset.first()
    except (ValueError, TypeError, DjangoValidationError):
        return None


def _is_visible_to_user(user, instance) -> bool:
    if not getattr(user, "is_authenticated", False):
        return False
    try:
        visible_ids = RoleAssignment.get_accessible_object_ids(
            folder=Folder.get_root_folder(),
            user=user,
            object_type=instance.__class__,
        )[0]
    except Exception:
        # Visibility could not be evaluated: treat the object as not discoverable.
        return False
    return str(instance.id) in {str(item_id) for item_id in visible_ids}


# ---- Read-only CSV export fallback ---------------------------------------------------


def _framework_match_terms(request_data: dict[str, Any], discovered_framework_name: str) -> list[str]:
    reference = request_data.get("framework_reference") or {}
    raw_terms = (
        request_data.get("framework_name"),
        reference.get("framework_name"),
        reference.get("framework_urn"),
        discovered_framework_name,
    )
    terms: list[str] = []
    for term in raw_terms:
        normalized = (term or "").strip().lower()
        if normalized and normalized not in terms:
            terms.append(normalized)
    return terms


def _locate_frameworks_csv(base_dir: str) -> Path | None:
    """Find the framework export CSV at the repository root, read-only."""
    seen: set[Path] = set()
    roots: list[Path] = []
    for start in (Path(base_dir or "."), Path(__file__).resolve().parent):
        try:
            resolved = start.resolve()
        except OSError:  # pragma: no cover - defensive
            continue
        for directory in (resolved, *resolved.parents):
            if directory not in seen:
                seen.add(directory)
                roots.append(directory)

    for directory in roots:
        path = directory / FRAMEWORKS_CSV_FILENAME
        if path.is_file():
            return path
    return None


def _load_csv_candidate_controls(base_dir: str, framework_terms: list[str]) -> list[dict[str, Any]]:
    """Read existing framework controls from the export CSV. Never writes, never raises."""
    path = _locate_frameworks_csv(base_dir)
    if path is None:
        return []

    matched: list[dict[str, str]] = []
    unmatched: list[dict[str, str]] = []
    try:
        with path.open(encoding="utf-8-sig", newline="") as handle:
            for row in csv.DictReader(handle):
                if (row.get("Is Assessable") or "").strip().lower() != "yes":
                    continue
                if framework_terms and not _csv_framework_row_matches(row, framework_terms):
                    continue
                if _csv_row_matches_context_terms(row):
                    matched.append(row)
                    if len(matched) >= MAX_CSV_SCAN_ROWS:
                        break
                elif len(unmatched) < MAX_CSV_UNMATCHED_ROWS:
                    unmatched.append(row)
    except (OSError, UnicodeDecodeError, csv.Error):  # pragma: no cover - defensive
        return []

    if matched:
        # Stable sort: strongest phrase match first, original export order within a rank.
        rows = sorted(
            enumerate(matched), key=lambda item: (_csv_priority_rank(item[1]), item[0])
        )
        rows = [row for _, row in rows]
    else:
        rows = unmatched

    candidates: list[dict[str, Any]] = []
    for row in rows[:MAX_CSV_CANDIDATES]:
        candidate = _csv_row_to_candidate(row)
        if candidate is not None:
            candidates.append(candidate)
    return candidates


def _csv_priority_rank(row: dict[str, str]) -> int:
    """Lower is stronger. Rows without a priority phrase sort last."""
    haystack = " ".join(
        (row.get(field) or "") for field in ("Control Name", "Control Description")
    ).lower()
    for rank, phrase in enumerate(CSV_PRIORITY_PHRASES):
        if phrase in haystack:
            return rank
    return len(CSV_PRIORITY_PHRASES)


def _csv_framework_row_matches(row: dict[str, str], framework_terms: list[str]) -> bool:
    name = (row.get("Framework Name") or "").strip().lower()
    urn = (row.get("Framework URN") or "").strip().lower()
    if not name and not urn:
        return False

    for term in framework_terms:
        if term in {name, urn}:
            return True
        # Loose containment either way, so "SAMA ECC-1:2018" still reaches the SAMA export
        # rows even though the CSV names the framework differently.
        for value in (name, urn):
            if value and (term in value or value in term):
                return True
        for token in _FRAMEWORK_FAMILY_TOKENS:
            if token in term and token in f"{name} {urn}":
                return True
    return False


# Framework families that are recognisable across naming variants in the export.
_FRAMEWORK_FAMILY_TOKENS = ("sama", "nca", "iso", "nist", "pci", "gdpr", "soc")


def _csv_row_matches_context_terms(row: dict[str, str]) -> bool:
    haystack = " ".join(
        (row.get(field) or "") for field in ("Control Name", "Control Description")
    ).lower()
    return any(term in haystack for term in CSV_CONTEXT_TERMS)


def _csv_row_to_candidate(row: dict[str, str]) -> dict[str, Any] | None:
    framework_name = (row.get("Framework Name") or "").strip()
    framework_urn = (row.get("Framework URN") or "").strip()
    ref_id = (row.get("Control Ref ID") or "").strip()
    control_urn = (row.get("Control URN") or "").strip()
    control_name = (row.get("Control Name") or "").strip()
    parent_ref_id = (row.get("Parent Ref ID") or "").strip()

    reference = control_urn or (f"{framework_urn}:{ref_id}" if framework_urn and ref_id else ref_id)
    if not reference:
        return None

    # Many export rows carry the clause text in the description and leave Control Name
    # blank. A readable placeholder title is generated so the mapping stays reviewable; it
    # is flagged so it is never treated as official framework clause text.
    title_is_generated = not control_name
    if control_name:
        title = control_name
    elif not ref_id:
        return None
    elif "sama" in framework_name.lower():
        title = f"SAMA control {ref_id}"
    else:
        title = f"Framework control {ref_id}"

    return {
        "reference": reference,
        "code": ref_id,
        "title": title,
        "description": (row.get("Control Description") or "").strip(),
        "framework_name": framework_name,
        "domain": parent_ref_id,
        "section": parent_ref_id,
        "source": CSV_SOURCE_LABEL,
        "typical_evidence": (row.get("Typical Evidence") or "").strip(),
        "title_is_generated": title_is_generated,
    }


# ---- Deterministic fallback ----------------------------------------------------------


def build_framework_control_mapping_suggestion_fallback_draft(
    request_data: dict[str, Any],
    candidates: list[dict[str, Any]],
    framework_name: str = "",
) -> dict[str, Any]:
    """Deterministic advisory draft used when no local provider is available.

    It maps supplied context to existing candidate controls by keyword overlap only. It
    never reads or writes GRC records and never invents a framework control.
    """
    evidence_needed = _default_evidence_needed(request_data)

    sources: list[tuple[dict[str, Any], str]] = []
    for finding in request_data.get("preliminary_findings") or []:
        sources.append((finding, "supports_finding"))
    for weakness in request_data.get("known_weaknesses") or []:
        sources.append(({"title": weakness}, "compliance_gap_mapping"))
    for control in request_data.get("applied_controls") or []:
        sources.append((control, "supports_applied_control"))
    for action in request_data.get("remediation_actions") or []:
        sources.append((action, "supports_remediation"))

    mappings: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()

    for source, mapping_type in sources:
        if len(mappings) >= MAX_FALLBACK_MAPPINGS:
            break
        source_title = (source.get("title") or "").strip()
        if not source_title:
            continue
        source_tokens = _expand_tokens(
            _tokens(f"{source_title} {source.get('description') or ''}")
        )

        for candidate, score in _rank_candidates(source_tokens, candidates):
            if len(mappings) >= MAX_FALLBACK_MAPPINGS:
                break
            key = (str(candidate.get("reference") or candidate.get("title")), source_title)
            if key in seen:
                continue
            seen.add(key)
            mappings.append(
                _build_fallback_mapping(
                    len(mappings) + 1,
                    candidate,
                    source,
                    source_title,
                    mapping_type,
                    framework_name,
                    evidence_needed,
                    score,
                )
            )

    if not mappings:
        warnings.append(
            {
                "code": "no_candidate_control_match",
                "message": (
                    "No existing candidate framework control matched the supplied findings, "
                    "applied controls, or remediation actions. No framework controls were invented."
                ),
                "affected_fields": ["candidate_framework_controls", "framework_control_mappings"],
                "needs_review": True,
            }
        )

    return {
        "provider_mode": "provider_not_configured_fallback",
        "overall_confidence": 0.0,
        "framework_control_mappings": mappings,
        "warnings": warnings,
        "ambiguity_flags": [],
    }


def _build_fallback_mapping(
    index: int,
    candidate: dict[str, Any],
    source: dict[str, Any],
    source_title: str,
    mapping_type: str,
    framework_name: str,
    evidence_needed: list[str],
    score: int,
) -> dict[str, Any]:
    source_reference = (source.get("reference") or "").strip()
    mapping = {
        "temporary_id": f"framework_mapping_{index}",
        "framework_control_reference": (
            candidate.get("reference") or candidate.get("code") or candidate.get("title") or ""
        ),
        "framework_control_code": candidate.get("code") or "",
        "framework_control_title": candidate.get("title") or "",
        "framework_control_description": candidate.get("description") or "",
        "framework_name": framework_name,
        "mapping_type": mapping_type,
        "linked_finding_reference": "",
        "linked_finding_title": "",
        "linked_applied_control_reference": "",
        "linked_applied_control_title": "",
        "linked_remediation_action_reference": "",
        "linked_remediation_action_title": "",
        "rationale": (
            f"The existing framework control '{candidate.get('title')}' overlaps with "
            f"'{source_title}'. This is an advisory mapping suggestion that requires human "
            "review before anything is recorded."
        ),
        "evidence_needed": list(evidence_needed),
        "confidence": min(0.85, round(0.5 + 0.1 * score, 2)),
        "review_status": REVIEW_STATUS,
    }

    if mapping_type == "supports_finding":
        mapping["linked_finding_reference"] = source_reference
        mapping["linked_finding_title"] = source_title
    elif mapping_type == "supports_applied_control":
        mapping["linked_applied_control_reference"] = source_reference
        mapping["linked_applied_control_title"] = source_title
    elif mapping_type == "supports_remediation":
        mapping["linked_remediation_action_reference"] = source_reference
        mapping["linked_remediation_action_title"] = source_title

    return mapping


def _rank_candidates(
    source_tokens: set[str], candidates: list[dict[str, Any]]
) -> list[tuple[dict[str, Any], int]]:
    scored: list[tuple[dict[str, Any], int]] = []
    for candidate in candidates:
        candidate_tokens = _expand_tokens(
            _tokens(
                " ".join(
                    str(candidate.get(field) or "")
                    for field in ("title", "description", "domain", "section", "code")
                )
            )
        )
        score = len(source_tokens & candidate_tokens)
        if score:
            scored.append((candidate, score))
    scored.sort(key=lambda item: (-item[1], str(item[0].get("title") or "")))
    return scored[:MAX_CANDIDATES_PER_SOURCE]


def _tokens(text: str) -> set[str]:
    return {
        token
        for token in _TOKEN_RE.findall((text or "").lower())
        if len(token) >= 3 and token not in _STOPWORDS
    }


def _expand_tokens(tokens: set[str]) -> set[str]:
    expanded = set(tokens)
    for token in tokens:
        expanded |= _SYNONYM_EXPANSIONS.get(token, set())
    return expanded


def _default_evidence_needed(request_data: dict[str, Any]) -> list[str]:
    evidence: list[str] = []
    for item in request_data.get("evidence_requests") or []:
        title = (item.get("title") or "").strip()
        if title and title not in evidence:
            evidence.append(title[:500])
        if len(evidence) >= 3:
            break
    return evidence or list(_GENERIC_EVIDENCE_NEEDED)


# ---- Normalization -------------------------------------------------------------------


def _normalize_request_data(request_data: dict[str, Any]) -> dict[str, Any]:
    normalized = dict(request_data)
    normalized["user_locale"] = normalized.get("user_locale") or DEFAULT_USER_LOCALE
    normalized["strict_mode"] = bool(normalized.get("strict_mode", True))
    normalized["known_weaknesses"] = list(normalized.get("known_weaknesses") or [])
    for field in (
        "assets",
        "applied_controls",
        "remediation_actions",
        "evidence_requests",
        "audit_questions",
        "preliminary_findings",
        "candidate_framework_controls",
    ):
        normalized[field] = list(normalized.get(field) or [])
    normalized["folder_reference"] = normalized.get("folder_reference") or {}
    normalized["framework_reference"] = normalized.get("framework_reference") or {}
    normalized["loaded_library_reference"] = normalized.get("loaded_library_reference") or {}
    return normalized


# Case items whose text says what the audit is about; candidates are ranked against them.
_CASE_CONTEXT_ITEM_FIELDS = (
    "applied_controls",
    "remediation_actions",
    "evidence_requests",
    "audit_questions",
    "preliminary_findings",
    "assets",
)


def _case_context_tokens(request_data: dict[str, Any]) -> set[str]:
    parts = [str(weakness) for weakness in request_data.get("known_weaknesses") or []]
    parts.append(str(request_data.get("case_summary") or ""))
    for field in _CASE_CONTEXT_ITEM_FIELDS:
        for item in request_data.get(field) or []:
            if isinstance(item, dict):
                parts.extend(str(item.get(key) or "") for key in ("title", "description"))
    return _expand_tokens(_tokens(" ".join(parts)))


def _order_by_case_relevance(
    request_data: dict[str, Any], candidates: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    """Put the candidates that share the most terms with the case first.

    Discovery reads requirements in document order, so without this the model only ever saw a
    framework's opening clauses (for SAMA, governance) and never the ones the case is about.
    The sort is stable, so candidates with the same overlap keep document order.
    """
    context = _case_context_tokens(request_data)
    if not context:
        return list(candidates)

    def overlap(candidate: dict[str, Any]) -> int:
        text = " ".join(str(candidate.get(field) or "") for field in ("title", "description"))
        return len(context & _expand_tokens(_tokens(text)))

    return sorted(candidates, key=lambda candidate: -overlap(candidate))


def _build_provider_payload(
    request_data: dict[str, Any], candidates: list[dict[str, Any]]
) -> dict[str, Any]:
    payload = dict(request_data)
    payload["candidate_framework_controls"] = [
        _shrink_candidate_for_provider(candidate)
        for candidate in _order_by_case_relevance(request_data, candidates)[
            :MAX_PROVIDER_CANDIDATES
        ]
    ]
    payload["max_framework_control_mappings"] = MAX_MAPPINGS
    return payload


def _shrink_candidate_for_provider(candidate: dict[str, Any]) -> dict[str, Any]:
    """Trim a candidate for the prompt only.

    Long clause text and blank optional fields are what make the Step 7A prompt slow, so
    the model receives a shortened copy. The registry keeps the full candidate text, and
    the response is restored from it, so nothing authoritative is lost.
    """
    shrunk: dict[str, Any] = {}
    for key, value in candidate.items():
        if key in INTERNAL_CANDIDATE_KEYS:
            continue
        if isinstance(value, str):
            trimmed = value.strip()
            if not trimmed:
                continue
            if key == "description":
                trimmed = trimmed[:MAX_PROVIDER_DESCRIPTION_CHARS]
            elif key == "typical_evidence":
                trimmed = trimmed[:MAX_PROVIDER_TYPICAL_EVIDENCE_CHARS]
            shrunk[key] = trimmed
        elif value is not None:
            shrunk[key] = value
    return shrunk


def _annotate_provider_mode(
    draft: dict[str, Any],
    *,
    provider_mode: str,
    warning: dict[str, Any] | None = None,
) -> None:
    draft["provider_mode"] = provider_mode
    if warning is not None:
        warnings = draft.setdefault("warnings", [])
        if not any(
            isinstance(item, dict) and item.get("code") == warning["code"] for item in warnings
        ):
            warnings.append(warning)


def _enrich_draft(
    draft: dict[str, Any],
    registry: dict[str, dict[str, Any]],
    framework_name: str,
) -> None:
    draft.setdefault("provider_mode", "configured_local_provider")
    draft.setdefault("warnings", [])
    draft["ambiguity_flags"] = _normalize_ambiguity_flags(draft.get("ambiguity_flags"))

    mappings = draft.get("framework_control_mappings")
    if isinstance(mappings, list):
        normalized = [
            _normalize_mapping(index, mapping, registry, framework_name)
            if isinstance(mapping, dict)
            else mapping
            for index, mapping in enumerate(mappings, start=1)
        ]
        deduplicated = _deduplicate_mappings(normalized)
        if len(deduplicated) > MAX_MAPPINGS:
            _annotate_provider_mode(
                draft,
                provider_mode=draft["provider_mode"],
                warning={
                    "code": "framework_control_mappings_trimmed",
                    "message": (
                        f"Step 7A kept the first {MAX_MAPPINGS} advisory mappings for review; "
                        f"{len(deduplicated) - MAX_MAPPINGS} further suggestions were trimmed."
                    ),
                    "affected_fields": ["framework_control_mappings"],
                    "needs_review": True,
                },
            )
        draft["framework_control_mappings"] = deduplicated[:MAX_MAPPINGS]

    _refresh_overall_confidence(draft)


def _deduplicate_mappings(mappings: list[Any]) -> list[Any]:
    """Drop repeated cards for the same control, link, and mapping_type.

    The same framework control may legitimately appear more than once when the mapping_type
    differs or it supports a different finding, applied control, or remediation action. An
    exact repeat is noise, so only the highest-confidence one is kept.
    """
    best_by_key: dict[tuple[str, str, str], int] = {}
    kept: list[Any] = []

    for mapping in mappings:
        if not isinstance(mapping, dict):
            kept.append(mapping)
            continue

        key = (
            normalize_control_key(mapping.get("framework_control_reference")),
            str(mapping.get("mapping_type") or "").strip().lower(),
            _linked_item_key(mapping),
        )
        confidence = mapping.get("confidence")
        score = float(confidence) if isinstance(confidence, (int, float)) and not isinstance(
            confidence, bool
        ) else -1.0

        previous_index = best_by_key.get(key)
        if previous_index is None:
            best_by_key[key] = len(kept)
            kept.append(mapping)
            continue

        previous = kept[previous_index]
        previous_confidence = previous.get("confidence")
        previous_score = (
            float(previous_confidence)
            if isinstance(previous_confidence, (int, float))
            and not isinstance(previous_confidence, bool)
            else -1.0
        )
        if score > previous_score:
            kept[previous_index] = mapping

    return kept


def _linked_item_key(mapping: dict[str, Any]) -> str:
    for reference_field, title_field in (
        ("linked_finding_reference", "linked_finding_title"),
        ("linked_applied_control_reference", "linked_applied_control_title"),
        ("linked_remediation_action_reference", "linked_remediation_action_title"),
    ):
        key = normalize_control_key(mapping.get(reference_field)) or normalize_control_key(
            mapping.get(title_field)
        )
        if key:
            return f"{reference_field}:{key}"
    return ""


def _restore_candidate_text(draft: dict[str, Any], registry: dict[str, dict[str, Any]]) -> None:
    """Replace framework control text with the candidate's own authoritative wording.

    The model only ever sees a shortened copy of each candidate, so a truncated excerpt is
    restored to the full existing text here. This runs after the guardrails, so it can only
    canonicalize text that has already been proven to come from a real candidate.
    """
    for mapping in draft.get("framework_control_mappings") or []:
        if not isinstance(mapping, dict):
            continue
        candidate = resolve_allowed_control(mapping, registry)
        if candidate is None:
            continue
        mapping["framework_control_title"] = candidate.get("title") or mapping.get(
            "framework_control_title", ""
        )
        mapping["framework_control_description"] = candidate.get("description") or ""
        if candidate.get("code"):
            mapping["framework_control_code"] = candidate["code"]
        # A mapping also resolves through its code or title, so a provider that mistypes the
        # reference still passes the guardrails and would hand Step 7B an identifier that
        # matches no requirement node. The candidate's own reference is authoritative.
        if candidate.get("reference"):
            mapping["framework_control_reference"] = candidate["reference"]


def _normalize_mapping(
    index: int,
    mapping: dict[str, Any],
    registry: dict[str, dict[str, Any]],
    framework_name: str,
) -> dict[str, Any]:
    """Fix harmless provider formatting and restore candidate-owned metadata.

    Whitespace, letter case on the mapping_type enum, numeric strings for confidence, and
    the positional temporary_id are normalized. Blank framework control metadata is filled
    from the resolved existing candidate so it can never be authored by the model. Missing
    or invalid substance (unknown control, rewritten clause text, unknown mapping_type,
    out-of-range confidence) is left untouched so the Step 7A guardrails reject it.
    """
    cleaned = {key: value for key, value in mapping.items() if key in ALLOWED_MAPPING_KEYS}

    for key in TEXT_MAPPING_KEYS:
        value = cleaned.get(key)
        if isinstance(value, str):
            cleaned[key] = value.strip()

    if not cleaned.get("temporary_id"):
        cleaned["temporary_id"] = f"framework_mapping_{index}"

    mapping_type = cleaned.get("mapping_type")
    if isinstance(mapping_type, str):
        lowered = mapping_type.strip().lower()
        cleaned["mapping_type"] = (
            lowered if lowered in MAPPING_TYPE_CHOICES else mapping_type.strip()
        )

    confidence = cleaned.get("confidence")
    if isinstance(confidence, str):
        try:
            cleaned["confidence"] = float(confidence.strip())
        except ValueError:
            pass

    evidence_needed = cleaned.get("evidence_needed")
    if isinstance(evidence_needed, list):
        cleaned["evidence_needed"] = [
            entry.strip() if isinstance(entry, str) else entry for entry in evidence_needed
        ]

    candidate = resolve_allowed_control(cleaned, registry)
    resolved_framework_name = ""
    if candidate is not None:
        if not cleaned.get("framework_control_reference"):
            cleaned["framework_control_reference"] = (
                candidate.get("reference") or candidate.get("code") or candidate.get("title") or ""
            )
        if not cleaned.get("framework_control_code"):
            cleaned["framework_control_code"] = candidate.get("code") or ""
        if candidate.get("title_is_generated") or not cleaned.get("framework_control_title"):
            # The candidate's own title wins: for export rows with a blank control name the
            # model may only propose a working label, never the authoritative title.
            cleaned["framework_control_title"] = candidate.get("title") or ""
        if not cleaned.get("framework_control_description"):
            cleaned["framework_control_description"] = candidate.get("description") or ""
        resolved_framework_name = (candidate.get("framework_name") or "").strip()

    if resolved_framework_name or framework_name:
        cleaned["framework_name"] = resolved_framework_name or framework_name

    for key in (
        "framework_control_code",
        "framework_control_description",
        "framework_name",
        *OPTIONAL_LINK_KEYS,
    ):
        if not isinstance(cleaned.get(key), str):
            cleaned[key] = ""

    if not cleaned.get("review_status"):
        cleaned["review_status"] = REVIEW_STATUS

    return cleaned


def _normalize_ambiguity_flags(value: Any) -> list[dict[str, str]]:
    """Coerce provider-supplied ambiguity flags into the {code, message} contract.

    Local providers sometimes return ambiguity_flags as bare strings, matching the
    normalization already applied in Steps 5A and 6A.
    """
    if not isinstance(value, list):
        return []

    normalized: list[dict[str, str]] = []
    for flag in value:
        if isinstance(flag, str):
            message = flag.strip()
            if message:
                normalized.append({"code": "provider_ambiguity", "message": message})
        elif isinstance(flag, dict):
            code = str(flag.get("code") or "provider_ambiguity").strip() or "provider_ambiguity"
            message = flag.get("message")
            if not isinstance(message, str) or not message.strip():
                message = str(flag.get("code") or "Ambiguity flagged by provider.")
            normalized.append({"code": code, "message": message.strip()})
        # Non-string, non-dict entries are dropped (treated as invalid).
    return normalized


def _refresh_overall_confidence(draft: dict[str, Any]) -> None:
    scores: list[float] = []
    for mapping in draft.get("framework_control_mappings") or []:
        if not isinstance(mapping, dict):
            continue
        score = mapping.get("confidence")
        if isinstance(score, (int, float)) and not isinstance(score, bool):
            if 0.0 <= float(score) <= 1.0:
                scores.append(float(score))
    draft["overall_confidence"] = round(sum(scores) / len(scores), 2) if scores else 0.0
