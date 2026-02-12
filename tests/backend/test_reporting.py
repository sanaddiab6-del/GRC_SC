# Backend Tests - Reporting Module
import pytest
from httpx import AsyncClient, ASGITransport
from main import app


@pytest.mark.asyncio
async def test_get_dashboard():
    """Test executive dashboard endpoint"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/dashboard")
        assert response.status_code == 200
        data = response.json()
        
        # Check required fields
        assert "compliance_summary" in data
        assert "control_posture" in data
        assert "frameworks" in data
        
        # Check compliance summary structure
        summary = data["compliance_summary"]
        assert "total_controls" in summary
        assert "compliance_rate" in summary
        assert "by_framework" in summary


@pytest.mark.asyncio
async def test_generate_report():
    """Test report generation"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        report_request = {
            "report_type": "compliance_summary",
            "framework_filter": ["ECC", "CCC"],
            "file_format": "json",
            "generated_by": "test_user"
        }
        
        response = await client.post("/api/v1/reports", json=report_request)
        assert response.status_code == 201
        data = response.json()
        
        assert "report_id" in data
        assert data["report_type"] == "compliance_summary"
        assert data["status"] in ["pending", "completed"]


@pytest.mark.asyncio
async def test_list_reports():
    """Test listing generated reports"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/reports")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
