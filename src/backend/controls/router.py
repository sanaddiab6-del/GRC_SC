"""
Controls Router
API endpoints for compliance controls management
"""

from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def list_controls():
    """List all controls"""
    return {"controls": []}


@router.get("/{control_id}")
async def get_control(control_id: str):
    """Get control by ID"""
    return {"control_id": control_id}
