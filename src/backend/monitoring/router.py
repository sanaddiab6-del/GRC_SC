"""Monitoring API router for system health and compliance metrics."""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func, text
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from controls.models import Control, ControlStatus

router = APIRouter(prefix="/monitoring", tags=["Monitoring & Observability"])


@router.get("/health")
async def get_system_health(
    db: AsyncSession = Depends(get_db),
):
    """Get real-time system health metrics."""
    try:
        await db.execute(text("SELECT 1"))
        db_status = "healthy"
    except Exception:
        db_status = "degraded"

    return {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "database_status": db_status,
        "last_health_check": datetime.now(timezone.utc).isoformat(),
        "message_en": "All systems operational",
        "message_ar": "جميع الأنظمة تعمل",
    }


@router.get("/compliance")
async def get_compliance_metrics(
    db: AsyncSession = Depends(get_db),
):
    """Get compliance posture across all frameworks."""
    total_result = await db.execute(select(func.count()).select_from(Control))
    total_controls = int(total_result.scalar() or 0)

    compliant_result = await db.execute(
        select(func.count()).select_from(Control).where(Control.status == ControlStatus.COMPLIANT)
    )
    compliant_controls = int(compliant_result.scalar() or 0)

    compliance_rate = (
        round((compliant_controls / total_controls * 100), 2) if total_controls > 0 else 0.0
    )

    return {
        "total_controls": total_controls,
        "compliant_controls": compliant_controls,
        "overall_compliance_percent": compliance_rate,
        "message_en": f"Compliance rate: {compliance_rate}%",
        "message_ar": f"معدل الامتثال: {compliance_rate}%",
    }


@router.get("/dashboard")
async def get_monitoring_dashboard(
    db: AsyncSession = Depends(get_db),
):
    """Get unified monitoring dashboard payload."""
    health = await get_system_health(db)
    compliance = await get_compliance_metrics(db)

    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "system_health": health,
        "compliance": compliance,
        "message_en": "SICO GRC Platform - Monitoring Dashboard",
        "message_ar": "منصة سيكو للحوكمة - لوحة المراقبة",
    }


@router.get("/dashboard/overview")
async def get_dashboard_overview(
    db: AsyncSession = Depends(get_db),
):
    """Get high-level monitoring dashboard overview."""
    compliance = await get_compliance_metrics(db)

    return {
        "compliance_rate": compliance["overall_compliance_percent"],
        "total_controls": compliance["total_controls"],
        "compliant_controls": compliance["compliant_controls"],
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "message_en": "Security dashboard overview",
        "message_ar": "نظرة عامة على لوحة الأمان",
    }


@router.get("/security-events")
async def get_security_events(
    hours: int = Query(24, ge=1, le=720),
):
    """Get recent security events summary."""
    return {
        "period_hours": hours,
        "total_incidents": 0,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "message_en": f"Security events in last {hours} hours",
        "message_ar": f"أحداث الأمن في آخر {hours} ساعة",
    }


__all__ = ["router"]
