"""
Privacy Management Router - PDPL Compliance
Implements consent management, DSAR, breach notification, and data classification
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from datetime import datetime, timedelta
from typing import List
import secrets

from core.database import get_db
from privacy import schemas
from privacy.models import (
    Consent, ConsentStatus, DataSubjectRequest, DSARStatus, DSARType,
    DataClassificationTag, DataBreachIncident, DataRetentionPolicy,
    PrivacyImpactAssessment
)
from auth.security import get_current_user, require_permission, require_role, log_audit_event
from auth.models import User


router = APIRouter(prefix="/privacy", tags=["Privacy & PDPL"])


# ===== CONSENT MANAGEMENT =====

@router.post("/consent", response_model=schemas.ConsentResponse, status_code=201)
async def give_consent(
    consent_data: schemas.ConsentCreate,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Give consent for data processing (PDPL Article 6).
    User agrees to specific data processing purposes.
    """
    consent = Consent(
        user_id=current_user.user_id,
        consent_type=consent_data.consent_type,
        purpose_en=consent_data.purpose_en,
        purpose_ar=consent_data.purpose_ar,
        legal_basis_en=consent_data.legal_basis_en,
        legal_basis_ar=consent_data.legal_basis_ar,
        consent_text_en=consent_data.consent_text_en,
        consent_text_ar=consent_data.consent_text_ar,
        expires_at=consent_data.expires_at,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent")
    )
    
    db.add(consent)
    await db.commit()
    await db.refresh(consent)
    
    # Audit log
    await log_audit_event(
        db=db,
        user_id=str(current_user.user_id),
        action="consent_given",
        resource="privacy",
        resource_id=str(consent.consent_id),
        status="success",
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        details={"consent_type": consent_data.consent_type}
    )
    
    return consent


@router.get("/consent", response_model=List[schemas.ConsentResponse])
async def list_my_consents(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List all consents for current user."""
    result = await db.execute(
        select(Consent).where(Consent.user_id == current_user.user_id).order_by(Consent.given_at.desc())
    )
    consents = result.scalars().all()
    return consents


@router.post("/consent/{consent_id}/withdraw")
async def withdraw_consent(
    consent_id: str,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Withdraw consent (PDPL Article 8).
    User can withdraw consent at any time.
    """
    result = await db.execute(
        select(Consent).where(
            and_(Consent.consent_id == consent_id, Consent.user_id == current_user.user_id)
        )
    )
    consent = result.scalar_one_or_none()
    
    if not consent:
        raise HTTPException(status_code=404, detail="Consent not found")
    
    if getattr(consent, "status") == ConsentStatus.WITHDRAWN:
        raise HTTPException(status_code=400, detail="Consent already withdrawn")
    
    setattr(consent, "status", ConsentStatus.WITHDRAWN)
    setattr(consent, "withdrawn_at", datetime.utcnow())
    
    await db.commit()
    
    # Audit log
    await log_audit_event(
        db=db,
        user_id=str(current_user.user_id),
        action="consent_withdrawn",
        resource="privacy",
        resource_id=str(consent_id),
        status="success",
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent")
    )
    
    return {"message": "Consent withdrawn successfully", "message_ar": "تم سحب الموافقة بنجاح"}


# ===== DATA SUBJECT ACCESS REQUESTS (DSAR) =====

@router.post("/dsar", response_model=schemas.DSARResponse, status_code=201)
async def create_dsar(
    dsar_data: schemas.DSARCreate,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create Data Subject Access Request (PDPL Articles 4-9).
    User can request access, rectification, erasure, portability, etc.
    """
    # Calculate due date (PDPL: 30 days maximum)
    due_date = datetime.utcnow() + timedelta(days=30)
    
    dsar = DataSubjectRequest(
        user_id=current_user.user_id,
        request_type=dsar_data.request_type,
        description_en=dsar_data.description_en,
        description_ar=dsar_data.description_ar,
        verification_method=dsar_data.verification_method,
        due_date=due_date
    )
    
    db.add(dsar)
    await db.commit()
    await db.refresh(dsar)
    
    # Audit log
    await log_audit_event(
        db=db,
        user_id=str(current_user.user_id),
        action="dsar_created",
        resource="privacy",
        resource_id=str(dsar.request_id),
        status="success",
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        details={"request_type": dsar_data.request_type}
    )
    
    return dsar


@router.get("/dsar", response_model=List[schemas.DSARResponse])
async def list_my_dsars(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List all DSARs for current user."""
    result = await db.execute(
        select(DataSubjectRequest).where(
            DataSubjectRequest.user_id == current_user.user_id
        ).order_by(DataSubjectRequest.requested_at.desc())
    )
    dsars = result.scalars().all()
    return dsars


@router.get("/dsar/{request_id}", response_model=schemas.DSARResponse)
async def get_dsar(
    request_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get DSAR details."""
    result = await db.execute(
        select(DataSubjectRequest).where(DataSubjectRequest.request_id == request_id)
    )
    dsar = result.scalar_one_or_none()
    
    if not dsar:
        raise HTTPException(status_code=404, detail="DSAR not found")
    
    # Users can only see their own DSARs (unless admin)
    if str(dsar.user_id) != str(current_user.user_id):
        # Check if user is admin or compliance officer
        user_roles = [role.role_name for role in current_user.roles]
        if "Admin" not in user_roles and "Compliance Officer" not in user_roles:
            raise HTTPException(status_code=403, detail="Access denied")
    
    return dsar


@router.patch("/dsar/{request_id}", response_model=schemas.DSARResponse)
async def update_dsar(
    request_id: str,
    dsar_update: schemas.DSARUpdate,
    current_user: User = Depends(require_permission("users", "update")),  # Admin/Compliance Officer
    db: AsyncSession = Depends(get_db)
):
    """
    Update DSAR (Admin/Compliance Officer only).
    Process and respond to data subject requests.
    """
    result = await db.execute(
        select(DataSubjectRequest).where(DataSubjectRequest.request_id == request_id)
    )
    dsar = result.scalar_one_or_none()
    
    if not dsar:
        raise HTTPException(status_code=404, detail="DSAR not found")
    
    # Update fields
    if dsar_update.status:
        setattr(dsar, "status", dsar_update.status)
        if dsar_update.status == DSARStatus.COMPLETED:
            setattr(dsar, "completed_at", datetime.utcnow())
    
    if dsar_update.processor_notes:
        setattr(dsar, "processor_notes", dsar_update.processor_notes)
    
    if dsar_update.response_en:
        setattr(dsar, "response_en", dsar_update.response_en)
    
    if dsar_update.response_ar:
        setattr(dsar, "response_ar", dsar_update.response_ar)
    
    if dsar_update.rejection_reason_en:
        setattr(dsar, "rejection_reason_en", dsar_update.rejection_reason_en)
    
    if dsar_update.rejection_reason_ar:
        setattr(dsar, "rejection_reason_ar", dsar_update.rejection_reason_ar)
    
    # Assign to current user if not assigned
    if getattr(dsar, "assigned_to") is None:
        setattr(dsar, "assigned_to", current_user.user_id)
        setattr(dsar, "assigned_at", datetime.utcnow())
    
    await db.commit()
    await db.refresh(dsar)
    
    # Audit log
    await log_audit_event(
        db=db,
        user_id=str(current_user.user_id),
        action="dsar_updated",
        resource="privacy",
        resource_id=str(request_id),
        status="success",
        ip_address=None,
        user_agent=None,
        details={"new_status": dsar_update.status}
    )
    
    return dsar


# ===== DATA BREACH NOTIFICATION =====

@router.post("/breach", response_model=schemas.DataBreachResponse, status_code=201)
async def report_breach(
    breach_data: schemas.DataBreachCreate,
    request: Request,
    current_user: User = Depends(require_role("Admin")),  # Admin only
    db: AsyncSession = Depends(get_db)
):
    """
    Report data breach (PDPL Article 27).
    Must notify SDAIA within 72 hours for high-severity breaches.
    """
    # Generate incident number
    year = datetime.utcnow().year
    count_result = await db.execute(
        select(DataBreachIncident).where(DataBreachIncident.incident_number.like(f"BR-{year}-%"))
    )
    count = len(count_result.scalars().all()) + 1
    incident_number = f"BR-{year}-{count:04d}"
    
    breach = DataBreachIncident(
        incident_number=incident_number,
        discovered_at=breach_data.discovered_at,
        breach_type=breach_data.breach_type,
        severity=breach_data.severity,
        affected_records_count=breach_data.affected_records_count,
        affected_data_types=breach_data.affected_data_types,
        impact_description_en=breach_data.impact_description_en,
        impact_description_ar=breach_data.impact_description_ar,
        containment_actions_en=breach_data.containment_actions_en,
        containment_actions_ar=breach_data.containment_actions_ar,
        discovered_by=current_user.user_id,
        incident_manager=current_user.user_id
    )
    
    db.add(breach)
    await db.commit()
    await db.refresh(breach)
    
    # Audit log
    await log_audit_event(
        db=db,
        user_id=str(current_user.user_id),
        action="breach_reported",
        resource="privacy",
        resource_id=str(breach.incident_id),
        status="success",
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        details={"severity": breach_data.severity, "affected_records": breach_data.affected_records_count}
    )
    
    return breach


@router.get("/breach", response_model=List[schemas.DataBreachResponse])
async def list_breaches(
    current_user: User = Depends(require_role("Admin")),
    db: AsyncSession = Depends(get_db)
):
    """List all data breach incidents (Admin only)."""
    result = await db.execute(
        select(DataBreachIncident).order_by(DataBreachIncident.reported_at.desc())
    )
    breaches = result.scalars().all()
    return breaches


# ===== DATA CLASSIFICATION =====

@router.post("/classification", response_model=schemas.DataClassificationResponse, status_code=201)
async def classify_data(
    classification_data: schemas.DataClassificationCreate,
    current_user: User = Depends(require_permission("controls", "create")),
    db: AsyncSession = Depends(get_db)
):
    """
    Classify data asset (NCA CCC-SEC-01).
    Tag resources with classification level.
    """
    tag = DataClassificationTag(
        resource_type=classification_data.resource_type,
        resource_id=classification_data.resource_id,
        classification=classification_data.classification,
        reason_en=classification_data.reason_en,
        reason_ar=classification_data.reason_ar,
        classified_by=current_user.user_id
    )
    
    db.add(tag)
    await db.commit()
    await db.refresh(tag)
    
    return tag


@router.get("/classification/{resource_type}/{resource_id}")
async def get_classification(
    resource_type: str,
    resource_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get classification for a resource."""
    result = await db.execute(
        select(DataClassificationTag).where(
            and_(
                DataClassificationTag.resource_type == resource_type,
                DataClassificationTag.resource_id == resource_id
            )
        )
    )
    tag = result.scalar_one_or_none()
    
    if not tag:
        return {"classification": "INTERNAL", "message": "No classification set, defaulting to INTERNAL"}
    
    return tag


# ===== RETENTION POLICIES =====

@router.post("/retention", response_model=schemas.RetentionPolicyResponse, status_code=201)
async def create_retention_policy(
    policy_data: schemas.RetentionPolicyCreate,
    current_user: User = Depends(require_role("Admin")),
    db: AsyncSession = Depends(get_db)
):
    """
    Create data retention policy (PDPL Article 12).
    Define how long data should be kept.
    """
    policy = DataRetentionPolicy(
        resource_type=policy_data.resource_type,
        retention_period_days=policy_data.retention_period_days,
        legal_basis_en=policy_data.legal_basis_en,
        legal_basis_ar=policy_data.legal_basis_ar,
        auto_delete_enabled=policy_data.auto_delete_enabled,
        deletion_method=policy_data.deletion_method,
        created_by=current_user.user_id
    )
    
    db.add(policy)
    await db.commit()
    await db.refresh(policy)
    
    return policy


@router.get("/retention", response_model=List[schemas.RetentionPolicyResponse])
async def list_retention_policies(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List all retention policies."""
    result = await db.execute(select(DataRetentionPolicy))
    policies = result.scalars().all()
    return policies


# ===== PRIVACY IMPACT ASSESSMENTS =====

@router.post("/pia", response_model=schemas.PIAResponse, status_code=201)
async def create_pia(
    pia_data: schemas.PIACreate,
    current_user: User = Depends(require_role("Admin")),
    db: AsyncSession = Depends(get_db)
):
    """
    Create Privacy Impact Assessment (PDPL Article 33).
    Required for high-risk processing activities.
    """
    # Calculate risk score
    risk_score = 0
    if pia_data.privacy_risks:
        for risk in pia_data.privacy_risks:
            risk_score += risk.get("impact", 0)
        risk_score = min(risk_score // len(pia_data.privacy_risks), 10)
    
    # Determine risk level
    if risk_score >= 8:
        risk_level = "critical"
    elif risk_score >= 6:
        risk_level = "high"
    elif risk_score >= 4:
        risk_level = "medium"
    else:
        risk_level = "low"
    
    pia = PrivacyImpactAssessment(
        project_name_en=pia_data.project_name_en,
        project_name_ar=pia_data.project_name_ar,
        description_en=pia_data.description_en,
        description_ar=pia_data.description_ar,
        data_types=pia_data.data_types,
        processing_purpose_en=pia_data.processing_purpose_en,
        processing_purpose_ar=pia_data.processing_purpose_ar,
        legal_basis_en=pia_data.legal_basis_en,
        legal_basis_ar=pia_data.legal_basis_ar,
        privacy_risks=pia_data.privacy_risks,
        risk_score=risk_score,
        risk_level=risk_level,
        mitigation_measures_en=pia_data.mitigation_measures_en,
        mitigation_measures_ar=pia_data.mitigation_measures_ar,
        conducted_by=current_user.user_id
    )
    
    db.add(pia)
    await db.commit()
    await db.refresh(pia)
    
    return pia


@router.get("/pia", response_model=List[schemas.PIAResponse])
async def list_pias(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List all Privacy Impact Assessments."""
    result = await db.execute(
        select(PrivacyImpactAssessment).order_by(PrivacyImpactAssessment.conducted_at.desc())
    )
    pias = result.scalars().all()
    return pias
