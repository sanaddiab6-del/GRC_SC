"""
Evidence API Router
Endpoints for evidence management with tamper protection
"""

import hashlib
from typing import Optional
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from core.database import get_db
from core.crud_utils import get_by_id, check_exists, update_model, delete_by_id
from evidence.models import Evidence, EvidenceStatus
from evidence.schemas import (
    EvidenceCreate,
    EvidenceUpdate,
    EvidenceResponse,
    EvidenceListResponse,
    EvidenceValidationRequest,
    EvidenceIntegrityResponse,
)

router = APIRouter()


def _compute_evidence_hash(evidence_data: EvidenceCreate) -> str:
    """Compute a SHA-256 fingerprint of the evidence content for tamper detection."""
    payload = (
        f"{evidence_data.evidence_id}|{evidence_data.control_id}|"
        f"{evidence_data.title_en}|{evidence_data.title_ar}|"
        f"{evidence_data.file_name or ''}|{evidence_data.file_size or 0}"
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


@router.get("/evidence", response_model=EvidenceListResponse)
async def list_evidence(
    control_id: Optional[str] = Query(None, description="Filter by control ID"),
    status: Optional[str] = Query(None, description="Filter by status"),
    evidence_type: Optional[str] = Query(None, description="Filter by evidence type"),
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """Get paginated list of evidence with filtering."""
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
    """Get specific evidence by ID."""
    evidence = await get_by_id(
        db=db,
        model=Evidence,
        id_field_name="evidence_id",
        id_value=evidence_id,
        error_message_en=f"Evidence {evidence_id} not found",
        error_message_ar=f"لم يتم العثور على الدليل {evidence_id}",
    )
    return evidence


@router.post("/evidence", response_model=EvidenceResponse, status_code=201)
async def create_evidence(
    evidence_data: EvidenceCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    Create new evidence.
    A SHA-256 hash is computed from the evidence metadata at creation time
    to enable tamper detection later.
    """
    # Check if evidence_id already exists
    await check_exists(
        db=db,
        model=Evidence,
        id_field_name="evidence_id",
        id_value=evidence_data.evidence_id,
        error_message_en=f"Evidence {evidence_data.evidence_id} already exists",
        error_message_ar=f"الدليل {evidence_data.evidence_id} موجود بالفعل",
    )

    # Compute server-side timestamps and tamper-protection hash
    collection_date = datetime.utcnow()
    expiry_date = collection_date + timedelta(days=evidence_data.retention_period_days)
    file_hash = _compute_evidence_hash(evidence_data)

    evidence = Evidence(
        **evidence_data.model_dump(),
        collection_date=collection_date,
        expiry_date=expiry_date,
        file_hash=file_hash,
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
    """Update evidence (partial update)."""
    evidence = await get_by_id(
        db=db,
        model=Evidence,
        id_field_name="evidence_id",
        id_value=evidence_id,
        error_message_en=f"Evidence {evidence_id} not found",
        error_message_ar=f"لم يتم العثور على الدليل {evidence_id}",
    )

    evidence = await update_model(item=evidence, update_data=evidence_data, db=db)
    return evidence


@router.post("/evidence/{evidence_id}/validate", response_model=EvidenceResponse)
async def validate_evidence(
    evidence_id: str,
    validation: EvidenceValidationRequest,
    db: AsyncSession = Depends(get_db),
):
    """Validate or reject evidence."""
    evidence = await get_by_id(
        db=db,
        model=Evidence,
        id_field_name="evidence_id",
        id_value=evidence_id,
        error_message_en=f"Evidence {evidence_id} not found",
        error_message_ar=f"لم يتم العثور على الدليل {evidence_id}",
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


@router.get("/evidence/{evidence_id}/integrity", response_model=EvidenceIntegrityResponse)
async def verify_evidence_integrity(
    evidence_id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Verify the integrity of an evidence record by recomputing its hash
    and comparing it to the stored value.
    Returns whether the evidence has been tampered with since collection.
    """
    evidence = await get_by_id(
        db=db,
        model=Evidence,
        id_field_name="evidence_id",
        id_value=evidence_id,
        error_message_en=f"Evidence {evidence_id} not found",
        error_message_ar=f"لم يتم العثور على الدليل {evidence_id}",
    )

    if not evidence.file_hash:
        return EvidenceIntegrityResponse(
            evidence_id=evidence_id,
            has_hash=False,
            integrity_ok=False,
            message_en="No integrity hash found for this evidence record.",
            message_ar="لم يتم العثور على بصمة تكاملية لهذا السجل.",
        )

    # Recompute hash from stored metadata
    from evidence.schemas import EvidenceCreate
    recomputed = hashlib.sha256(
        (
            f"{evidence.evidence_id}|{evidence.control_id}|"
            f"{evidence.title_en}|{evidence.title_ar}|"
            f"{evidence.file_name or ''}|{evidence.file_size or 0}"
        ).encode("utf-8")
    ).hexdigest()

    integrity_ok = recomputed == evidence.file_hash
    if integrity_ok:
        msg_en = "Evidence integrity verified successfully."
        msg_ar = "تم التحقق من تكامل الدليل بنجاح."
    else:
        msg_en = "Evidence integrity check FAILED: record may have been tampered with."
        msg_ar = "فشل التحقق من تكامل الدليل: ربما تم التلاعب بالسجل."
    return EvidenceIntegrityResponse(
        evidence_id=evidence_id,
        has_hash=True,
        integrity_ok=integrity_ok,
        message_en=msg_en,
        message_ar=msg_ar,
    )


@router.delete("/evidence/{evidence_id}", status_code=204)
async def delete_evidence(
    evidence_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Delete evidence."""
    await delete_by_id(
        db=db,
        model=Evidence,
        id_field_name="evidence_id",
        id_value=evidence_id,
        error_message_en=f"Evidence {evidence_id} not found",
        error_message_ar=f"لم يتم العثور على الدليل {evidence_id}",
    )


@router.get("/evidence/control/{control_id}/summary")
async def get_control_evidence_summary(
    control_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get evidence summary for a control."""
    # Get total count efficiently
    total_query = select(func.count()).select_from(Evidence).where(Evidence.control_id == control_id)
    total_result = await db.execute(total_query)
    total = total_result.scalar() or 0

    # Get status breakdown with single query
    status_query = select(
        Evidence.status,
        func.count(Evidence.id)
    ).where(Evidence.control_id == control_id).group_by(Evidence.status)
    status_result = await db.execute(status_query)

    by_status = {}
    for status, count in status_result:
        key = status if isinstance(status, str) else status.value
        by_status[key] = count

    # Get type breakdown with single query
    type_query = select(
        Evidence.evidence_type,
        func.count(Evidence.id)
    ).where(Evidence.control_id == control_id).group_by(Evidence.evidence_type)
    type_result = await db.execute(type_query)

    by_type = {}
    for etype, count in type_result:
        key = etype if isinstance(etype, str) else etype.value
        by_type[key] = count

    return {
        "control_id": control_id,
        "total_evidence": total,
        "by_status": by_status,
        "by_type": by_type,
        "compliance_rate": (by_status.get("validated", 0) / total * 100) if total > 0 else 0,
    }
