import pytest
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent / "src" / "backend"
sys.path.insert(0, str(backend_path))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_root_endpoint():
    """Test the root endpoint returns expected response"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "operational"
    assert data["service"] == "SICO GRC Platform API"
    assert "ECC 3.0" in data["frameworks"]
    assert "CCC 1.0" in data["frameworks"]
    assert "PDPL 2023" in data["frameworks"]


def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_api_info():
    """Test API info endpoint"""
    response = client.get("/api/v1/info")
    assert response.status_code == 200
    data = response.json()
    assert data["api_version"] == "v1"
    assert "ecc" in data["supported_frameworks"]
    assert "ccc" in data["supported_frameworks"]
    assert "pdpl" in data["supported_frameworks"]
    
    # Test bilingual support
    ecc = data["supported_frameworks"]["ecc"]
    assert "name" in ecc
    assert "name_ar" in ecc
    assert ecc["name"] == "Essential Cybersecurity Controls"
    assert "الضوابط الأساسية للأمن السيبراني" in ecc["name_ar"]


def test_api_capabilities():
    """Test that API advertises key capabilities"""
    response = client.get("/api/v1/info")
    assert response.status_code == 200
    data = response.json()
    
    capabilities = data["capabilities"]
    assert "Unified Control Library" in capabilities
    assert "ECC-CCC Baseline Mapping" in capabilities
    assert "PDPL Registers (RoPA, DSAR, Breach)" in capabilities
    assert "Evidence Automation" in capabilities
    assert "SOC-GRC Integration" in capabilities
    assert "Bilingual AI (Arabic/English)" in capabilities
    assert "Executive Reporting" in capabilities


def test_framework_counts():
    """Test that framework control counts are correct"""
    response = client.get("/api/v1/info")
    assert response.status_code == 200
    data = response.json()
    
    frameworks = data["supported_frameworks"]
    assert frameworks["ecc"]["controls_count"] == 114
    assert frameworks["ccc"]["controls_count"] == 154
    assert frameworks["pdpl"]["articles_count"] == 40
