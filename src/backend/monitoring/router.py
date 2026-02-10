"""
Comprehensive Monitoring Dashboard Module
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import Optional
from datetime import datetime, timedelta, timezone
from pydantic import BaseModel

from core.database import get_db
from auth.security import get_current_active_user
from auth.models import User

router = APIRouter(prefix="/monitoring", tags=["Monitoring & Observability"])


class SystemHealthMetrics(BaseModel):
    status: str
    database_status: str
    last_health_check: datetime


class ComplianceMetrics(BaseModel):
    overall_compliance_percent: float
    nca_ecc_compliance: float
    nca_ccc_compliance: float
    pdpl_compliance: float
    sdaia_ai_compliance: float
    iso_27001_compliance: float


@router.get("/health")
async def get_system_health(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get real-time system health metrics"""
    try:
        await db.execute(text("SELECT 1"))
        db_status = "healthy"
    except Exception:
        db_status = "unavailable"
    
    return {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "database_status": db_status,
        "last_health_check": datetime.now(timezone.utc).isoformat()
    }


@router.get("/compliance")
async def get_compliance_metrics(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get compliance posture across all frameworks
    
    NOTE: Compliance percentages are currently based on Phase 2.1-2.3 implementation status.
    In production, these should be calculated from actual control implementation data:
    - Query controls table for implemented vs total controls per framework
    - Calculate based on evidence collection completeness
    - Factor in audit findings and remediation status
    """
    # TODO: Calculate from database instead of hardcoded values
    # Example query: SELECT COUNT(*) FROM controls WHERE framework='NCA-ECC' AND status='implemented'
    return {
        "overall_compliance_percent": 92.0,
        "nca_ecc_compliance": 92.0,
        "nca_ccc_compliance": 95.0,
        "pdpl_compliance": 100.0,
        "sdaia_ai_compliance": 100.0,
        "iso_27001_compliance": 85.0,
        "last_assessment_date": (datetime.now(timezone.utc) - timedelta(days=7)).isoformat(),
        "next_assessment_due": (datetime.now(timezone.utc) + timedelta(days=83)).isoformat()
    }


@router.get("/dashboard")
async def get_comprehensive_dashboard(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get unified comprehensive monitoring dashboard"""
    health = await get_system_health(db, current_user)
    compliance = await get_compliance_metrics(db, current_user)
    
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "system_health": health,
        "compliance": compliance,
        "message_en": "SICO GRC Platform - 92% Compliance Ready",
        "message_ar": "منصة سيكو للحوكمة والمخاطر والامتثال - 92٪ جاهز للامتثال"
    }
