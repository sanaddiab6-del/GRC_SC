import pytest
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent / "src" / "backend"
sys.path.insert(0, str(backend_path))

from fastapi.testclient import TestClient
from app.main import app
"""
Basic test for the SICO GRC Platform API
"""

import pytest
from fastapi.testclient import TestClient
import sys
import os

# Add the backend directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'backend'))

from main import app

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
    """Test the root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "SICO GRC Platform API"
    assert data["version"] == "0.1.0"
    assert data["status"] == "operational"
    assert "frameworks" in data


def test_health_check():
    """Test the health check endpoint"""
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
def test_list_frameworks():
    """Test listing frameworks"""
    response = client.get("/api/v1/frameworks")
    assert response.status_code == 200
    data = response.json()
    assert "frameworks" in data
    frameworks = data["frameworks"]
    assert len(frameworks) == 3
    
    framework_ids = [f["id"] for f in frameworks]
    assert "ecc" in framework_ids
    assert "ccc" in framework_ids
    assert "pdpl" in framework_ids


def test_list_controls():
    """Test listing controls"""
    response = client.get("/api/v1/controls/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    
    # Test filtering by framework
    response = client.get("/api/v1/controls/?framework=ecc")
    assert response.status_code == 200
    data = response.json()
    for control in data:
        assert control["framework"] == "ecc"


def test_get_control():
    """Test getting a specific control"""
    response = client.get("/api/v1/controls/ECC-1.1.1")
    assert response.status_code == 200
    data = response.json()
    assert data["control_id"] == "ECC-1.1.1"
    assert data["framework"] == "ecc"


def test_get_nonexistent_control():
    """Test getting a control that doesn't exist"""
    response = client.get("/api/v1/controls/INVALID-1.1.1")
    assert response.status_code == 404


def test_list_assessments():
    """Test listing assessments"""
    response = client.get("/api/v1/assessments/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_dashboard():
    """Test the dashboard endpoint"""
    response = client.get("/api/v1/assessments/dashboard")
    assert response.status_code == 200
    data = response.json()
    assert "overall_compliance" in data
    assert "frameworks" in data
    assert "ecc" in data["frameworks"]
    assert "ccc" in data["frameworks"]
    assert "pdpl" in data["frameworks"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
