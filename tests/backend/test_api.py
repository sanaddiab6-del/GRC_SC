# Backend Tests
import pytest

@pytest.mark.asyncio
async def test_health_check(test_client):
    """Test API health check endpoint"""
    response = await test_client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "ECC" in data["frameworks"]
    assert data["features"]["bilingual"] is True


@pytest.mark.asyncio
async def test_root_endpoint(test_client):
    """Test root endpoint redirects to the web login route"""
    response = await test_client.get("/", follow_redirects=False)
    assert response.status_code == 302
    assert response.headers.get("location", "").endswith("/auth/login")
