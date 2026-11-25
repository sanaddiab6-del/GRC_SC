"""SICO AI Pre-Assessment: verification and result rules.

This part is pure Python (no database, no model call) so every rule can be unit tested:

* a quote counts only if it is found verbatim in the objective the user typed;
* the observation is built by code from verified text only, never from free model text;
* Compliant and Not applicable can never be produced;
* a conditional requirement or an uncertain sentence never becomes Non-compliant.

The database write (Domain, Perimeter, Audit and results in one transaction) is added in
a later step of this feature.
"""
from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from datetime import date
from typing import Any, Iterable

from .pre_assessment_topics import CONTEXT_ONLY, TOPICS, is_uncertain

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
        quote = str(raw.get("quote") or "")
        verified = verify_quote(quote, objective)
        if verified is None:
            dropped.append({"reason": "quote_not_in_objective", "quote": quote[:80]})
            continue
        topics = tuple(
            t for t in dict.fromkeys(raw.get("topics") or [])
            if isinstance(t, str) and (t in TOPICS or t == CONTEXT_ONLY)
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
    requirement_conditional: bool,
    clause: str | None,
    requirement_text: str,
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
    return name[:NAME_MAX_CHARS]


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
