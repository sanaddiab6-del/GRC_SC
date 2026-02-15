"""
Incident Response API router (NCA ECC-IS-5).
"""
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
from typing import List, Optional
from datetime import datetime, timedelta
from uuid import UUID

from core.database import get_db
from auth.security import get_current_user, require_permission, log_audit_event
from auth.models import User
from .models import SecurityIncident, IncidentPlaybook, IncidentStatus, IncidentSeverity, IncidentCategory
from .schemas import (
    IncidentCreate, IncidentUpdate, IncidentResponse,
    PlaybookCreate, PlaybookResponse, IncidentReport
)

router = APIRouter()


def generate_incident_number() -> str:
    """Generate unique incident number (INC-YYYY-####)"""
    from datetime import datetime
    year = datetime.utcnow().year
    # In real implementation, query DB for last number
    return f"INC-{year}-001"


@router.post("/incidents", response_model=IncidentResponse, dependencies=[Depends(require_permission("incident:create"))])
async def create_incident(
    incident: IncidentCreate,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create security incident (NCA ECC-IS-5)"""
    try:
        # Generate incident number
        incident_number = generate_incident_number()
        
        # Create incident
        new_incident = SecurityIncident(
            incident_number=incident_number,
            **incident.model_dump(),
            reported_by=current_user.user_id,
            reported_at=datetime.utcnow()
        )
        
        db.add(new_incident)
        await db.commit()
        await db.refresh(new_incident)
        
        # Audit log
        await log_audit_event(
            db=db,
            user_id=str(current_user.user_id),
            action="incident.created",
            resource="incident",
            resource_id=str(new_incident.incident_id),
            status="success",
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
            details={
                "incident_number": incident_number,
                "severity": incident.severity.value,
                "category": incident.category.value
            }
        )
        
        return new_incident
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create incident: {str(e)}")


@router.get("/incidents", response_model=List[IncidentResponse], dependencies=[Depends(require_permission("incident:read"))])
async def list_incidents(
    status: Optional[IncidentStatus] = None,
    severity: Optional[IncidentSeverity] = None,
    category: Optional[IncidentCategory] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """List security incidents"""
    query = select(SecurityIncident)
    
    # Filters
    filters = []
    if status:
        filters.append(SecurityIncident.status == status)
    if severity:
        filters.append(SecurityIncident.severity == severity)
    if category:
        filters.append(SecurityIncident.category == category)
    
    if filters:
        query = query.where(and_(*filters))
    
    query = query.order_by(SecurityIncident.reported_at.desc()).offset(skip).limit(limit)
    
    result = await db.execute(query)
    incidents = result.scalars().all()
    return incidents


@router.get("/incidents/{incident_id}", response_model=IncidentResponse, dependencies=[Depends(require_permission("incident:read"))])
async def get_incident(
    incident_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get incident details"""
    result = await db.execute(
        select(SecurityIncident).where(SecurityIncident.incident_id == incident_id)
    )
    incident = result.scalar_one_or_none()
    
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    return incident


@router.patch("/incidents/{incident_id}", response_model=IncidentResponse, dependencies=[Depends(require_permission("incident:update"))])
async def update_incident(
    incident_id: UUID,
    update: IncidentUpdate,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update incident"""
    result = await db.execute(
        select(SecurityIncident).where(SecurityIncident.incident_id == incident_id)
    )
    incident = result.scalar_one_or_none()
    
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    # Update fields
    update_data = update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(incident, field, value)
    
    # Auto-update timestamps based on status
    if update.status == IncidentStatus.CONTAINED and getattr(incident, "contained_at") is None:
        setattr(incident, "contained_at", datetime.utcnow())
    elif update.status == IncidentStatus.RECOVERED and getattr(incident, "resolved_at") is None:
        setattr(incident, "resolved_at", datetime.utcnow())
    elif update.status == IncidentStatus.CLOSED and getattr(incident, "closed_at") is None:
        setattr(incident, "closed_at", datetime.utcnow())
    
    await db.commit()
    await db.refresh(incident)
    
    # Audit log
    await log_audit_event(
        db=db,
        user_id=str(current_user.user_id),
        action="incident.updated",
        resource="incident",
        resource_id=str(incident_id),
        status="success",
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        details=update_data
    )
    
    return incident


@router.post("/incidents/{incident_id}/report-nca", dependencies=[Depends(require_permission("incident:report"))])
async def report_to_nca(
    incident_id: UUID,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Report incident to NCA (required for HIGH/CRITICAL incidents)"""
    result = await db.execute(
        select(SecurityIncident).where(SecurityIncident.incident_id == incident_id)
    )
    incident = result.scalar_one_or_none()
    
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    # Mark as reported
    setattr(incident, "nca_reported", True)
    setattr(incident, "nca_reported_at", datetime.utcnow())
    
    await db.commit()
    
    # Audit log
    await log_audit_event(
        db=db,
        user_id=str(current_user.user_id),
        action="incident.reported_nca",
        resource="incident",
        resource_id=str(incident_id),
        status="success",
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent")
    )
    
    return {
        "message_en": "Incident reported to NCA successfully",
        "message_ar": "تم الإبلاغ عن الحادث إلى الهيئة الوطنية للأمن السيبراني بنجاح",
        "reported_at": incident.nca_reported_at
    }


# Playbook endpoints
@router.post("/playbooks", response_model=PlaybookResponse, dependencies=[Depends(require_permission("incident:manage"))])
async def create_playbook(
    playbook: PlaybookCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create incident response playbook"""
    new_playbook = IncidentPlaybook(
        **playbook.model_dump(),
        created_by=current_user.user_id
    )
    
    db.add(new_playbook)
    await db.commit()
    await db.refresh(new_playbook)
    
    return new_playbook


@router.get("/playbooks", response_model=List[PlaybookResponse], dependencies=[Depends(require_permission("incident:read"))])
async def list_playbooks(
    category: Optional[IncidentCategory] = None,
    is_active: bool = True,
    db: AsyncSession = Depends(get_db)
):
    """List incident playbooks"""
    query = select(IncidentPlaybook).where(IncidentPlaybook.is_active == is_active)
    
    if category:
        query = query.where(IncidentPlaybook.category == category)
    
    result = await db.execute(query)
    playbooks = result.scalars().all()
    return playbooks


@router.get("/playbooks/{playbook_id}", response_model=PlaybookResponse, dependencies=[Depends(require_permission("incident:read"))])
async def get_playbook(
    playbook_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get playbook details"""
    result = await db.execute(
        select(IncidentPlaybook).where(IncidentPlaybook.playbook_id == playbook_id)
    )
    playbook = result.scalar_one_or_none()
    
    if not playbook:
        raise HTTPException(status_code=404, detail="Playbook not found")
    
    return playbook


@router.get("/statistics/incidents")
async def get_incident_statistics(
    days: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("incident:read"))
):
    """Get incident statistics"""
    since_date = datetime.utcnow() - timedelta(days=days)
    
    # Count by severity
    severity_query = select(
        SecurityIncident.severity,
        func.count(SecurityIncident.incident_id).label('count')
    ).where(
        SecurityIncident.reported_at >= since_date
    ).group_by(SecurityIncident.severity)
    
    severity_result = await db.execute(severity_query)
    severity_stats = {row.severity.value: row.count for row in severity_result}
    
    # Count by status
    status_query = select(
        SecurityIncident.status,
        func.count(SecurityIncident.incident_id).label('count')
    ).where(
        SecurityIncident.reported_at >= since_date
    ).group_by(SecurityIncident.status)
    
    status_result = await db.execute(status_query)
    status_stats = {row.status.value: row.count for row in status_result}
    
    # Total incidents
    total_query = select(func.count(SecurityIncident.incident_id)).where(
        SecurityIncident.reported_at >= since_date
    )
    total_result = await db.execute(total_query)
    total = total_result.scalar()
    
    return {
        "period_days": days,
        "total_incidents": total,
        "by_severity": severity_stats,
        "by_status": status_stats,
        "message_en": f"Incident statistics for last {days} days",
        "message_ar": f"إحصائيات الحوادث لآخر {days} يوم"
    }
