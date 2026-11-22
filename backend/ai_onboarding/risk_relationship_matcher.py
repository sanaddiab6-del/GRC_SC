"""Read-only, deterministic suggestions for existing risk relationships.

This does not establish a vulnerability, probability, impact, or risk treatment.
It does not call a language model. The caller must pre-filter candidates by
folder and enforce per-object permissions before calling the matcher.
"""
from __future__ import annotations

import re

STOPWORDS = frozenset({
    'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'could', 'for', 'from', 'has',
    'have', 'in', 'into', 'is', 'it', 'its', 'may', 'of', 'on', 'or', 'our', 'that',
    'the', 'their', 'this', 'to', 'via', 'was', 'were', 'will', 'with', 'without',
    'actors', 'system', 'systems', 'environment', 'risk', 'scenario', 'potential',
    'could', 'gain', 'cause', 'leading', 'result', 'employees', 'due', 'lack',
})


def normalized_tokens(value: str) -> set[str]:
    text = (value or '').lower()
    text = re.sub(r'\bmfa\b', 'multi factor authentication', text)
    text = re.sub(r'\b2fa\b', 'multi factor authentication', text)
    text = re.sub(r'\blog[ -]?in\b', 'authentication', text)
    text = re.sub(r'\bunauthori[sz]ed\b', 'unauthorized access', text)
    text = re.sub(r'[^a-z0-9]+', ' ', text)
    return {token for token in text.split() if len(token) > 2 and token not in STOPWORDS}


def advisory_line(description: str, label: str) -> str:
    match = re.search(r'^' + re.escape(label) + r':\s*(.+)$', description or '', re.I | re.M)
    return match.group(1).strip()[:500] if match else ''


def match_candidates(advisory: str, candidates: list[dict], max_results: int = 5) -> list[dict]:
    """Only return lexical candidates; do not claim semantic or evidence verification."""
    if not advisory.strip():
        return []
    wanted = normalized_tokens(advisory)
    if not wanted:
        return []
    matches = []
    for item in candidates:
        name_tokens = normalized_tokens(item.get('name', ''))
        desc_tokens = normalized_tokens(item.get('description', ''))
        name_hits = wanted & name_tokens
        description_hits = wanted & desc_tokens
        if not name_hits and not description_hits:
            continue
        score = (3 * len(name_hits)) + len(description_hits)
        matches.append({
            'id': str(item['id']),
            'name': item.get('name', ''),
            'reference': item.get('reference', ''),
            'matching_words': sorted(name_hits | description_hits)[:8],
            'match_score': score,
            'review_required': True,
        })
    return sorted(matches, key=lambda r: (-r['match_score'], r['name'].lower(), r['id']))[:max_results]
