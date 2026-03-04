# Backend Tests
import pytest
from httpx import AsyncClient, ASGITransport
from main import app


@pytest.mark.asyncio
async def test_health_check():
    """Test API health check endpoint"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "ECC" in data["frameworks"]
        assert data["features"]["bilingual"] is True


@pytest.mark.asyncio
async def test_root_endpoint():
    """Test root endpoint returns bilingual message"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/", follow_redirects=True)
        assert response.status_code == 200
        data = response.json()
        assert "message_en" in data
        assert "message_ar" in data
