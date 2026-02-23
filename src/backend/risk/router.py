"""
Risk Management API router (NCA ECC-RM).
"""
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
from typing import List, Optional
from datetime import datetime, timedelta
from uuid import UUID

from core.database import get_db
from core.crud_utils import get_by_id, update_model
from core.audit_utils import log_create_event, log_update_event
from auth.security import get_current_user, require_permission, log_audit_event
from auth.models import User
from .models import Risk, RiskAssessment, ThirdPartyRisk, RiskCategory, RiskStatus, TreatmentStatus
from .schemas import (
    RiskCreate, RiskUpdate, RiskResponse,
    AssessmentCreate, AssessmentResponse,
    VendorCreate, VendorUpdate, VendorResponse
)

router = APIRouter()


def generate_risk_number() -> str:
    """Generate unique risk number (RISK-YYYY-####)"""
    from datetime import datetime
    year = datetime.utcnow().year
    # In real implementation, query DB for last number
    return f"RISK-{year}-001"


def calculate_risk_score(likelihood: int, impact: int) -> tuple[int, str]:
    """Calculate risk score and level (NCA ECC-RM-1)"""
    score = likelihood * impact
    
    if score <= 5:
        level = "low"
    elif score <= 12:
        level = "medium"
    elif score <= 20:
        level = "high"
    else:
        level = "critical"
    
    return score, level


@router.post("/risks", response_model=RiskResponse, dependencies=[Depends(require_permission("risk:create"))])
async def create_risk(
    risk: RiskCreate,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create risk (NCA ECC-RM-1)"""
    try:
        # Generate risk number
        risk_number = generate_risk_number()
        
        # Calculate inherent risk
        inherent_score, inherent_level = calculate_risk_score(risk.likelihood, risk.impact)
        
        # Calculate residual risk (if controls exist)
        residual_likelihood = risk.likelihood
        residual_impact = risk.impact
        if risk.control_effectiveness:
            # Reduce likelihood based on control effectiveness
            reduction = risk.control_effectiveness / 5.0
            residual_likelihood = max(1, int(risk.likelihood * (1 - reduction)))
        
        residual_score, residual_level = calculate_risk_score(residual_likelihood, residual_impact)
        
        # Create risk
        new_risk = Risk(
            risk_number=risk_number,
            **risk.model_dump(),
            identified_by=current_user.user_id,
            inherent_risk_score=inherent_score,
            inherent_risk_level=inherent_level,
            residual_likelihood=residual_likelihood,
            residual_impact=residual_impact,
            residual_risk_score=residual_score,
            residual_risk_level=residual_level,
            next_review_date=datetime.utcnow() + timedelta(days=90)  # Review every 90 days
        )
        
        db.add(new_risk)
        await db.commit()
        await db.refresh(new_risk)
        
        # Audit log
        await log_audit_event(
            db=db,
            user_id=str(current_user.user_id),
            action="risk.created",
            resource="risk",
            resource_id=str(new_risk.risk_id),
            status="success",
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
            details={
                "risk_number": risk_number,
                "category": risk.category.value,
                "inherent_score": inherent_score,
                "residual_score": residual_score
            }
        )
        
        return new_risk
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create risk: {str(e)}")


@router.get("/risks", response_model=List[RiskResponse], dependencies=[Depends(require_permission("risk:read"))])
async def list_risks(
    category: Optional[RiskCategory] = None,
    status: Optional[RiskStatus] = None,
    min_risk_score: Optional[int] = Query(None, ge=1, le=25),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """List risks"""
    query = select(Risk)
    
    # Filters
    filters = []
    if category:
        filters.append(Risk.category == category)
    if status:
        filters.append(Risk.status == status)
    if min_risk_score:
        filters.append(Risk.residual_risk_score >= min_risk_score)
    
    if filters:
        query = query.where(and_(*filters))
    
    query = query.order_by(Risk.residual_risk_score.desc()).offset(skip).limit(limit)
    
    result = await db.execute(query)
    risks = result.scalars().all()
    return risks


@router.get("/risks/{risk_id}", response_model=RiskResponse, dependencies=[Depends(require_permission("risk:read"))])
async def get_risk(
    risk_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get risk details"""
    risk = await get_by_id(
        db=db,
        model=Risk,
        id_field_name="risk_id",
        id_value=risk_id,
        error_message_en="Risk not found",
        error_message_ar="لم يتم العثور على المخاطر",
    )
    return risk


@router.patch("/risks/{risk_id}", response_model=RiskResponse, dependencies=[Depends(require_permission("risk:update"))])
async def update_risk(
    risk_id: UUID,
    update: RiskUpdate,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update risk"""
    risk = await get_by_id(
        db=db,
        model=Risk,
        id_field_name="risk_id",
        id_value=risk_id,
        error_message_en="Risk not found",
        error_message_ar="لم يتم العثور على المخاطر",
    )
    
    # Update fields
    update_data = update.model_dump(exclude_unset=True)

    # Enforce strict lifecycle transitions for status/state
    if "status" in update_data:
        from core.lifecycle_transitions import RISK_TRANSITIONS
        current_status = getattr(risk, "status")
        new_status = update_data["status"]
        allowed = RISK_TRANSITIONS.get(current_status, [])
        if new_status != current_status and new_status not in allowed:
            tooltip = (
                f"Transition from '{current_status}' to '{new_status}' is not allowed. "
                f"Allowed: {allowed if allowed else 'No further transitions.'}"
            )
            raise HTTPException(
                status_code=400,
                detail={
                    "message_en": f"Invalid status transition: {current_status} → {new_status}",
                    "message_ar": f"الانتقال من الحالة '{current_status}' إلى '{new_status}' غير مسموح.",
                    "tooltip": tooltip,
                },
            )

    for field, value in update_data.items():
        setattr(risk, field, value)
    
    # Recalculate risk if likelihood or impact changed
    if update.likelihood or update.impact:
        likelihood_value = int(update.likelihood or getattr(risk, "likelihood") or 0)
        impact_value = int(update.impact or getattr(risk, "impact") or 0)
        score, level = calculate_risk_score(likelihood_value, impact_value)
        setattr(risk, "inherent_risk_score", score)
        setattr(risk, "inherent_risk_level", level)
        
        # Recalculate residual
        control_effectiveness = int(getattr(risk, "control_effectiveness") or 0)
        if control_effectiveness:
            reduction = control_effectiveness / 5.0
            residual_likelihood = max(1, int(likelihood_value * (1 - reduction)))
            residual_score, residual_level = calculate_risk_score(residual_likelihood, impact_value)
            setattr(risk, "residual_likelihood", residual_likelihood)
            setattr(risk, "residual_risk_score", residual_score)
            setattr(risk, "residual_risk_level", residual_level)
    
    await db.commit()
    await db.refresh(risk)
    
    # Audit log
    await log_update_event(
        db=db,
        user_id=str(current_user.user_id),
        resource="risk",
        resource_id=str(risk_id),
        request=request,
        details=update_data,
    )
    
    return risk


# Risk assessment endpoints
@router.post("/risks/{risk_id}/assess", response_model=AssessmentResponse, dependencies=[Depends(require_permission("risk:assess"))])
async def create_assessment(
    risk_id: UUID,
    assessment: AssessmentCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create risk assessment (NCA ECC-RM-1)"""
    # Verify risk exists
    result = await db.execute(select(Risk).where(Risk.risk_id == risk_id))
    risk = result.scalar_one_or_none()
    if not risk:
        raise HTTPException(status_code=404, detail="Risk not found")
    
    # Calculate score
    score, level = calculate_risk_score(assessment.likelihood, assessment.impact)
    
    # Create assessment
    new_assessment = RiskAssessment(
        risk_id=risk_id,
        assessed_by=current_user.user_id,
        **assessment.model_dump(exclude={'risk_id'}),
        risk_score=score,
        risk_level=level
    )
    
    db.add(new_assessment)
    
    # Update risk
    setattr(risk, "last_assessed_at", datetime.utcnow())
    setattr(risk, "next_review_date", datetime.utcnow() + timedelta(days=90))
    
    await db.commit()
    await db.refresh(new_assessment)
    
    return new_assessment


@router.get("/risks/{risk_id}/assessments", response_model=List[AssessmentResponse], dependencies=[Depends(require_permission("risk:read"))])
async def list_assessments(
    risk_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get risk assessment history"""
    result = await db.execute(
        select(RiskAssessment)
        .where(RiskAssessment.risk_id == risk_id)
        .order_by(RiskAssessment.assessed_at.desc())
    )
    assessments = result.scalars().all()
    return assessments


# Third-party vendor risk endpoints
@router.post("/vendors", response_model=VendorResponse, dependencies=[Depends(require_permission("risk:manage"))])
async def create_vendor(
    vendor: VendorCreate,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create third-party vendor risk assessment (NCA ECC-RM-3)"""
    new_vendor = ThirdPartyRisk(
        **vendor.model_dump(),
        vendor_manager=current_user.user_id,
        review_frequency_days=365,
        next_review_date=datetime.utcnow() + timedelta(days=365)
    )
    
    db.add(new_vendor)
    await db.commit()
    await db.refresh(new_vendor)
    
    # Audit log
    await log_audit_event(
        db=db,
        user_id=str(current_user.user_id),
        action="vendor.created",
        resource="vendor",
        resource_id=str(new_vendor.vendor_id),
        status="success",
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        details={"vendor_name": vendor.vendor_name, "risk_rating": vendor.risk_rating}
    )
    
    return new_vendor


@router.get("/vendors", response_model=List[VendorResponse], dependencies=[Depends(require_permission("risk:read"))])
async def list_vendors(
    risk_rating: Optional[str] = None,
    is_active: bool = True,
    db: AsyncSession = Depends(get_db)
):
    """List third-party vendors"""
    query = select(ThirdPartyRisk).where(ThirdPartyRisk.is_active == is_active)
    
    if risk_rating:
        query = query.where(ThirdPartyRisk.risk_rating == risk_rating)
    
    result = await db.execute(query)
    vendors = result.scalars().all()
    return vendors


@router.get("/vendors/{vendor_id}", response_model=VendorResponse, dependencies=[Depends(require_permission("risk:read"))])
async def get_vendor(
    vendor_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get vendor details"""
    vendor = await get_by_id(
        db=db,
        model=ThirdPartyRisk,
        id_field_name="vendor_id",
        id_value=vendor_id,
        error_message_en="Vendor not found",
        error_message_ar="لم يتم العثور على البائع",
    )
    return vendor


@router.patch("/vendors/{vendor_id}", response_model=VendorResponse, dependencies=[Depends(require_permission("risk:update"))])
async def update_vendor(
    vendor_id: UUID,
    update: VendorUpdate,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update vendor risk assessment"""
    vendor = await get_by_id(
        db=db,
        model=ThirdPartyRisk,
        id_field_name="vendor_id",
        id_value=vendor_id,
        error_message_en="Vendor not found",
        error_message_ar="لم يتم العثور على البائع",
    )
    
    vendor = await update_model(item=vendor, update_data=update, db=db)
    
    # Audit log
    await log_update_event(
        db=db,
        user_id=str(current_user.user_id),
        resource="vendor",
        resource_id=str(vendor_id),
        request=request,
        details=update.model_dump(exclude_unset=True),
    )
    
    return vendor


@router.get("/statistics/risks")
async def get_risk_statistics(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("risk:read"))
):
    """Get risk statistics"""
    # Count by level
    level_query = select(
        Risk.residual_risk_level,
        func.count(Risk.risk_id).label('count')
    ).where(
        Risk.status != RiskStatus.CLOSED
    ).group_by(Risk.residual_risk_level)
    
    level_result = await db.execute(level_query)
    level_stats = {row.residual_risk_level: row.count for row in level_result if row.residual_risk_level}
    
    # Count by category
    category_query = select(
        Risk.category,
        func.count(Risk.risk_id).label('count')
    ).where(
        Risk.status != RiskStatus.CLOSED
    ).group_by(Risk.category)
    
    category_result = await db.execute(category_query)
    category_stats = {row.category.value: row.count for row in category_result}
    
    # Total risks
    total_query = select(func.count(Risk.risk_id)).where(Risk.status != RiskStatus.CLOSED)
    total_result = await db.execute(total_query)
    total = total_result.scalar()
    
    # Risks exceeding tolerance
    exceeding_query = select(func.count(Risk.risk_id)).where(
        and_(
            Risk.status != RiskStatus.CLOSED,
            Risk.risk_tolerance_exceeded == True
        )
    )
    exceeding_result = await db.execute(exceeding_query)
    exceeding = exceeding_result.scalar()
    
    return {
        "total_active_risks": total,
        "by_level": level_stats,
        "by_category": category_stats,
        "exceeding_tolerance": exceeding,
        "message_en": "Risk register statistics",
        "message_ar": "إحصائيات سجل المخاطر"
    }
