"""
Main app (health / frameworks / security-status) endpoint tests.
These are all public endpoints with no auth required.
"""
import pytest
from httpx import AsyncClient, ASGITransport


@pytest.mark.asyncio
async def test_root_redirects():
    from main import app

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test", follow_redirects=False) as c:
        r = await c.get("/")
    assert r.status_code == 302


@pytest.mark.asyncio
async def test_health_simple():
    from main import app

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        r = await c.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "healthy"


@pytest.mark.asyncio
async def test_health_detailed():
    from main import app

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        r = await c.get("/api/v1/health")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "healthy"
    assert data["features"]["bilingual"] is True
    assert "ECC" in data["frameworks"]


@pytest.mark.asyncio
async def test_list_frameworks():
    from main import app

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        r = await c.get("/api/v1/frameworks")
    assert r.status_code == 200
    data = r.json()
    ids = [f["id"] for f in data["frameworks"]]
    assert "ecc" in ids
    assert "ccc" in ids
    assert "pdpl" in ids


@pytest.mark.asyncio
async def test_security_status():
    from main import app

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        r = await c.get("/api/v1/security-status")
    assert r.status_code == 200
    data = r.json()
    assert data["authentication"]["jwt_enabled"] is True
    assert data["authorization"]["rbac_enabled"] is True
    assert "AES-256" in data["encryption"]["algorithm"]
