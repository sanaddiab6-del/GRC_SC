"""
API Router for Control Management
"""

from fastapi import APIRouter, HTTPException
from typing import List, Optional
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1/controls", tags=["controls"])


class ControlBase(BaseModel):
    """Base control model"""
    control_id: str
    title: str
    description: str
    framework: str  # ecc, ccc, pdpl
    domain: str
    priority: str  # Critical, High, Medium, Low
    implementation_status: Optional[str] = "not_started"


class Control(ControlBase):
    """Full control model"""
    id: int
    
    model_config = {"from_attributes": True}


@router.get("/", response_model=List[Control])
async def list_controls(
    framework: Optional[str] = None,
    domain: Optional[str] = None,
    priority: Optional[str] = None
):
    """
    List all controls with optional filters
    """
    # Mock data for now
    controls = [
        {
            "id": 1,
            "control_id": "ECC-1.1.1",
            "title": "Information Security Policy",
            "description": "Establish and maintain an information security policy",
            "framework": "ecc",
            "domain": "Cybersecurity Governance",
            "priority": "Critical",
            "implementation_status": "implemented"
        },
        {
            "id": 2,
            "control_id": "CCC-2.1.1",
            "title": "Cloud Service Provider Assessment",
            "description": "Assess cloud service providers before adoption",
            "framework": "ccc",
            "domain": "Cloud Strategy",
            "priority": "High",
            "implementation_status": "in_progress"
        },
        {
            "id": 3,
            "control_id": "PDPL-3.1",
            "title": "Data Processing Lawfulness",
            "description": "Ensure lawful basis for personal data processing",
            "framework": "pdpl",
            "domain": "Data Protection",
            "priority": "Critical",
            "implementation_status": "not_started"
        }
    ]
    
    # Apply filters
    if framework:
        controls = [c for c in controls if c["framework"] == framework]
    if domain:
        controls = [c for c in controls if c["domain"] == domain]
    if priority:
        controls = [c for c in controls if c["priority"] == priority]
    
    return controls


@router.get("/{control_id}", response_model=Control)
async def get_control(control_id: str):
    """
    Get a specific control by ID
    """
    # Mock data
    controls = {
        "ECC-1.1.1": {
            "id": 1,
            "control_id": "ECC-1.1.1",
            "title": "Information Security Policy",
            "description": "Establish and maintain an information security policy",
            "framework": "ecc",
            "domain": "Cybersecurity Governance",
            "priority": "Critical",
            "implementation_status": "implemented"
        }
    }
    
    if control_id not in controls:
        raise HTTPException(status_code=404, detail="Control not found")
    
    return controls[control_id]
Controls API Module
Provides REST endpoints for control management
Wraps the controls router for API v1
"""

from fastapi import APIRouter
from src.backend.controls.router import router as controls_router

router = APIRouter()

# Include all control endpoints
router.include_router(controls_router, tags=["controls"])

__all__ = ["router"]
