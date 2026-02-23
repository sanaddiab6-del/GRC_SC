"""
Evidence API Router
Endpoints for evidence management
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional
from datetime import datetime, timedelta

from core.database import get_db
from evidence.models import Evidence, EvidenceStatus
from evidence.schemas import (
    EvidenceCreate,
    EvidenceUpdate,
    EvidenceResponse,
    EvidenceListResponse,
    EvidenceValidationRequest,
)
Evidence Router
API endpoints for evidence management
"""

from fastapi import APIRouter

router = APIRouter()


@router.get("/evidence", response_model=EvidenceListResponse)
async def list_evidence(
    control_id: Optional[str] = Query(None, description="Filter by control ID"),
    status: Optional[str] = Query(None, description="Filter by status"),
    evidence_type: Optional[str] = Query(None, description="Filter by evidence type"),
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """
    Get paginated list of evidence with filtering
    """
    query = select(Evidence)
    
    # Apply filters
    if control_id:
        query = query.where(Evidence.control_id == control_id)
    if status:
        query = query.where(Evidence.status == status)
    if evidence_type:
        query = query.where(Evidence.evidence_type == evidence_type)
    
    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_query)
    
    # Apply pagination
    query = query.offset(offset).limit(limit)
    result = await db.execute(query)
    items = result.scalars().all()
    
    response_items = [EvidenceResponse.model_validate(item) for item in items]
    return EvidenceListResponse(
        total=total or 0,
        offset=offset,
        limit=limit,
        items=response_items,
    )


@router.get("/evidence/{evidence_id}", response_model=EvidenceResponse)
async def get_evidence(
    evidence_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get specific evidence by ID"""
    query = select(Evidence).where(Evidence.evidence_id == evidence_id)
    result = await db.execute(query)
    evidence = result.scalar_one_or_none()
    
    if not evidence:
        raise HTTPException(
            status_code=404,
            detail={
                "message_en": f"Evidence {evidence_id} not found",
                "message_ar": f"لم يتم العثور على الدليل {evidence_id}",
            },
        )
    
    return evidence


@router.post("/evidence", response_model=EvidenceResponse, status_code=201)
async def create_evidence(
    evidence_data: EvidenceCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create new evidence"""
    # Check if evidence_id already exists
    existing = await db.execute(
        select(Evidence).where(Evidence.evidence_id == evidence_data.evidence_id)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=400,
            detail={
                "message_en": f"Evidence {evidence_data.evidence_id} already exists",
                "message_ar": f"الدليل {evidence_data.evidence_id} موجود بالفعل",
            },
        )
    
    # Calculate expiry date
    collection_date = datetime.utcnow()
    expiry_date = collection_date + timedelta(days=evidence_data.retention_period_days)
    
    evidence = Evidence(
        **evidence_data.model_dump(),
        collection_date=collection_date,
        expiry_date=expiry_date,
    )
    
    db.add(evidence)
    await db.commit()
    await db.refresh(evidence)
    
    return evidence


@router.patch("/evidence/{evidence_id}", response_model=EvidenceResponse)
async def update_evidence(
    evidence_id: str,
    evidence_data: EvidenceUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update evidence (partial update)"""
    query = select(Evidence).where(Evidence.evidence_id == evidence_id)
    result = await db.execute(query)
    evidence = result.scalar_one_or_none()
    
    if not evidence:
        raise HTTPException(
            status_code=404,
            detail={
                "message_en": f"Evidence {evidence_id} not found",
                "message_ar": f"لم يتم العثور على الدليل {evidence_id}",
            },
        )
    
    # Update only provided fields
    update_data = evidence_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(evidence, field, value)
    
    await db.commit()
    await db.refresh(evidence)
    
    return evidence


@router.post("/evidence/{evidence_id}/validate", response_model=EvidenceResponse)
async def validate_evidence(
    evidence_id: str,
    validation: EvidenceValidationRequest,
    db: AsyncSession = Depends(get_db),
):
    """Validate or reject evidence"""
    query = select(Evidence).where(Evidence.evidence_id == evidence_id)
    result = await db.execute(query)
    evidence = result.scalar_one_or_none()
    
    if not evidence:
        raise HTTPException(
            status_code=404,
            detail={
                "message_en": f"Evidence {evidence_id} not found",
                "message_ar": f"لم يتم العثور على الدليل {evidence_id}",
            },
        )
    
    # Update validation status
    setattr(evidence, "validated_by", validation.validated_by)
    setattr(evidence, "validated_at", datetime.utcnow())
    setattr(evidence, "validation_notes", validation.validation_notes)
    setattr(
        evidence,
        "status",
        EvidenceStatus.VALIDATED if validation.approved else EvidenceStatus.REJECTED,
    )
    
    await db.commit()
    await db.refresh(evidence)
    
    return evidence


@router.delete("/evidence/{evidence_id}", status_code=204)
async def delete_evidence(
    evidence_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Delete evidence"""
    query = select(Evidence).where(Evidence.evidence_id == evidence_id)
    result = await db.execute(query)
    evidence = result.scalar_one_or_none()
    
    if not evidence:
        raise HTTPException(
            status_code=404,
            detail={
                "message_en": f"Evidence {evidence_id} not found",
                "message_ar": f"لم يتم العثور على الدليل {evidence_id}",
            },
        )
    
    await db.delete(evidence)
    await db.commit()


@router.get("/evidence/control/{control_id}/summary")
async def get_control_evidence_summary(
    control_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get evidence summary for a control"""
    query = select(Evidence).where(Evidence.control_id == control_id)
    result = await db.execute(query)
    evidence_list = result.scalars().all()
    
    # Calculate summary statistics
    total = len(evidence_list)
    by_status = {}
    by_type = {}
    
    for evidence in evidence_list:
        status = evidence.status.value
        etype = evidence.evidence_type.value
        by_status[status] = by_status.get(status, 0) + 1
        by_type[etype] = by_type.get(etype, 0) + 1
    
    return {
        "control_id": control_id,
        "total_evidence": total,
        "by_status": by_status,
        "by_type": by_type,
        "compliance_rate": (by_status.get("validated", 0) / total * 100) if total > 0 else 0,
    }

@router.get("/")
async def list_evidence():
    """List all evidence"""
    return {"evidence": []}


@router.post("/")
async def create_evidence():
    """Create new evidence"""
    return {"status": "created"}
