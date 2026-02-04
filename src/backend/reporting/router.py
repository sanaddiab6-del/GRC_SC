"""
Reporting Router
API endpoints for compliance reporting
"""

from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def list_reports():
    """List all reports"""
    return {"reports": []}


@router.post("/generate")
async def generate_report():
    """Generate new report"""
    return {"status": "generating"}
