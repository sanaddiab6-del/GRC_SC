"""
Evidence Router
API endpoints for evidence management
"""

from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def list_evidence():
    """List all evidence"""
    return {"evidence": []}


@router.post("/")
async def create_evidence():
    """Create new evidence"""
    return {"status": "created"}
