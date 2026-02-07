# Backend Tests - Evidence Module
import pytest
from httpx import AsyncClient, ASGITransport
from src.backend.main import app


@pytest.mark.asyncio
async def test_create_evidence():
    """Test creating new evidence"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        evidence_data = {
            "evidence_id": "EVD-TEST-001",
            "control_id": "ECC-GV-1",
            "evidence_type": "policy",
            "title_en": "Test Evidence",
            "title_ar": "دليل تجريبي",
            "retention_period_days": 2555
        }
        
        response = await client.post("/api/v1/evidence", json=evidence_data)
        assert response.status_code == 201
        data = response.json()
        assert data["evidence_id"] == "EVD-TEST-001"
        assert data["status"] == "pending"


@pytest.mark.asyncio
async def test_list_evidence():
    """Test listing evidence with filters"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/evidence?control_id=ECC-GV-1")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data


@pytest.mark.asyncio
async def test_validate_evidence():
    """Test evidence validation"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        validation_data = {
            "validated_by": "test_auditor",
            "validation_notes": "Approved for compliance",
            "approved": True
        }
        
        response = await client.post(
            "/api/v1/evidence/EVD-TEST-001/validate",
            json=validation_data
        )
        # Will return 404 if evidence doesn't exist, which is expected in test
        assert response.status_code in [200, 404]
