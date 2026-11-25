"""SICO AI Pre-Assessment: closed topic list, requirement retrieval and text detectors.

Pure Python: no database, no Django settings and no model call. The model only labels each
fact with topics from TOPIC_ENUM; this module turns those topics into a short list of
framework requirements with a deterministic keyword search, so the same fact always gives
the same short list.
"""
from __future__ import annotations

import math
import re
import unicodedata
from dataclasses import dataclass
from typing import Iterable

CONTEXT_ONLY = "context_only"

# Synonyms are matched against the English requirement text of the selected framework.
# A term ending in "*" is a prefix ("encrypt*" matches "encryption"); every other term must
# match whole words. Keep terms specific: a short prefix such as "log*" would also match
# "logical" and "login".
TOPICS: dict[str, tuple[str, ...]] = {
    "authentication_passwords": (
        "password*", "passphrase*", "credential*", "authentication factor*",
        "default password*", "login", "log-on", "logon", "user authentication",
        # Password age / rotation: "the same password since 2022" is about these.
        "changed at least", "changed periodically", "rotat*", "password change*",
        "password age", "expir*",
    ),
    "mfa": (
        "multi-factor", "multi factor", "mfa", "two-factor", "2fa",
        "one-time password*", "otp",
    ),
    "access_control": (
        "access control*", "access right*", "least privilege", "need-to-know",
        "need to know", "privileged", "administrator*", "admin", "user account*",
        "access review*", "authoriz*", "shared account*", "generic id*", "shared id*",
        "group, shared", "identity and access",
    ),
    "sensitive_data_storage": (
        "cardholder data", "account data", "pan", "primary account number*", "card number*",
        "stor*", "retention", "retain*", "sensitive authentication data", "personal data",
        "personally identifiable", "pii", "privacy", "confidential*", "classif*",
        "trade secret*", "intellectual property",
    ),
    "encryption_keys": (
        "encrypt*", "cryptograph*", "key management", "cryptographic key*", "tls",
        "transmission*", "unreadable", "hash*", "tokeniz*", "truncat*",
    ),
    "third_party_providers": (
        "third-part*", "third part*", "service provider*", "tpsp*", "supplier*", "vendor*",
        "hosting", "cloud", "outsourc*", "contract*", "agreement*", "managed service*",
    ),
    "payment_terminals": (
        "poi", "point of interaction", "payment terminal*", "card-reading device*",
        "tamper*", "skimm*", "substitution", "pos",
    ),
    "web_application_security": (
        "web application*", "website*", "public-facing", "payment page*", "script*",
        "e-commerce", "web application firewall", "injection",
    ),
    "network_security": (
        "network security control*", "firewall*", "segmentation", "dmz", "wireless",
        "router*", "network diagram*", "data flow*", "network",
    ),
    "vulnerability_patching": (
        "vulnerabilit*", "patch*", "security update*", "scan*", "penetration test*", "asv",
        "malware", "anti-malware",
    ),
    "secure_configuration": (
        "configuration standard*", "hardening", "harden*", "default setting*", "baseline*",
        "system component*", "configuration*",
    ),
    "logging_monitoring": (
        "log", "logs", "logging", "audit log*", "audit trail*", "monitor*", "alert*",
        "siem", "time synchroni*", "event log*",
    ),
    "incident_response": (
        "incident*", "breach*", "response plan*", "compromise*", "forensic*",
    ),
    "asset_inventory": (
        "inventory", "inventories", "asset*", "hardware", "software",
    ),
    "governance_policy": (
        "polic*", "procedure*", "roles and responsibilities", "approved", "management",
        "strategy", "strategies", "roadmap", "isms", "scope", "cybersecurity function",
        "information security function", "steering committee", "independent", "compliance",
    ),
    "risk_management": (
        "risk assessment*", "targeted risk analysis", "risk treatment", "risk register*",
        "risk management", "risk*",
    ),
    "awareness_training": (
        "awareness", "training", "trained", "phishing", "personnel", "staff", "education",
        "skill*",
    ),
    "physical_security": (
        "physical", "facilit*", "premises", "visitor*", "media", "cctv", "secure area*",
        "server room*",
    ),
    "backup_continuity": (
        "backup*", "back-up*", "recovery", "restor*", "continuity", "disaster",
        "resilien*", "availability",
    ),
    "secure_development": (
        "software development", "developer*", "development", "change management",
        "code review*", "bespoke", "custom software", "testing environment*", "change control",
    ),
    "endpoint_devices": (
        "endpoint*", "laptop*", "workstation*", "mobile device*", "removable media",
        "byod", "bring your own device",
    ),
}

TOPIC_ENUM: tuple[str, ...] = (*TOPICS.keys(), CONTEXT_ONLY)

SHORTLIST_SIZE = 6

# Weights: a topic synonym says more than a word the model wrote in its paraphrase, and a
# hit in the requirement itself says more than a hit only in its section heading.
_TOPIC_WEIGHT = 3.0
_CLAIM_WEIGHT = 1.5
_CONTEXT_FACTOR = 0.5
_DECAY = 0.5
# Only the presence of a term counts, not how often it appears, so a long requirement is
# not favoured and needs no length penalty (a penalty pushed down long but exact
# requirements such as ECC 1-2-1). The diminishing weight inside a topic is what stops a
# long requirement from winning by listing many broad synonyms.

_STOPWORDS = frozenset(
    """
    about above after again against also always among another because been before being
    below between both cannot could does doing down during each every from further have
    having here into itself just many more most must never other ours over same should
    some such than that their them then there these they this those through under until
    very were what when where which while whom with would your yours company companies
    organization organisation business still since using used uses want need needs asked
    sure whether maybe think perhaps probably possibly unsure unclear known
    """.split()
)

_WORD_RE = re.compile(r"[a-z0-9][a-z0-9\-]*")


def _fold(text: str) -> str:
    text = unicodedata.normalize("NFKC", text or "")
    text = (
        text.replace("’", "'").replace("‘", "'")
        .replace("“", '"').replace("”", '"')
        .replace("–", "-").replace("—", "-").replace("‑", "-")
    )
    return re.sub(r"\s+", " ", text).strip().lower()


def _term_pattern(term: str) -> re.Pattern[str]:
    term = term.lower()
    if term.endswith("*"):
        return re.compile(r"(?<![a-z0-9])" + re.escape(term[:-1]))
    return re.compile(r"(?<![a-z0-9])" + re.escape(term) + r"(?![a-z0-9])")


_TOPIC_PATTERNS: dict[str, tuple[tuple[str, re.Pattern[str]], ...]] = {
    topic: tuple((term, _term_pattern(term)) for term in terms) for topic, terms in TOPICS.items()
}


@dataclass(frozen=True)
class RequirementCandidate:
    """One assessable requirement of the selected framework, as plain data."""

    key: str  # RequirementAssessment / RequirementNode id, or any stable id in tests
    ref_id: str
    text: str  # name + description of the requirement itself
    context: str = ""  # names and descriptions of its parent sections
    has_assessable_children: bool = False
    order: int = 0  # position in the framework, used only to break ties


@dataclass
class _Indexed:
    candidate: RequirementCandidate
    text: str
    context: str


def build_candidates(nodes: Iterable[dict]) -> list[RequirementCandidate]:
    """Turn framework nodes into candidates.

    Each node is a dict with urn, parent_urn, assessable, ref_id, name and description (the
    shape of RequirementNode rows and of library YAML nodes). Parent sections become the
    context of their children; a node with assessable children is kept but flagged, because
    the children are the specific requirements.
    """
    nodes = list(nodes)
    by_urn = {n.get("urn"): n for n in nodes if n.get("urn")}
    has_assessable_child: set[str] = set()
    for n in nodes:
        parent = n.get("parent_urn")
        if parent and n.get("assessable"):
            has_assessable_child.add(parent)

    candidates: list[RequirementCandidate] = []
    for order, n in enumerate(nodes):
        if not n.get("assessable"):
            continue
        context_parts: list[str] = []
        parent = by_urn.get(n.get("parent_urn"))
        seen: set[str] = set()
        while parent is not None and parent.get("urn") not in seen:
            seen.add(parent.get("urn"))
            context_parts.append(" ".join(filter(None, [parent.get("name"), parent.get("description")])))
            parent = by_urn.get(parent.get("parent_urn"))
        candidates.append(
            RequirementCandidate(
                key=str(n.get("key") or n.get("id") or n.get("urn") or n.get("ref_id")),
                ref_id=str(n.get("ref_id") or ""),
                text=" ".join(filter(None, [n.get("name"), n.get("description")])),
                context=" ".join(context_parts),
                has_assessable_children=n.get("urn") in has_assessable_child,
                order=order,
            )
        )
    return candidates


def _claim_terms(claim: str) -> list[str]:
    words = _WORD_RE.findall(_fold(claim))
    terms: list[str] = []
    for word in words:
        word = word.strip("-")
        if len(word) < 4 or word in _STOPWORDS or word.isdigit():
            continue
        if word not in terms:
            terms.append(word)
    return terms


def _diminishing(weights: list[float]) -> float:
    """Best hit counts fully, the next one half, then a quarter, and so on."""
    return sum(w * (_DECAY ** i) for i, w in enumerate(sorted(weights, reverse=True)))


def shortlist_requirements(
    candidates: list[RequirementCandidate],
    topics: Iterable[str],
    claim: str = "",
    k: int = SHORTLIST_SIZE,
) -> list[RequirementCandidate]:
    """Return at most k requirements for one fact, best first, deterministic.

    Parent requirements whose assessable children exist are skipped in favour of the
    children. A fact labelled only context_only gets an empty list.
    """
    topic_list = [t for t in dict.fromkeys(topics) if t in TOPICS]
    if not topic_list:
        return []

    indexed = [
        _Indexed(c, _fold(c.text), _fold(c.context))
        for c in candidates
        if not c.has_assessable_children
    ]
    if not indexed:
        return []
    total = len(indexed)

    # One group per topic, and one group per word of the model's paraphrase. Inside a topic
    # group the hits are summed with diminishing weight, so a long requirement that happens
    # to contain many broad synonyms ("approved", "management", "scope") does not beat a
    # requirement that matches the specific words of the fact.
    groups: list[list[tuple[re.Pattern[str], float]]] = []
    for topic in topic_list:
        groups.append([(pattern, _TOPIC_WEIGHT) for _term, pattern in _TOPIC_PATTERNS[topic]])
    for word in _claim_terms(claim):
        groups.append([(_term_pattern(word), _CLAIM_WEIGHT)])

    # Inverse document frequency over this framework only: a word found in every
    # requirement ("cybersecurity" in ECC) carries almost no weight.
    weighted: list[list[tuple[re.Pattern[str], float]]] = []
    for group in groups:
        kept: list[tuple[re.Pattern[str], float]] = []
        for pattern, weight in group:
            df = sum(1 for i in indexed if pattern.search(i.text) or pattern.search(i.context))
            if df == 0:
                continue
            idf = math.log(1.0 + (total - df + 0.5) / (df + 0.5))
            kept.append((pattern, weight * idf))
        if kept:
            weighted.append(kept)

    scored: list[tuple[float, int, RequirementCandidate]] = []
    for item in indexed:
        own = 0.0
        ctx = 0.0
        for group in weighted:
            own_hits: list[float] = []
            ctx_hits: list[float] = []
            for pattern, weight in group:
                if pattern.search(item.text):
                    own_hits.append(weight)
                elif pattern.search(item.context):
                    ctx_hits.append(weight * _CONTEXT_FACTOR)
            own += _diminishing(own_hits)
            ctx += _diminishing(ctx_hits)
        if own <= 0 and ctx <= 0:
            continue
        scored.append((own + ctx, item.candidate.order, item.candidate))

    scored.sort(key=lambda row: (-row[0], row[1]))
    return [row[2] for row in scored[:k]]


# Conditional requirements: "If passwords are used as the only factor..." cannot be
# judged non-compliant unless the condition itself is stated, so these become a
# Potential gap.
_CONDITIONAL_START = re.compile(r"^\W*(if|where|when|in case)\b", re.IGNORECASE)
_CONDITIONAL_ANYWHERE = re.compile(
    r"\b(where applicable|if applicable|when applicable|where relevant|if used|where used)\b",
    re.IGNORECASE,
)


def is_conditional_requirement(text: str) -> bool:
    folded = _fold(text)
    return bool(_CONDITIONAL_START.search(folded) or _CONDITIONAL_ANYWHERE.search(folded))


# Uncertainty in the objective: a fact from such a sentence can never become a
# Non-compliant or Partially compliant result.
_UNCERTAIN = re.compile(
    r"(\bnot sure\b|\bunsure\b|\bnot certain\b|\buncertain\b|\bi think\b|\bi guess\b"
    r"|\bwe think\b|\bmaybe\b|\bmay be\b|\bperhaps\b|\bprobably\b|\bpossibly\b|\bmight\b"
    r"|\bdon'?t know\b|\bdo not know\b|\bno idea\b|\bunclear\b|\bnot clear\b|\bnot known\b"
    r"|\bunknown\b|\bnot confirmed\b|\bto be confirmed\b"
    r"|لست متأكد|مش متأكد|مو متأكد|مش متاكد|لست متاكد|ما بعرف|ما نعرف|لا أعرف|لا اعرف"
    r"|لا نعرف|يمكن|ربما|أظن|اظن|نظن|على ما أعتقد|على ما اعتقد|غير متأكد|غير متاكد|غير واضح)",
    re.IGNORECASE,
)


def is_uncertain(text: str) -> bool:
    return bool(_UNCERTAIN.search(_fold(text)))
