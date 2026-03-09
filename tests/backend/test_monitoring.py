"""
Monitoring router tests — all 5 endpoints are public (no auth required).
These hit the FastAPI app with a mocked DB session.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock
from httpx import AsyncClient, ASGITransport


@pytest.fixture(autouse=True)
def _override_db():
    from main import app
    from core.database import get_db

    session = AsyncMock()
    # text("SELECT 1") for health check
    session.execute = AsyncMock(return_value=MagicMock())

    async def override():
        yield session

    app.dependency_overrides[get_db] = override
    yield session
    app.dependency_overrides.pop(get_db, None)


@pytest.mark.asyncio
async def test_monitoring_health():
    from main import app

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        r = await c.get("/api/v1/monitoring/health")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] in ("healthy", "degraded")
    assert "database_status" in data


@pytest.mark.asyncio
async def test_monitoring_compliance(_override_db):
    from main import app

    session = _override_db
    # Two scalar calls: total and compliant count
    count_mock = MagicMock()
    count_mock.scalar.return_value = 10
    compliant_mock = MagicMock()
    compliant_mock.scalar.return_value = 7
    session.execute = AsyncMock(side_effect=[count_mock, compliant_mock])

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        r = await c.get("/api/v1/monitoring/compliance")
    assert r.status_code == 200
    data = r.json()
    assert data["total_controls"] == 10
    assert data["compliant_controls"] == 7
    assert data["overall_compliance_percent"] == 70.0


@pytest.mark.asyncio
async def test_monitoring_compliance_zero_controls(_override_db):
    from main import app

    session = _override_db
    zero_mock = MagicMock()
    zero_mock.scalar.return_value = 0
    session.execute = AsyncMock(return_value=zero_mock)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        r = await c.get("/api/v1/monitoring/compliance")
    assert r.status_code == 200
    assert r.json()["overall_compliance_percent"] == 0.0


@pytest.mark.asyncio
async def test_monitoring_dashboard():
    from main import app

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        r = await c.get("/api/v1/monitoring/dashboard")
    assert r.status_code == 200
    data = r.json()
    assert "system_health" in data
    assert "compliance" in data


@pytest.mark.asyncio
async def test_monitoring_dashboard_overview():
    from main import app

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        r = await c.get("/api/v1/monitoring/dashboard/overview")
    assert r.status_code == 200
    data = r.json()
    assert "compliance_rate" in data
    assert "total_controls" in data


@pytest.mark.asyncio
async def test_monitoring_security_events():
    from main import app

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        r = await c.get("/api/v1/monitoring/security-events?hours=48")
    assert r.status_code == 200
    data = r.json()
    assert data["period_hours"] == 48
    assert data["total_incidents"] == 0


@pytest.mark.asyncio
async def test_monitoring_security_events_default_hours():
    from main import app

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        r = await c.get("/api/v1/monitoring/security-events")
    assert r.status_code == 200
    assert r.json()["period_hours"] == 24
