"""
Comprehensive Monitoring Dashboard Module
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import Optional
from datetime import datetime, timedelta
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
        "last_health_check": datetime.utcnow().isoformat()
        "last_health_check": datetime.now(timezone.utc).isoformat()
    }


@router.get("/compliance")
async def get_compliance_metrics(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get compliance posture across all frameworks"""
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
        "last_assessment_date": (datetime.utcnow() - timedelta(days=7)).isoformat(),
        "next_assessment_due": (datetime.utcnow() + timedelta(days=83)).isoformat()
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
        "timestamp": datetime.utcnow().isoformat(),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "system_health": health,
        "compliance": compliance,
        "message_en": "SICO GRC Platform - 92% Compliance Ready",
        "message_ar": "منصة سيكو للحوكمة والمخاطر والامتثال - 92٪ جاهز للامتثال"
Security Monitoring API Router
Real-time compliance posture and security metrics dashboard
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from typing import Dict, List, Any
from datetime import datetime, timedelta

from core.database import get_db
from auth.dependencies import require_permission
from controls.models import Control
from evidence.models import Evidence
from incident.models import Incident
from risk.models import Risk, RiskLevel
from backup.models import BackupJob, BackupStatus
from audit.models import AuditLog
from privacy.models import ConsentRecord, DataSubjectAccessRequest

router = APIRouter(prefix="/api/v1/monitoring", tags=["Security Monitoring"])


@router.get("/dashboard/overview")
async def get_dashboard_overview(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_permission("audit:read"))
):
    """
    Get high-level security monitoring dashboard overview
    Requires: audit:read permission
    """
    now = datetime.now()
    last_30_days = now - timedelta(days=30)
    last_24_hours = now - timedelta(hours=24)
    
    # Controls compliance metrics
    total_controls_query = select(func.count(Control.id))
    total_controls_result = await db.execute(total_controls_query)
    total_controls = total_controls_result.scalar() or 0
    
    # Active incidents (last 30 days)
    active_incidents_query = select(func.count(Incident.id)).where(
        and_(
            Incident.status.in_(["open", "in_progress"]),
            Incident.detected_at >= last_30_days
        )
    )
    active_incidents_result = await db.execute(active_incidents_query)
    active_incidents = active_incidents_result.scalar() or 0
    
    # Critical risks
    critical_risks_query = select(func.count(Risk.id)).where(
        Risk.risk_level == RiskLevel.CRITICAL
    )
    critical_risks_result = await db.execute(critical_risks_query)
    critical_risks = critical_risks_result.scalar() or 0
    
    # Recent backups (last 7 days)
    last_7_days = now - timedelta(days=7)
    recent_backups_query = select(func.count(BackupJob.id)).where(
        and_(
            BackupJob.created_at >= last_7_days,
            BackupJob.status == BackupStatus.COMPLETED
        )
    )
    recent_backups_result = await db.execute(recent_backups_query)
    recent_backups = recent_backups_result.scalar() or 0
    
    # Audit events (last 24 hours)
    audit_events_query = select(func.count(AuditLog.id)).where(
        AuditLog.timestamp >= last_24_hours
    )
    audit_events_result = await db.execute(audit_events_query)
    audit_events_24h = audit_events_result.scalar() or 0
    
    # Privacy metrics
    pending_dsar_query = select(func.count(DataSubjectAccessRequest.id)).where(
        DataSubjectAccessRequest.status.in_(["pending", "in_progress"])
    )
    pending_dsar_result = await db.execute(pending_dsar_query)
    pending_dsar = pending_dsar_result.scalar() or 0
    
    return {
        "timestamp": now.isoformat(),
        "compliance": {
            "total_controls": total_controls,
            # Note: These scores are based on Phase 2.4 completion status
            # TODO: Calculate dynamically from control implementation status in future iteration
            "compliance_score": 92,  # From compliance status report
            "nca_ecc_score": 92,
            "pdpl_score": 100,
            "ccc_score": 95,
            "sdaia_ai_score": 100
        },
        "security": {
            "active_incidents": active_incidents,
            "critical_risks": critical_risks,
            "recent_backups": recent_backups,
            "audit_events_24h": audit_events_24h
        },
        "privacy": {
            "pending_dsar": pending_dsar,
            "active_consents": 0  # Placeholder
        },
        "status": "healthy" if active_incidents == 0 and critical_risks == 0 else "attention_required",
        "message_en": "Security posture healthy" if active_incidents == 0 else "Security attention required",
        "message_ar": "الوضع الأمني جيد" if active_incidents == 0 else "يتطلب الوضع الأمني اهتمامًا"
    }


@router.get("/compliance/scorecard")
async def get_compliance_scorecard(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_permission("audit:read"))
):
    """
    Get detailed compliance scorecard by framework
    Requires: audit:read permission
    
    Note: Compliance scores are based on Phase 2.4 implementation status.
    Future enhancement: Calculate dynamically from control status in database.
    """
    return {
        "timestamp": datetime.now().isoformat(),
        "overall_compliance": 92,
        "frameworks": [
            {
                "framework": "NCA ECC",
                "framework_ar": "ضوابط الأمن السيبراني الأساسية",
                "score": 92,
                "total_controls": 23,
                "implemented": 21,
                "in_progress": 2,
                "status": "compliant",
                "gaps": [
                    {"control_id": "ECC-BC-1", "name": "Backup Requirements", "status": "completed"},
                    {"control_id": "ECC-BC-2", "name": "Business Continuity", "status": "completed"}
                ]
            },
            {
                "framework": "NCA CCC",
                "framework_ar": "إطار الحوسبة السحابية",
                "score": 95,
                "total_controls": 20,
                "implemented": 19,
                "in_progress": 1,
                "status": "compliant"
            },
            {
                "framework": "PDPL",
                "framework_ar": "نظام حماية البيانات الشخصية",
                "score": 100,
                "total_controls": 43,
                "implemented": 43,
                "in_progress": 0,
                "status": "fully_compliant"
            },
            {
                "framework": "SDAIA AI",
                "framework_ar": "مبادئ الذكاء الاصطناعي",
                "score": 100,
                "total_controls": 6,
                "implemented": 6,
                "in_progress": 0,
                "status": "fully_compliant"
            },
            {
                "framework": "ISO 27001",
                "framework_ar": "إدارة أمن المعلومات",
                "score": 85,
                "total_controls": 114,
                "implemented": 97,
                "in_progress": 17,
                "status": "in_progress"
            }
        ]
    }


@router.get("/incidents/trends")
async def get_incident_trends(
    days: int = 30,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_permission("audit:read"))
):
    """
    Get incident trends over time
    Requires: audit:read permission
    """
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    # Query incidents grouped by date
    incidents_query = select(
        func.date(Incident.detected_at).label('date'),
        func.count(Incident.id).label('count'),
        Incident.severity
    ).where(
        Incident.detected_at >= start_date
    ).group_by(
        func.date(Incident.detected_at),
        Incident.severity
    ).order_by(func.date(Incident.detected_at))
    
    result = await db.execute(incidents_query)
    incidents_data = result.all()
    
    # Transform data for charting
    trends = {}
    for row in incidents_data:
        date_str = row.date.isoformat() if row.date else "unknown"
        if date_str not in trends:
            trends[date_str] = {"date": date_str, "total": 0, "by_severity": {}}
        trends[date_str]["total"] += row.count
        trends[date_str]["by_severity"][row.severity] = row.count
    
    return {
        "period_days": days,
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "trends": list(trends.values())
    }


@router.get("/risks/heatmap")
async def get_risk_heatmap(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_permission("audit:read"))
):
    """
    Get risk heatmap (likelihood vs impact)
    Requires: audit:read permission
    """
    # Query risks grouped by likelihood and impact
    risks_query = select(
        Risk.likelihood,
        Risk.impact,
        func.count(Risk.id).label('count')
    ).group_by(
        Risk.likelihood,
        Risk.impact
    )
    
    result = await db.execute(risks_query)
    risks_data = result.all()
    
    # Build heatmap matrix (5x5)
    heatmap = []
    for likelihood in range(1, 6):
        row = []
        for impact in range(1, 6):
            count = next(
                (r.count for r in risks_data if r.likelihood == likelihood and r.impact == impact),
                0
            )
            row.append(count)
        heatmap.append(row)
    
    return {
        "heatmap": heatmap,
        "labels": {
            "likelihood": ["Very Low", "Low", "Medium", "High", "Very High"],
            "likelihood_ar": ["منخفض جدًا", "منخفض", "متوسط", "عالي", "عالي جدًا"],
            "impact": ["Negligible", "Minor", "Moderate", "Major", "Catastrophic"],
            "impact_ar": ["ضئيل", "بسيط", "متوسط", "كبير", "كارثي"]
        }
    }


@router.get("/backups/status")
async def get_backup_status(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_permission("backup:read"))
):
    """
    Get backup system status and recent backups
    Requires: backup:read permission
    """
    now = datetime.now()
    last_7_days = now - timedelta(days=7)
    
    # Recent backups
    recent_backups_query = select(BackupJob).where(
        BackupJob.created_at >= last_7_days
    ).order_by(BackupJob.created_at.desc()).limit(10)
    
    result = await db.execute(recent_backups_query)
    recent_backups = result.scalars().all()
    
    # Calculate success rate
    total_backups = len(recent_backups)
    successful_backups = sum(1 for b in recent_backups if b.status == BackupStatus.COMPLETED)
    success_rate = (successful_backups / total_backups * 100) if total_backups > 0 else 0
    
    return {
        "success_rate": round(success_rate, 2),
        "total_backups_7d": total_backups,
        "successful_backups": successful_backups,
        "failed_backups": total_backups - successful_backups,
        "last_backup": recent_backups[0].created_at.isoformat() if recent_backups else None,
        "recent_backups": [
            {
                "id": b.id,
                "job_name": b.job_name,
                "status": b.status.value,
                "backup_size_mb": b.backup_size_mb,
                "created_at": b.created_at.isoformat()
            }
            for b in recent_backups[:5]
        ]
    }


@router.get("/audit/summary")
async def get_audit_summary(
    hours: int = 24,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_permission("audit:read"))
):
    """
    Get audit log summary for specified time period
    Requires: audit:read permission
    """
    start_time = datetime.now() - timedelta(hours=hours)
    
    # Query audit logs
    audit_query = select(
        AuditLog.action,
        func.count(AuditLog.id).label('count')
    ).where(
        AuditLog.timestamp >= start_time
    ).group_by(AuditLog.action)
    
    result = await db.execute(audit_query)
    audit_data = result.all()
    
    total_events = sum(row.count for row in audit_data)
    
    return {
        "period_hours": hours,
        "total_events": total_events,
        "events_by_action": [
            {"action": row.action, "count": row.count}
            for row in audit_data
        ]
    }
