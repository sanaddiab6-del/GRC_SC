"""Conservative, read-only suggestions for the SICO AI risk review.

Consumes ONLY the permission-filtered, same-folder catalog supplied by the
full-context view. These are proposed matches, NEVER evidence or permissions.
No ORM calls, provider calls, or database writes are performed here.
"""
from __future__ import annotations

import re
from typing import Any

_MAX_CONTEXT = 12000


def _clean(value: Any, maximum: int = 2000) -> str:
    if not isinstance(value, str):
        return ""
    return " ".join(value.strip().split())[:maximum]


def _mention(name: str, text: str) -> bool:
    """Only a whole, literal record name in the supplied text counts.

    Substrings ('bank' in 'bankruptcy'), generic short labels and partial
    keyword overlaps are intentionally excluded.
    """
    name = _clean(name, 180)
    if len(name) < 7 or not any(c.isalpha() for c in name):
        return False
    if not text:
        return False
    escaped = r"\s+".join(re.escape(piece) for piece in name.split())
    return bool(re.search(r"(?<!\w)" + escaped + r"(?!\w)", text, flags=re.I))


def _literal_matches(options: list[dict], text: str) -> list[dict]:
    matches = []
    seen = set()
    for item in options[:60]:
        if not isinstance(item, dict):
            continue
        label = _clean(item.get("label"), 180)
        reference = item.get("reference")
        if not isinstance(reference, str) or reference in seen:
            continue
        if _mention(label, text):
            matches.append({"reference": reference, "label": label})
            seen.add(reference)
    return matches


def inspect_risk_context(catalogs: dict, scenario: dict) -> dict:
    """Explain supported suggestions and information gaps.

    Any auto-selected asset MUST be a unique *literal full-name mention* from
    the already readable, folder-filtered Asset catalog. No other GRC
    relationship, treatment, or risk rating is inferred from text.
    """
    if not isinstance(catalogs, dict) or not isinstance(scenario, dict):
        return {"suggestions": {}, "review_drafts": {}, "candidate_mentions": {}, "gaps": []}

    narrative = " ".join(_clean(scenario.get(k), 4000) for k in
        ("scenario_title", "scenario_description", "scenario_threat",
         "scenario_vulnerability", "scenario_rationale"))[:_MAX_CONTEXT]
    asset_title = _clean(scenario.get("asset_title"), 200)
    control_title = _clean(scenario.get("linked_applied_control_title"), 200)
    assets = catalogs.get("assets") or []
    controls = catalogs.get("existing_controls") or []
    # If the name is explicitly provided, only that exact full label is eligible.
    exact_asset = [x for x in assets if _clean(x.get("label")).casefold() == asset_title.casefold()] if asset_title else []
    literal_assets = _literal_matches(assets, narrative)
    auto_assets = exact_asset if len(exact_asset) == 1 else (
        literal_assets if len(literal_assets) == 1 else [])
    # An ACTIVE control in the catalog is NOT proof it mitigates this scenario.
    # Present mention candidates for reviewer investigation, never prelink.
    literal_controls = _literal_matches(controls, narrative)
    if control_title:
        literal_controls = [x for x in controls if _clean(x.get("label")).casefold() == control_title.casefold()]

    rationale = _clean(scenario.get("scenario_rationale"), 1700)
    review_drafts = {}
    if rationale:
        review_drafts["justification"] = (
            "AI advisory rationale (UNVERIFIED; NOT rating evidence): " + rationale
        )[:2000]

    gaps = []
    if not auto_assets:
        gaps.append("Assets: no unique exact asset name was established in this assessment's readable folder records. Review inventory; do not invent an asset.")
    if literal_controls:
        gaps.append("Controls: matching control names are candidates only. Confirm they actually protect this system and are implemented before linking.")
    else:
        gaps.append("Controls: no existing control can be verified for this scenario from its description. Check implementation evidence.")
    gaps.extend([
        "Owner: SICO AI cannot choose a responsible person without an approved company assignment.",
        "Official risk ratings: inherent, current and residual probability/impact require evidence and human review of the assessment's actual matrix.",
        "Residual risk and treatment: do not assume planned measures are implemented or a treatment has been approved.",
    ])
    return {
        "suggestions": {"asset_references": [x["reference"] for x in auto_assets]},
        "review_drafts": review_drafts,
        "candidate_mentions": {
            "assets": literal_assets[:10],
            "existing_controls": literal_controls[:10],
        },
        "gaps": gaps,
        "method": "Read-only full-name matching against authorized same-folder records; no evidence verification.",
    }
