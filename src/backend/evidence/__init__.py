"""Evidence module - placeholder for evidence management"""
from fastapi import APIRouter

router = APIRouter()

@router.get("/evidence")
async def list_evidence():
    return {"message": "Evidence management - coming soon"}
