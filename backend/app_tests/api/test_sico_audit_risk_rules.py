"""Pure tests for the new read-only audit and matrix rules (no database needed)."""

from datetime import date

import pytest

from ai_onboarding.audit_risk_rules import (
    PreviewInputError,
    preview_risk_ratings,
    review_evidence_metadata,
)


def matrix():
    return {
        "probability": [{"name": "Low"}, {"name": "High"}],
        "impact": [{"name": "Low"}, {"name": "High"}],
        "grid": [[0, 1], [1, 2]],
        "risk": [{"name": "Low"}, {"name": "Medium"}, {"name": "High"}],
    }


def test_missing_evidence_does_not_create_a_noncompliance_decision():
    result = review_evidence_metadata([], today=date(2026, 10, 19))
    assert result["proposed_compliance_result"] is None
    assert "no_evidence_linked" in result["review_flags"]


def test_expired_evidence_requires_review():
    evidence = [{"status": "approved", "expiry_date": "2026-01-01", "has_attachment": True, "has_link": False}]
    result = review_evidence_metadata(evidence, today=date(2026, 10, 19))
    assert "evidence_expired" in result["review_flags"]
    assert result["proposed_compliance_result"] is None


def test_matrix_is_used_instead_of_likelihood_times_impact():
    result = preview_risk_ratings(matrix(), {
        "inherent": {"probability": 1, "impact": 1},
        "current": {"probability": 0, "impact": 1},
        "residual": {"probability": 0, "impact": 0},
    })
    assert result["ratings"]["inherent"]["risk_level_index"] == 2
    assert result["ratings"]["current"]["risk_level_index"] == 1
    assert result["ratings"]["residual"]["risk_level_index"] == 0
    assert result["writes_performed"] is False


@pytest.mark.parametrize("bad", [-1, 2, True, 1.2, "1"])
def test_invalid_index_rejected(bad):
    with pytest.raises(PreviewInputError):
        preview_risk_ratings(matrix(), {"current": {"probability": bad, "impact": 1}})


def test_malformed_matrix_cannot_silently_produce_score():
    broken = matrix()
    broken["grid"] = [[0], [1]]
    with pytest.raises(PreviewInputError):
        preview_risk_ratings(broken, {"current": {"probability": 1, "impact": 1}})


def test_unexpected_risk_fields_rejected():
    with pytest.raises(PreviewInputError):
        preview_risk_ratings(matrix(), {"accepted": {"probability": 0, "impact": 0}})
