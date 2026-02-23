"""
Audit Management Router - Phase 2.4 (Documentation & Certification).
Implements audit programs, engagement tracking, findings, and certifications.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Any, List, Optional
from datetime import datetime

from core.database import get_db
from auth.security import get_current_user, require_permission, require_role, log_audit_event
from auth.models import User
from audit.models import (
    AuditProgram, AuditEngagement, AuditFinding, CertificationRecord,
    AuditType, AuditStatus, FindingSeverity, FindingStatus,
)
from audit.schemas import (
    AuditProgramCreate, AuditProgramResponse,
    AuditFindingCreate, AuditFindingUpdate, AuditFindingResponse,
    CertificationCreate, CertificationResponse,
)

router = APIRouter()


# ===== AUDIT PROGRAM ENDPOINTS =====

@router.post("/audit/programs", response_model=AuditProgramResponse, status_code=201,
             dependencies=[Depends(require_role("Admin"))])
async def create_audit_program(
    program_data: AuditProgramCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create audit program (ISO 27001 Clause 9.2). Admin only."""
    year = program_data.audit_year
    type_code = program_data.audit_type.value.upper()[:3]
    count_result = await db.execute(
        select(func.count(AuditProgram.program_id))
        .where(AuditProgram.audit_year == year)
    )
    count = (count_result.scalar() or 0) + 1
    program_code = f"AUDIT-{year}-{type_code}-{count:03d}"

    program = AuditProgram(
        program_code=program_code,
        lead_auditor_id=current_user.user_id,
        **program_data.model_dump(),
    )

    db.add(program)
    await db.commit()
    await db.refresh(program)

    await log_audit_event(
        db=db,
        user_id=str(current_user.user_id),
        action="audit_program.created",
        resource="audit_program",
        resource_id=str(program.program_id),
        status="success",
        ip_address=None,
        user_agent=None,
        details={"program_code": program_code, "audit_type": program_data.audit_type.value},
    )

    return program


@router.get("/audit/programs", response_model=List[AuditProgramResponse])
async def list_audit_programs(
    audit_type: Optional[AuditType] = None,
    status: Optional[AuditStatus] = None,
    audit_year: Optional[int] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List audit programs."""
    from sqlalchemy import and_
    query = select(AuditProgram)
    filters = []
    if audit_type:
        filters.append(AuditProgram.audit_type == audit_type)
    if status:
        filters.append(AuditProgram.status == status)
    if audit_year:
        filters.append(AuditProgram.audit_year == audit_year)
    if filters:
        query = query.where(and_(*filters))

    query = query.order_by(AuditProgram.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/audit/programs/{program_id}", response_model=AuditProgramResponse)
async def get_audit_program(
    program_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get audit program details."""
    result = await db.execute(select(AuditProgram).where(AuditProgram.program_id == program_id))
    program = result.scalar_one_or_none()
    if not program:
        raise HTTPException(status_code=404, detail="Audit program not found")
    return program


# ===== AUDIT FINDINGS ENDPOINTS =====

@router.post("/audit/findings", response_model=AuditFindingResponse, status_code=201)
async def create_finding(
    finding_data: AuditFindingCreate,
    current_user: User = Depends(require_permission("controls", "create")),
    db: AsyncSession = Depends(get_db),
):
    """Create audit finding (ISO 27001 Clause 10.1)."""
    # Verify program exists
    prog_result = await db.execute(
        select(AuditProgram).where(AuditProgram.program_id == finding_data.program_id)
    )
    if not prog_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Audit program not found")

    count_result = await db.execute(
        select(func.count(AuditFinding.finding_id))
        .where(AuditFinding.program_id == finding_data.program_id)
    )
    count = (count_result.scalar() or 0) + 1
    finding_number = f"FIND-{finding_data.program_id}-{count:04d}"

    finding = AuditFinding(
        finding_number=finding_number,
        owner_id=current_user.user_id,
        **finding_data.model_dump(),
    )

    db.add(finding)
    await db.commit()
    await db.refresh(finding)

    await log_audit_event(
        db=db,
        user_id=str(current_user.user_id),
        action="audit_finding.created",
        resource="audit_finding",
        resource_id=str(finding.finding_id),
        status="success",
        ip_address=None,
        user_agent=None,
        details={"finding_number": finding_number, "severity": finding_data.severity.value},
    )

    return finding


@router.get("/audit/findings", response_model=List[AuditFindingResponse])
async def list_findings(
    program_id: Optional[int] = None,
    severity: Optional[FindingSeverity] = None,
    status: Optional[FindingStatus] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List audit findings."""
    from sqlalchemy import and_
    query = select(AuditFinding)
    filters = []
    if program_id:
        filters.append(AuditFinding.program_id == program_id)
    if severity:
        filters.append(AuditFinding.severity == severity)
    if status:
        filters.append(AuditFinding.status == status)
    if filters:
        query = query.where(and_(*filters))

    query = query.order_by(AuditFinding.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


@router.patch("/audit/findings/{finding_id}", response_model=AuditFindingResponse)
async def update_finding(
    finding_id: int,
    update_data: AuditFindingUpdate,
    current_user: User = Depends(require_permission("controls", "update")),
    db: AsyncSession = Depends(get_db),
):
    """Update audit finding status and remediation plan."""
    result = await db.execute(select(AuditFinding).where(AuditFinding.finding_id == finding_id))
    finding = result.scalar_one_or_none()
    if not finding:
        raise HTTPException(status_code=404, detail="Finding not found")

    for field, value in update_data.model_dump(exclude_unset=True).items():
        setattr(finding, field, value)

    await db.commit()
    await db.refresh(finding)
    return finding


# ===== CERTIFICATION RECORDS ENDPOINTS =====

@router.post("/audit/certifications", response_model=CertificationResponse, status_code=201,
             dependencies=[Depends(require_role("Admin"))])
async def create_certification(
    cert_data: CertificationCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Register compliance certification (ISO 27001, NCA, SOC2, etc.)."""
    cert = CertificationRecord(**cert_data.model_dump())
    db.add(cert)
    await db.commit()
    await db.refresh(cert)

    await log_audit_event(
        db=db,
        user_id=str(current_user.user_id),
        action="certification.created",
        resource="certification",
        resource_id=str(cert.certification_id),
        status="success",
        ip_address=None,
        user_agent=None,
        details={"standard": cert_data.certification_standard, "cert_number": cert_data.certificate_number},
    )

    return cert


@router.get("/audit/certifications", response_model=List[CertificationResponse])
async def list_certifications(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all certification records."""
    result = await db.execute(
        select(CertificationRecord).order_by(CertificationRecord.expiry_date.asc())
    )
    return result.scalars().all()


@router.get("/audit/statistics")
async def audit_statistics(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Audit program compliance statistics."""
    from sqlalchemy import and_

    total_programs = (await db.execute(select(func.count(AuditProgram.program_id)))).scalar() or 0
    open_findings = (await db.execute(
        select(func.count(AuditFinding.finding_id)).where(
            AuditFinding.status == FindingStatus.OPEN
        )
    )).scalar() or 0
    critical_findings = (await db.execute(
        select(func.count(AuditFinding.finding_id)).where(
            and_(
                AuditFinding.severity == FindingSeverity.CRITICAL,
                AuditFinding.status == FindingStatus.OPEN,
            )
        )
    )).scalar() or 0
    active_certs = (await db.execute(
        select(func.count(CertificationRecord.certification_id)).where(
            CertificationRecord.status == "active"
        )
    )).scalar() or 0

    return {
        "total_audit_programs": total_programs,
        "open_findings": open_findings,
        "critical_open_findings": critical_findings,
        "active_certifications": active_certs,
        "message_en": "Audit statistics",
        "message_ar": "إحصائيات التدقيق",
    }
