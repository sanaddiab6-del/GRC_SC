"""
Risk management business logic and router endpoint tests.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock


# ─── Risk scoring (pure unit tests) ──────────────────────────────────────────

def test_calculate_risk_score_low():
    from risk.router import calculate_risk_score

    score, level = calculate_risk_score(1, 1)
    assert score == 1
    assert level == "low"


def test_calculate_risk_score_medium():
    from risk.router import calculate_risk_score

    score, level = calculate_risk_score(3, 3)
    assert score == 9
    assert level == "medium"


def test_calculate_risk_score_high():
    from risk.router import calculate_risk_score

    score, level = calculate_risk_score(4, 4)
    assert score == 16
    assert level == "high"


def test_calculate_risk_score_critical():
    from risk.router import calculate_risk_score

    score, level = calculate_risk_score(5, 5)
    assert score == 25
    assert level == "critical"


def test_calculate_risk_score_boundary_5():
    from risk.router import calculate_risk_score

    score, level = calculate_risk_score(5, 1)
    assert score == 5
    assert level == "low"


def test_calculate_risk_score_boundary_12():
    from risk.router import calculate_risk_score

    score, level = calculate_risk_score(4, 3)
    assert score == 12
    assert level == "medium"


def test_calculate_risk_score_boundary_20():
    from risk.router import calculate_risk_score

    score, level = calculate_risk_score(5, 4)
    assert score == 20
    assert level == "high"


def test_calculate_risk_score_boundary_21():
    from risk.router import calculate_risk_score

    score, level = calculate_risk_score(3, 7)
    assert score == 21
    assert level == "critical"


# ─── Risk number generation ──────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_generate_risk_number_first():
    from risk.router import generate_risk_number

    session = AsyncMock()
    result = MagicMock()
    result.scalar_one_or_none.return_value = None
    session.execute = AsyncMock(return_value=result)

    num = await generate_risk_number(session)
    assert num.startswith("RISK-")
    assert num.endswith("-001")


@pytest.mark.asyncio
async def test_generate_risk_number_increment():
    from risk.router import generate_risk_number

    session = AsyncMock()
    result = MagicMock()
    result.scalar_one_or_none.return_value = "RISK-2025-005"
    session.execute = AsyncMock(return_value=result)

    num = await generate_risk_number(session)
    assert num.endswith("-006")


# ─── Incident number generation ──────────────────────────────────────────────

def test_generate_incident_number():
    from incident.router import generate_incident_number

    num = generate_incident_number()
    assert num.startswith("INC-")
    # Contains a year
    import re
    assert re.match(r"INC-\d{4}-\d+", num)
