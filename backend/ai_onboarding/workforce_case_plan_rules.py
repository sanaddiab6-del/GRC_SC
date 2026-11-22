"""Pure safe planning rules for SICO new-case preflight. No I/O and no AI guessing."""
from __future__ import annotations
import re


class CasePlanInputError(ValueError):
    pass


def normalize_name(value, *, limit=160):
    if not isinstance(value, str):
        raise CasePlanInputError("An expected name or scope is not text.")
    return re.sub(r"\s+", " ", value).strip()[:limit]


def exact_organization_match(value, organization):
    return bool(normalize_name(value) and normalize_name(organization)
                and normalize_name(value).casefold() == normalize_name(organization).casefold())


def proposed_case_names(organization, scope, framework):
    org = normalize_name(organization, limit=90)
    area = normalize_name(scope, limit=110)
    standard = normalize_name(framework, limit=110)
    if len(org) < 3 or len(area) < 5 or len(standard) < 3:
        raise CasePlanInputError("Organization, framework and assessment scope must be specified.")
    return {
        "domain": org,
        "perimeter": normalize_name(f"{org} - {area}"),
        "assessment": normalize_name(f"{org} - {standard} - {area}"),
        "assessment_version": "1.0",
    }


def readiness_label(blockers):
    return "blocked" if blockers else "review_required"


def safe_error_codes(messages):
    # Codes for UI and acceptance tests. Never expose unreadable object IDs.
    return sorted({m.get("code", "unspecified") for m in messages})
