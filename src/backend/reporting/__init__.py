"""Reporting module - placeholder for reporting engine"""
from fastapi import APIRouter

router = APIRouter()

@router.get("/reports")
async def list_reports():
    return {"message": "Reporting engine - coming soon"}
