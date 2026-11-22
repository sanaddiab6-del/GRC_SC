"""Deterministic, read-only audit and risk preview rules.

These rules do not declare compliance or accept risks. They identify evidence-review
work and calculate matrix values supplied by an authorized assessor. Keeping the
math here makes it independently testable, with no model or network dependency.
"""

from __future__ import annotations

from datetime import date
from typing import Any


class PreviewInputError(ValueError):
    """A proposed score or a matrix definition is invalid."""


def review_evidence_metadata(evidences: list[dict[str, Any]], *, today: date | None = None) -> dict[str, Any]:
    """Identify audit-review tasks. Evidence presence is NEVER proof of compliance."""
    today = today or date.today()
    flags = []
    if not evidences:
        flags.append("no_evidence_linked")
    for evidence in evidences:
        status = evidence.get("status")
        expires = evidence.get("expiry_date")
        if status == "missing":
            flags.append("evidence_marked_missing")
        if status in {"draft", "in_review", "rejected"}:
            flags.append("evidence_not_approved")
        if status == "expired" or (expires and date.fromisoformat(expires) < today):
            flags.append("evidence_expired")
        if not evidence.get("has_attachment") and not evidence.get("has_link"):
            flags.append("evidence_without_attachment_or_link")
    return {
        "review_flags": sorted(set(flags)),
        "proposed_compliance_result": None,
        "review_status": "requires_professional_assessment",
        "reason": (
            "Evidence metadata alone cannot establish implementation or compliance. "
            "A reviewer must inspect the actual contents and test them against the requirement."
        ),
    }


def _matrix_score(matrix_definition: dict[str, Any], probability: int, impact: int) -> dict[str, Any]:
    """Mirror core.models.risk_scoring: grid[probability][impact]."""
    grid = matrix_definition.get("grid")
    risks = matrix_definition.get("risk")
    probabilities = matrix_definition.get("probability")
    impacts = matrix_definition.get("impact")
    if not isinstance(grid, list) or not isinstance(risks, list):
        raise PreviewInputError("The selected risk matrix has an invalid grid/risk definition.")
    if not isinstance(probabilities, list) or not isinstance(impacts, list):
        raise PreviewInputError("The selected risk matrix has invalid probability/impact choices.")
    # bool is an int in Python, but must not be accepted as a risk rating.
    if type(probability) is not int or type(impact) is not int:
        raise PreviewInputError("Probability and impact must be integer matrix indices.")
    if probability < 0 or impact < 0 or probability >= len(probabilities) or impact >= len(impacts):
        raise PreviewInputError("Probability or impact is outside the selected matrix scale.")
    try:
        value = grid[probability][impact]
    except (IndexError, TypeError):
        raise PreviewInputError("The selected matrix grid has missing cells.") from None
    if type(value) is not int or value < 0 or value >= len(risks):
        raise PreviewInputError("The selected matrix grid references an invalid risk level.")
    metadata = risks[value]
    return {
        "probability_index": probability,
        "impact_index": impact,
        "risk_level_index": value,
        "risk_level_name": metadata.get("name", str(value)) if isinstance(metadata, dict) else str(value),
    }


def preview_risk_ratings(matrix_definition: dict[str, Any], ratings: dict[str, Any]) -> dict[str, Any]:
    """Calculate inherited/current/target-residual matrix values without saving anything."""
    if not isinstance(ratings, dict) or not ratings:
        raise PreviewInputError("Provide at least one risk rating stage.")
    unexpected = sorted(set(ratings) - {"inherent", "current", "residual"})
    if unexpected:
        raise PreviewInputError("Unrecognized rating stage(s): " + ", ".join(unexpected))
    result = {}
    for stage in ("inherent", "current", "residual"):
        if stage not in ratings:
            continue
        pair = ratings[stage]
        if not isinstance(pair, dict) or set(pair) != {"probability", "impact"}:
            raise PreviewInputError(f"{stage} must provide probability and impact indices.")
        result[stage] = _matrix_score(matrix_definition, pair["probability"], pair["impact"])
    warnings = []
    if "residual" in result:
        warnings.append("Residual ratings describe the target after proposed treatments; they are not achieved current risk.")
    if "current" in result and "residual" in result:
        if result["residual"]["risk_level_index"] > result["current"]["risk_level_index"]:
            warnings.append("Target residual risk is higher than current risk; verify the proposed treatment and rating.")
    return {
        "ratings": result,
        "warnings": warnings,
        "status": "draft_for_human_review",
        "writes_performed": False,
    }
