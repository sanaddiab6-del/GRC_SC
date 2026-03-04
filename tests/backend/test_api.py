# Backend Tests
from pathlib import Path
import sys

import pytest
from httpx import AsyncClient, ASGITransport

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from backend.main import app

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
