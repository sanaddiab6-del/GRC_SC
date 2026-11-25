"""SICO AI Pre-Assessment: verification, result rules and the database write.

Everything except commit_pre_assessment is pure Python (no database, no model call), so
every rule can be unit tested:

* a quote counts only if it is found verbatim in the objective the user typed;
* the observation is built by code from verified text only, never from free model text;
* Compliant and Not applicable can never be produced;
* a conditional requirement or an uncertain sentence never becomes Non-compliant;
* an explicit result needs a quote that itself states a deficiency;
* the requirement's subject and the cited clause must be about what the quote shows;
* the final write re-runs every one of these checks; nothing the page sends back is
  trusted just because an earlier request produced it.

commit_pre_assessment writes Domain, Perimeter, a new Audit and the results in one
transaction.
"""
from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from datetime import date
from typing import Any, Iterable

from .pre_assessment_topics import (
    CONTEXT_ONLY,
    TOPICS,
    RequirementCandidate,
    is_uncertain,
    missing_anchors,
    shortlist_requirements,
    states_deficiency,
)

MAX_FACTS = 6
MIN_QUOTE_CHARS = 12
MAX_QUOTE_SHARE = 0.6
MAX_CLAIM_CHARS = 140
MAX_RESULTS_PER_FACT = 3
MAX_RESULTS_PER_RUN = 15
MAX_QUOTED_CHARS = 300
NAME_MAX_CHARS = 200

# What the judge model may answer for one requirement. Compliant and Not applicable are
# not in the list at all.
RELATIONS = ("not_related", "related_unknown", "gap_explicit", "partial_explicit")

KIND_NON_COMPLIANT = "non_compliant"
KIND_PARTIAL = "partially_compliant"
KIND_POTENTIAL_GAP = "potential_gap"
KIND_TO_BE_CONFIRMED = "to_be_confirmed"

# Platform RequirementAssessment values written for each kind. Only these results exist
# in this feature.
RESULT_FOR_KIND = {
    KIND_NON_COMPLIANT: "non_compliant",
    KIND_PARTIAL: "partially_compliant",
    KIND_POTENTIAL_GAP: "not_assessed",
    KIND_TO_BE_CONFIRMED: "not_assessed",
}
ALLOWED_RESULTS = frozenset(RESULT_FOR_KIND.values())
WRITTEN_STATUS = "in_review"

_KIND_STRENGTH = {
    KIND_NON_COMPLIANT: 3,
    KIND_PARTIAL: 2,
    KIND_POTENTIAL_GAP: 1,
    KIND_TO_BE_CONFIRMED: 0,
}


# --------------------------------------------------------------------------- text helpers

def _unify_characters(text: str) -> str:
    text = unicodedata.normalize("NFKC", text or "")
    return (
        text.replace("’", "'").replace("‘", "'")
        .replace("“", '"').replace("”", '"')
        .replace("–", "-").replace("—", "-").replace("‑", "-")
    )


def normalize_text(text: str) -> str:
    """NFKC, straight quotes and dashes, single spaces. Case is kept."""
    return re.sub(r"\s+", " ", _unify_characters(text)).strip()


def _normalize_keep_lines(text: str) -> str:
    """Like normalize_text, but line breaks stay: they end a sentence."""
    text = re.sub(r"[^\S\n]+", " ", _unify_characters(text))
    return re.sub(r" ?\n[\s]*", "\n", text).strip()


def normalize_name(name: str) -> str:
    """Organization / Domain name as stored: trimmed, single spaces."""
    return normalize_text(name)[:NAME_MAX_CHARS]


def name_key(name: str) -> str:
    """Comparison key: case and extra spaces do not make a different organization."""
    return normalize_name(name).casefold()


def _clean_quote(quote: str) -> str:
    quote = normalize_text(quote)
    return quote.strip(" \"'.,;:!?-")


def _find(needle: str, haystack: str) -> re.Match[str] | None:
    """Case-insensitive search; any run of spaces or line breaks matches any other."""
    if not needle:
        return None
    pattern = r"\s+".join(re.escape(part) for part in needle.split(" ") if part)
    return re.search(pattern, haystack, flags=re.IGNORECASE)


_SENTENCE_END = re.compile(r"[.!?؟](?=\s|$)|\n")


def sentence_around(text: str, start: int, end: int) -> str:
    """The whole sentence of `text` that contains text[start:end]."""
    left = 0
    for match in _SENTENCE_END.finditer(text, 0, start):
        left = match.end()
    right_match = _SENTENCE_END.search(text, end)
    right = right_match.end() if right_match else len(text)
    return text[left:right].strip()


def shorten(text: str, limit: int = MAX_QUOTED_CHARS) -> str:
    text = normalize_text(text)
    if len(text) <= limit:
        return text
    cut = text[: limit - 1]
    if " " in cut:
        cut = cut[: cut.rfind(" ")]
    return cut.rstrip(" ,;:-") + "…"


@dataclass(frozen=True)
class VerifiedQuote:
    quote: str  # the model's quote, cleaned, exactly as it appears in the objective
    sentence: str  # the full sentence of the objective that contains it


def verify_quote(quote: str, objective: str) -> VerifiedQuote | None:
    """Accept a quote only if it is in the objective verbatim (case and spacing aside).

    The returned sentence is what gets shown to people: a model cannot shorten
    "not sure if card numbers are saved" into "card numbers are saved" and have only the
    shortened part quoted.
    """
    text = _normalize_keep_lines(objective)
    cleaned = _clean_quote(quote)
    if len(cleaned) < MIN_QUOTE_CHARS:
        return None
    if text and len(cleaned) > MAX_QUOTE_SHARE * len(normalize_text(text)):
        return None
    match = _find(cleaned, text)
    if match is None:
        return None
    return VerifiedQuote(
        quote=normalize_text(text[match.start():match.end()]),
        sentence=normalize_text(sentence_around(text, match.start(), match.end())),
    )


def verify_clause(clause: str, requirement_text: str) -> str | None:
    """The part of the requirement the model says is not met, if it is really in it."""
    text = normalize_text(requirement_text)
    cleaned = _clean_quote(clause)
    if len(cleaned) < MIN_QUOTE_CHARS:
        return None
    match = _find(cleaned, text)
    if match is None:
        return None
    return text[match.start():match.end()]


# --------------------------------------------------------------------------- facts

@dataclass(frozen=True)
class VerifiedFact:
    index: int
    quote: str
    sentence: str
    claim: str  # model paraphrase, used for retrieval only and never stored
    topics: tuple[str, ...]
    uncertain: bool

    @property
    def judgeable(self) -> bool:
        return any(t != CONTEXT_ONLY for t in self.topics)

    @property
    def states_deficiency(self) -> bool:
        # Checked on the quote, not the whole sentence: one sentence can hold a neutral
        # fact and a deficiency ("runs on a hosting company server and ... the same admin
        # password since 2022").
        return states_deficiency(self.quote)


_FIELD_NAMES = ("quote", "claim_en", "topics", "certainty", "ref_id", "relation", "violated_clause", "reason")
_FIELD_BY_SIMPLE_KEY = {re.sub(r"[^a-z]", "", name): name for name in _FIELD_NAMES}


def item_fields(raw: dict) -> dict[str, Any]:
    """The known fields of one model item, whatever spacing or case the model used for the
    keys (seen: "ref- id"). Unknown keys are dropped."""
    fields: dict[str, Any] = {}
    for key, value in raw.items():
        name = _FIELD_BY_SIMPLE_KEY.get(re.sub(r"[^a-z]", "", str(key).lower()))
        if name and name not in fields:
            fields[name] = value
    return fields


def _topic_name(value: Any) -> str:
    """The topic name the model meant: it sometimes answers "authentication_passwords:
    password" instead of the bare name. Only names in the closed list are accepted after."""
    if not isinstance(value, str):
        return ""
    return value.split(":", 1)[0].strip().lower()


def verify_facts(raw_facts: Any, objective: str) -> tuple[list[VerifiedFact], list[dict[str, str]]]:
    """Keep only facts whose quote is in the objective; return (facts, dropped)."""
    facts: list[VerifiedFact] = []
    dropped: list[dict[str, str]] = []
    seen: set[tuple[str, tuple[str, ...]]] = set()
    if not isinstance(raw_facts, list):
        return facts, [{"reason": "facts_not_a_list", "quote": ""}]

    for raw in raw_facts:
        if len(facts) >= MAX_FACTS:
            dropped.append({"reason": "too_many_facts", "quote": str((raw or {}).get("quote", ""))[:80]})
            continue
        if not isinstance(raw, dict):
            dropped.append({"reason": "fact_not_an_object", "quote": ""})
            continue
        raw = item_fields(raw)
        quote = str(raw.get("quote") or "")
        verified = verify_quote(quote, objective)
        if verified is None:
            dropped.append({"reason": "quote_not_in_objective", "quote": quote[:80]})
            continue
        topics = tuple(
            t for t in dict.fromkeys(_topic_name(t) for t in (raw.get("topics") or []))
            if t in TOPICS or t == CONTEXT_ONLY
        )[:2]
        if not topics:
            dropped.append({"reason": "no_known_topic", "quote": quote[:80]})
            continue
        key = (verified.sentence.casefold(), topics)
        if key in seen:
            dropped.append({"reason": "duplicate_fact", "quote": quote[:80]})
            continue
        seen.add(key)
        model_uncertain = str(raw.get("certainty") or "").strip().lower() != "stated"
        facts.append(
            VerifiedFact(
                index=len(facts),
                quote=verified.quote,
                sentence=verified.sentence,
                claim=normalize_text(str(raw.get("claim_en") or ""))[:MAX_CLAIM_CHARS],
                topics=topics,
                # The code decides too: an uncertain sentence stays uncertain whatever
                # the model says.
                uncertain=model_uncertain or is_uncertain(verified.sentence),
            )
        )
    return facts, dropped


# --------------------------------------------------------------------------- outcomes

@dataclass(frozen=True)
class Outcome:
    kind: str
    clause: str | None = None

    @property
    def result(self) -> str:
        return RESULT_FOR_KIND[self.kind]

    @property
    def status(self) -> str:
        return WRITTEN_STATUS

    @property
    def strength(self) -> int:
        return _KIND_STRENGTH[self.kind]


def decide_outcome(
    relation: str,
    *,
    fact_uncertain: bool,
    fact_states_deficiency: bool,
    requirement_conditional: bool,
    clause: str | None,
    requirement_text: str,
    requirement_subject: str,
    fact_quote: str,
) -> Outcome | None:
    """Turn the judge's answer for one requirement into what may be written.

    The model only says how the fact relates; the code decides the result.
    """
    if relation not in RELATIONS or relation == "not_related":
        return None
    if relation == "related_unknown" or fact_uncertain:
        return Outcome(KIND_TO_BE_CONFIRMED)
    verified_clause = verify_clause(clause or "", requirement_text)
    if verified_clause is None:
        return Outcome(KIND_TO_BE_CONFIRMED)
    if not fact_states_deficiency:
        # The quote states no deficiency: neither a finding nor a Potential gap.
        return Outcome(KIND_TO_BE_CONFIRMED)
    if missing_anchors(requirement_subject, verified_clause, fact_quote):
        # The requirement or the cited clause is about something the quote does not show
        # (another account type, a committee instead of a team, MFA never mentioned).
        return Outcome(KIND_TO_BE_CONFIRMED)
    if requirement_conditional:
        return Outcome(KIND_POTENTIAL_GAP, verified_clause)
    if relation == "gap_explicit":
        return Outcome(KIND_NON_COMPLIANT, verified_clause)
    return Outcome(KIND_PARTIAL, verified_clause)


@dataclass(frozen=True)
class PlannedResult:
    requirement_key: str
    ref_id: str
    fact_index: int
    rank: int  # position in the fact's short list
    outcome: Outcome
    sentence: str


def apply_caps(
    planned: Iterable[PlannedResult],
    per_fact: int = MAX_RESULTS_PER_FACT,
    per_run: int = MAX_RESULTS_PER_RUN,
) -> list[PlannedResult]:
    """One result per requirement (the strongest), at most per_fact per fact and per_run
    in total. Stronger results and earlier facts are kept first."""
    best: dict[str, PlannedResult] = {}
    for item in planned:
        current = best.get(item.requirement_key)
        if current is None or (
            (-item.outcome.strength, item.fact_index, item.rank)
            < (-current.outcome.strength, current.fact_index, current.rank)
        ):
            best[item.requirement_key] = item

    ordered = sorted(best.values(), key=lambda p: (-p.outcome.strength, p.fact_index, p.rank))
    kept: list[PlannedResult] = []
    per_fact_count: dict[int, int] = {}
    for item in ordered:
        if len(kept) >= per_run:
            break
        if per_fact_count.get(item.fact_index, 0) >= per_fact:
            continue
        per_fact_count[item.fact_index] = per_fact_count.get(item.fact_index, 0) + 1
        kept.append(item)
    return kept


def plan_fact_results(
    fact: VerifiedFact,
    shortlist: list[RequirementCandidate],
    judgements: Any,
) -> tuple[list[PlannedResult], list[dict[str, str]]]:
    """Apply the code's rules to the judge's raw answer for one fact.

    Only requirements of the fact's own short list are accepted, each once; an unknown
    relation (including "compliant" or "not_applicable") is ignored. Returns (results,
    ignored items).
    """
    if not isinstance(judgements, list):
        return [], [{"reason": "judgements_not_a_list", "ref_id": ""}]
    by_ref = {c.ref_id: (rank, c) for rank, c in enumerate(shortlist)}
    planned: list[PlannedResult] = []
    ignored: list[dict[str, str]] = []
    seen: set[str] = set()
    for raw in judgements:
        if not isinstance(raw, dict):
            ignored.append({"reason": "judgement_not_an_object", "ref_id": ""})
            continue
        raw = item_fields(raw)
        ref = normalize_text(str(raw.get("ref_id") or ""))
        if ref not in by_ref:
            ignored.append({"reason": "ref_not_in_short_list", "ref_id": ref[:40]})
            continue
        if ref in seen:
            ignored.append({"reason": "duplicate_judgement", "ref_id": ref[:40]})
            continue
        seen.add(ref)
        relation = normalize_text(str(raw.get("relation") or "")).lower()
        if relation not in RELATIONS:
            ignored.append({"reason": "unknown_relation", "ref_id": ref[:40]})
            continue
        rank, candidate = by_ref[ref]
        outcome = decide_outcome(
            relation,
            fact_uncertain=fact.uncertain,
            fact_states_deficiency=fact.states_deficiency,
            requirement_conditional=candidate.conditional,
            clause=str(raw.get("violated_clause") or ""),
            requirement_text=candidate.text,
            requirement_subject=candidate.subject,
            fact_quote=fact.quote,
        )
        if outcome is not None:
            planned.append(PlannedResult(candidate.key, candidate.ref_id, fact.index, rank, outcome, fact.sentence))
    return apply_caps(planned, per_fact=MAX_RESULTS_PER_FACT, per_run=MAX_RESULTS_PER_FACT), ignored


def build_observation(outcome: Outcome, *, model: str, day: date, sentence: str) -> str:
    """Observation text, built by code from verified text only."""
    prefix = f"[SICO AI · {model} · {day.isoformat()}]"
    said = shorten(sentence)
    if outcome.kind == KIND_NON_COMPLIANT:
        return f'{prefix} Non-compliant: requirement says "{shorten(outcome.clause or "")}" — objective says "{said}"'
    if outcome.kind == KIND_PARTIAL:
        return f'{prefix} Partially compliant: requirement says "{shorten(outcome.clause or "")}" — objective says "{said}"'
    if outcome.kind == KIND_POTENTIAL_GAP:
        return f'{prefix} Potential gap: conditional requirement; its condition is not stated in the objective — "{said}"'
    return f'{prefix} To be confirmed: related to the objective but not stated clearly — "{said}"'


def summarize(results: Iterable[PlannedResult], assessable_total: int) -> dict[str, int]:
    counts = {kind: 0 for kind in RESULT_FOR_KIND}
    for item in results:
        counts[item.outcome.kind] += 1
    written = sum(counts.values())
    counts["not_assessed_untouched"] = max(0, assessable_total - written)
    return counts


# --------------------------------------------------------------------------- names and ids

_SLUG = re.compile(r"[a-z0-9]+(?:[-_][a-z0-9]+)*")


def framework_label(name: str, ref_id: str | None) -> str:
    """Short framework label: its ref_id when it reads like one ("PCI DSS 4.0.1"),
    otherwise its name (ECC's ref_id is the slug "essential-cybersecurity-controls")."""
    ref = normalize_text(ref_id or "")
    if ref and not _SLUG.fullmatch(ref):
        return ref
    return normalize_text(name)


def perimeter_name(organization: str, framework_name: str, framework_ref_id: str | None) -> str:
    name = f"{normalize_name(organization)} – {framework_label(framework_name, framework_ref_id)} scope"
    # The platform refuses "/" in a Perimeter name (PerimeterWriteSerializer.validate_name).
    return name.replace("/", "-")[:NAME_MAX_CHARS]


def perimeter_description(sentences: Iterable[str]) -> str:
    lines = ["Scope drafted by SICO AI Pre-Assessment from the case objective — to be confirmed."]
    for sentence in dict.fromkeys(shorten(s) for s in sentences if s):
        lines.append(f'• "{sentence}"')
    lines.append("Anything not quoted above is not stated in the objective.")
    return "\n".join(lines)


def audit_description(*, model: str, day: date, sentences: Iterable[str]) -> str:
    lines = [
        f"SICO AI Pre-Assessment · {model} · {day.isoformat()}",
        "Preliminary gap analysis from the case objective only — not a formal audit; "
        "every result needs human review.",
    ]
    quoted = list(dict.fromkeys(shorten(s) for s in sentences if s))
    if quoted:
        lines.append("Facts used:")
        lines.extend(f'• "{s}"' for s in quoted)
    return "\n".join(lines)


_LEADING_INT = re.compile(r"^\s*v?(\d+)", re.IGNORECASE)


def next_version(existing_versions: Iterable[str | None]) -> str:
    """Highest whole number among existing versions, plus one ("1.1" counts as 1)."""
    highest = 0
    for value in existing_versions:
        match = _LEADING_INT.match(str(value or ""))
        if match:
            highest = max(highest, int(match.group(1)))
    return f"{highest + 1}.0"


AUDIT_REF_PREFIX = "SICO-AUD"
_AUDIT_REF = re.compile(r"^\s*SICO-AUD-(\d{4})-(\d{4,})\s*$", re.IGNORECASE)


def next_audit_ref_id(year: int, existing_ref_ids: Iterable[str | None]) -> str:
    """SICO-AUD-YYYY-NNNN; the number restarts at 0001 every year and counts ids typed
    by hand in the same format."""
    highest = 0
    for value in existing_ref_ids:
        match = _AUDIT_REF.match(str(value or ""))
        if match and int(match.group(1)) == year:
            highest = max(highest, int(match.group(2)))
    return f"{AUDIT_REF_PREFIX}-{year:04d}-{highest + 1:04d}"


# --------------------------------------------------------------------------- the whole run

def plan_run(
    facts: list[VerifiedFact],
    candidates: list[RequirementCandidate],
    judgements_by_fact: dict[int, Any],
) -> list[PlannedResult]:
    """Re-run every rule for every fact with the judge answers the page sent back.

    The short list is rebuilt here, so a judgement for a requirement outside the fact's
    own short list is ignored. Caps apply across the whole run.
    """
    planned: list[PlannedResult] = []
    for fact in facts:
        items = judgements_by_fact.get(fact.index)
        if not fact.judgeable or not items:
            continue
        shortlist = shortlist_requirements(candidates, fact.topics, fact.claim)
        results, _ignored = plan_fact_results(fact, shortlist, items)
        planned.extend(results)
    return apply_caps(planned)


# --------------------------------------------------------------------------- database write
#
# Django models are imported inside the function so the rules above stay importable (and
# testable) without a configured database.

# One lock for every pre-assessment write: version and SICO-AUD number are computed and
# used inside it, so two clicks at the same moment cannot get the same values.
ADVISORY_LOCK_KEY = 0x51C0A1A55E55
ORGANIZATION_REFUSAL = (
    "You do not have permission to create or use this organization in SICO. "
    "Ask an administrator."
)


class PreAssessmentRefused(Exception):
    def __init__(self, code: str, detail: str, status: int = 403):
        super().__init__(code)
        self.code = code
        self.detail = detail
        self.status = status


def _allowed(user, codename: str, folder) -> bool:
    from django.contrib.auth.models import Permission
    from iam.models import RoleAssignment

    permission = Permission.objects.filter(codename=codename).first()
    return permission is not None and RoleAssignment.is_access_allowed(user, permission, folder)


def _refuse_organization() -> None:
    # Same answer whether the Domain exists but is not readable, or cannot be created:
    # the message never tells a user that an organization they cannot see exists.
    raise PreAssessmentRefused("organization_unavailable", ORGANIZATION_REFUSAL)


def commit_pre_assessment(
    *,
    request,
    framework,
    organization: str,
    facts: list[VerifiedFact],
    results: list[PlannedResult],
    model: str,
    day: date,
) -> dict[str, Any]:
    """Create Domain (if needed), Perimeter (if needed), a new Audit and its results.

    Everything happens in one transaction: any failure leaves nothing behind. The Audit is
    always new, so no Audit made by a person is ever changed.
    """
    from django.db import connection, transaction

    from core.models import ComplianceAssessment, Perimeter, RequirementAssessment
    from core.serializers import (
        ComplianceAssessmentWriteSerializer,
        FolderWriteSerializer,
        PerimeterWriteSerializer,
        RequirementAssessmentWriteSerializer,
    )
    from iam.models import Folder, RoleAssignment

    user = request.user
    context = {"request": request}
    org = normalize_name(organization)
    sentences = [f.sentence for f in facts]
    created: dict[str, bool] = {"domain": False, "perimeter": False}

    with transaction.atomic():
        if connection.vendor == "postgresql":
            with connection.cursor() as cursor:
                cursor.execute("SELECT pg_advisory_xact_lock(%s)", [ADVISORY_LOCK_KEY])

        # Domain: the organization's name, ignoring case and extra spaces.
        root = Folder.get_root_folder()
        domain = next(
            (f for f in Folder.objects.filter(parent_folder=root, content_type=Folder.ContentType.DOMAIN)
             if name_key(f.name) == name_key(org)),
            None,
        )
        if domain is not None:
            if not RoleAssignment.is_object_readable(user, Folder, domain.id):
                _refuse_organization()
        else:
            if not _allowed(user, "add_folder", root):
                _refuse_organization()
            # Same as creating a Domain from the platform's own form.
            serializer = FolderWriteSerializer(
                data={"name": org, "parent_folder": str(root.id), "create_iam_groups": True}, context=context
            )
            serializer.is_valid(raise_exception=True)
            domain = serializer.save()
            Folder.create_default_ug_and_ra(domain)
            created["domain"] = True
        for codename in ("add_complianceassessment", "change_requirementassessment"):
            if not _allowed(user, codename, domain):
                _refuse_organization()

        # Perimeter: one per framework, reused on the next click; its description is
        # never rewritten.
        wanted_perimeter = perimeter_name(org, str(framework.name), framework.ref_id)
        perimeter = next(
            (p for p in Perimeter.objects.filter(folder=domain) if name_key(p.name) == name_key(wanted_perimeter)),
            None,
        )
        if perimeter is not None:
            if not RoleAssignment.is_object_readable(user, Perimeter, perimeter.id):
                _refuse_organization()
        else:
            if not _allowed(user, "add_perimeter", domain):
                _refuse_organization()
            serializer = PerimeterWriteSerializer(
                data={"folder": str(domain.id), "name": wanted_perimeter,
                      "description": perimeter_description(sentences)},
                context=context,
            )
            serializer.is_valid(raise_exception=True)
            perimeter = serializer.save()
            created["perimeter"] = True

        # Audit: always new. Version and SICO-AUD number are computed under the lock.
        versions = [a.version for a in ComplianceAssessment.objects.filter(perimeter=perimeter)
                    if name_key(a.name) == name_key(org)]
        ref_ids = ComplianceAssessment.objects.filter(
            ref_id__istartswith=f"{AUDIT_REF_PREFIX}-{day.year:04d}-"
        ).values_list("ref_id", flat=True)
        serializer = ComplianceAssessmentWriteSerializer(
            data={
                "folder": str(domain.id),
                "perimeter": str(perimeter.id),
                "framework": str(framework.id),
                "name": org,
                "version": next_version(versions),
                "ref_id": next_audit_ref_id(day.year, ref_ids),
                "status": "in_progress",
                "description": audit_description(model=model, day=day, sentences=sentences),
            },
            context=context,
        )
        serializer.is_valid(raise_exception=True)
        audit = serializer.save()
        audit.create_requirement_assessments()

        # Results, through the platform's own serializer and its write rules.
        rows = {
            str(ra.requirement_id): ra
            for ra in RequirementAssessment.objects.select_for_update().filter(
                compliance_assessment=audit,
                requirement_id__in=[r.requirement_key for r in results],
                requirement__assessable=True,
                selected=True,
            )
        }
        written: list[tuple[PlannedResult, Any, str]] = []
        skipped: list[str] = []
        for item in results:
            row = rows.get(item.requirement_key)
            if row is None:
                skipped.append(item.ref_id)
                continue
            observation = build_observation(item.outcome, model=model, day=day, sentence=item.sentence)
            serializer = RequirementAssessmentWriteSerializer(
                instance=row,
                data={"result": item.outcome.result, "status": item.outcome.status, "observation": observation},
                partial=True,
                context=context,
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            written.append((item, row.pk, observation))

        # Read back: exactly what was planned was saved, and nothing else in the Audit moved.
        for item, pk, observation in written:
            row = RequirementAssessment.objects.get(pk=pk)
            if (row.result, row.status, row.observation) != (item.outcome.result, item.outcome.status, observation):
                raise RuntimeError("persisted_state_mismatch")
        touched = RequirementAssessment.objects.filter(compliance_assessment=audit).exclude(
            result=RequirementAssessment.Result.NOT_ASSESSED, status=RequirementAssessment.Status.TODO
        ).count()
        if touched != len(written):
            raise RuntimeError("persisted_state_mismatch")
        assessable_total = RequirementAssessment.objects.filter(
            compliance_assessment=audit, requirement__assessable=True, selected=True
        ).count()

    return {
        "audit": {"id": str(audit.id), "name": audit.name, "version": audit.version, "ref_id": audit.ref_id,
                  "status": audit.status, "url": f"/compliance-assessments/{audit.id}"},
        "domain": {"id": str(domain.id), "name": domain.name, "created": created["domain"]},
        "perimeter": {"id": str(perimeter.id), "name": perimeter.name, "created": created["perimeter"]},
        "summary": summarize([w[0] for w in written], assessable_total),
        "results": [{"ref_id": w[0].ref_id, "kind": w[0].outcome.kind, "result": w[0].outcome.result}
                    for w in written],
        "not_in_audit": skipped,
    }
