"""Pure text and decision rules for read-only, traceable GRC record discovery."""
from __future__ import annotations

import re


class DiscoveryInputError(ValueError):
    pass


def clean_hint(value: str | None, max_chars: int = 150) -> str:
    if value is None:
        return ""
    if not isinstance(value, str):
        raise DiscoveryInputError("A text hint must be a string.")
    return re.sub(r"\s+", " ", value).strip()[:max_chars]


def classify_name_match(name: str, hint: str) -> str:
    """Only exact names can ever be auto-selected; partial matches require review."""
    name, hint = clean_hint(name).casefold(), clean_hint(hint).casefold()
    if not name or not hint:
        return "none"
    if name == hint:
        return "exact"
    if hint in name or name in hint:
        return "possible"
    return "none"


def framework_terms(hint: str) -> list[str]:
    """Allow different versions and aliases to be candidates, never auto-approve them."""
    original = clean_hint(hint)
    words = re.findall(r"[A-Za-z0-9]+", original)
    ignored = {"the", "of", "and", "standard", "framework", "controls", "cybersecurity"}
    terms = []
    for word in words:
        if len(word) >= 3 and word.lower() not in ignored and word.lower() not in terms:
            terms.append(word.lower())
    return terms[:6]


def choose_single_exact_domain(matches: list[dict]) -> str | None:
    """Ambiguity cannot be hidden by selecting the first permitted folder."""
    exact = [x for x in matches if x.get("match") == "exact"]
    return exact[0]["id"] if len(exact) == 1 else None


def bounded_title(value: str | None, max_chars: int = 160) -> str:
    return clean_hint(value, max_chars)


def prepare_grounded_next_checks(domain_status: str, frameworks: list[dict], categories: dict) -> list[dict]:
    """Non-AI, non-compliance factual workflow prompts; no unsupported verdicts."""
    checks = []
    if domain_status == "no_readable_domain_match":
        checks.append({"priority": "review", "topic": "Organization", "message": "No readable matching organizational domain was found. Confirm spelling, access and company before proposing creation."})
    elif domain_status == "ambiguous_or_partial_match":
        checks.append({"priority": "review", "topic": "Organization", "message": "Multiple or partial organization candidates require a human choice. Do not create a duplicate or silently reuse a different company."})
    if not frameworks:
        checks.append({"priority": "review", "topic": "Framework", "message": "No readable framework candidate matched the input hint in the bounded search. Verify library access and naming before setup."})
    elif len(frameworks) > 1 or frameworks[0].get("match") != "exact":
        checks.append({"priority": "review", "topic": "Framework", "message": "Framework candidates need version, applicability and regulatory validation before assessment creation."})
    if domain_status in {"exact_existing_domain", "selected_possible_domain"}:
        for key, label in (
            ("perimeters", "scope / perimeter"),
            ("assets", "assets"),
            ("applied_controls", "applied controls"),
            ("policies", "policies"),
            ("evidences", "evidence records"),
        ):
            if not categories.get(key):
                checks.append({"priority": "investigate", "topic": label.title(), "message": f"No readable {label} were returned directly inside the selected domain. Check child domains and permissions before concluding none exist."})
    return checks
