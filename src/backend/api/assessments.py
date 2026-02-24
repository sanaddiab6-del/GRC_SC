"""
API Router for Compliance Assessments
"""

from fastapi import APIRouter
from typing import List
from pydantic import BaseModel
from datetime import datetime

router = APIRouter(prefix="/api/v1/assessments", tags=["assessments"])


class AssessmentSummary(BaseModel):
    """Assessment summary model"""
    id: int
    name: str
    framework: str
    status: str
    compliance_score: float
    created_at: datetime
    updated_at: datetime


@router.get("/", response_model=List[AssessmentSummary])
async def list_assessments():
    """
    List all compliance assessments
    """
    return [
        {
            "id": 1,
            "name": "Q1 2026 ECC Assessment",
            "framework": "ecc",
            "status": "in_progress",
            "compliance_score": 75.5,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        },
        {
            "id": 2,
            "name": "Cloud Migration CCC Review",
            "framework": "ccc",
            "status": "completed",
            "compliance_score": 82.0,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
    ]


@router.get("/dashboard")
async def get_dashboard():
    """
    Get compliance dashboard summary
    """
    return {
        "overall_compliance": 78.5,
        "frameworks": {
            "ecc": {
                "total_controls": 114,
                "implemented": 86,
                "in_progress": 20,
                "not_started": 8,
                "compliance_score": 75.4
            },
            "ccc": {
                "total_controls": 180,
                "implemented": 147,
                "in_progress": 25,
                "not_started": 8,
                "compliance_score": 81.7
            },
            "pdpl": {
                "total_controls": 42,
                "implemented": 32,
                "in_progress": 6,
                "not_started": 4,
                "compliance_score": 76.2
            }
        },
        "recent_activities": [
            {
                "timestamp": datetime.now().isoformat(),
                "action": "Control ECC-1.1.1 marked as implemented",
                "user": "admin"
            }
        ]
    }
__all__ = ["router"]
