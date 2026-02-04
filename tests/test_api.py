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
