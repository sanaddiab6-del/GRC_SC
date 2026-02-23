"""
ISMS Router - ISO 27001 Policy Management & Asset Inventory (Phase 2.4).
Implements ISMS policy lifecycle, document control, and asset register.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional
from datetime import datetime

from core.database import get_db
from auth.security import get_current_user, require_permission, require_role, log_audit_event
from auth.models import User
from isms.models import ISMSPolicy, AssetInventory, PolicyStatus, PolicyType, DocumentClassification
from isms.schemas import (
    ISMSPolicyCreate, ISMSPolicyUpdate, ISMSPolicyResponse,
    AssetCreate, AssetUpdate, AssetResponse,
)

router = APIRouter()


# ===== ISMS POLICY ENDPOINTS =====

@router.post("/isms/policies", response_model=ISMSPolicyResponse, status_code=201,
             dependencies=[Depends(require_role("Admin"))])
async def create_policy(
    policy_data: ISMSPolicyCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Create ISMS security policy (ISO 27001 A.5.1).
    Admin only.
    """
    # Generate policy number
    year = datetime.utcnow().year
    count_result = await db.execute(
        select(func.count(ISMSPolicy.policy_id))
    )
    count = (count_result.scalar() or 0) + 1
    policy_type_code = policy_data.policy_type.value.upper()[:3]
    policy_number = f"POL-{policy_type_code}-{count:04d}"

    policy = ISMSPolicy(
        policy_number=policy_number,
        author_id=current_user.user_id,
        **policy_data.model_dump(),
    )

    if policy_data.effective_date:
        from datetime import timedelta
        setattr(policy, "next_review_date",
                policy_data.effective_date + timedelta(days=policy_data.review_frequency_days))

    db.add(policy)
    await db.commit()
    await db.refresh(policy)

    await log_audit_event(
        db=db,
        user_id=str(current_user.user_id),
        action="isms_policy.created",
        resource="isms_policy",
        resource_id=str(policy.policy_id),
        status="success",
        ip_address=None,
        user_agent=None,
        details={"policy_number": policy_number, "policy_type": policy_data.policy_type.value},
    )

    return policy


@router.get("/isms/policies", response_model=List[ISMSPolicyResponse])
async def list_policies(
    policy_type: Optional[PolicyType] = None,
    status: Optional[PolicyStatus] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List ISMS policies with optional filters."""
    query = select(ISMSPolicy)

    filters = []
    if policy_type:
        filters.append(ISMSPolicy.policy_type == policy_type)
    if status:
        filters.append(ISMSPolicy.status == status)

    from sqlalchemy import and_
    if filters:
        query = query.where(and_(*filters))

    query = query.order_by(ISMSPolicy.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/isms/policies/{policy_id}", response_model=ISMSPolicyResponse)
async def get_policy(
    policy_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get ISMS policy details."""
    result = await db.execute(select(ISMSPolicy).where(ISMSPolicy.policy_id == policy_id))
    policy = result.scalar_one_or_none()
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")
    return policy


@router.patch("/isms/policies/{policy_id}", response_model=ISMSPolicyResponse,
              dependencies=[Depends(require_role("Admin"))])
async def update_policy(
    policy_id: int,
    update_data: ISMSPolicyUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update ISMS policy (Admin only)."""
    result = await db.execute(select(ISMSPolicy).where(ISMSPolicy.policy_id == policy_id))
    policy = result.scalar_one_or_none()
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")

    for field, value in update_data.model_dump(exclude_unset=True).items():
        setattr(policy, field, value)

    # Set timestamps based on status transitions
    new_status = update_data.status
    if new_status == PolicyStatus.APPROVED and not getattr(policy, "approval_date"):
        setattr(policy, "approval_date", datetime.utcnow())
        setattr(policy, "approver_id", current_user.user_id)
    elif new_status == PolicyStatus.PUBLISHED and not getattr(policy, "publication_date"):
        setattr(policy, "publication_date", datetime.utcnow())

    await db.commit()
    await db.refresh(policy)

    await log_audit_event(
        db=db,
        user_id=str(current_user.user_id),
        action="isms_policy.updated",
        resource="isms_policy",
        resource_id=str(policy_id),
        status="success",
        ip_address=None,
        user_agent=None,
        details={"updated_fields": list(update_data.model_dump(exclude_unset=True).keys())},
    )

    return policy


@router.get("/isms/statistics")
async def isms_statistics(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """ISMS compliance statistics."""
    total_result = await db.execute(select(func.count(ISMSPolicy.policy_id)))
    total = total_result.scalar() or 0

    approved_result = await db.execute(
        select(func.count(ISMSPolicy.policy_id)).where(
            ISMSPolicy.status == PolicyStatus.PUBLISHED
        )
    )
    published = approved_result.scalar() or 0

    assets_result = await db.execute(select(func.count(AssetInventory.asset_id)))
    total_assets = assets_result.scalar() or 0

    return {
        "total_policies": total,
        "published_policies": published,
        "total_assets": total_assets,
        "coverage_rate": f"{(published / total * 100):.1f}%" if total > 0 else "0%",
        "message_en": "ISMS statistics",
        "message_ar": "إحصائيات نظام إدارة أمن المعلومات",
    }


# ===== ASSET INVENTORY ENDPOINTS =====

@router.post("/isms/assets", response_model=AssetResponse, status_code=201)
async def create_asset(
    asset_data: AssetCreate,
    current_user: User = Depends(require_permission("controls", "create")),
    db: AsyncSession = Depends(get_db),
):
    """Register information asset (ISO 27001 A.5.9 - Asset inventory)."""
    count_result = await db.execute(select(func.count(AssetInventory.asset_id)))
    count = (count_result.scalar() or 0) + 1
    asset_type_code = asset_data.asset_type.upper()[:3]
    asset_number = f"ASSET-{asset_type_code}-{count:04d}"

    asset = AssetInventory(
        asset_number=asset_number,
        owner_id=current_user.user_id,
        **asset_data.model_dump(),
    )

    db.add(asset)
    await db.commit()
    await db.refresh(asset)

    return asset


@router.get("/isms/assets", response_model=List[AssetResponse])
async def list_assets(
    asset_type: Optional[str] = None,
    classification: Optional[DocumentClassification] = None,
    processes_personal_data: Optional[bool] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List information assets."""
    from sqlalchemy import and_
    query = select(AssetInventory)
    filters = []
    if asset_type:
        filters.append(AssetInventory.asset_type == asset_type)
    if classification:
        filters.append(AssetInventory.classification == classification)
    if processes_personal_data is not None:
        filters.append(AssetInventory.processes_personal_data == processes_personal_data)
    if filters:
        query = query.where(and_(*filters))

    query = query.order_by(AssetInventory.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/isms/assets/{asset_id}", response_model=AssetResponse)
async def get_asset(
    asset_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get asset details."""
    result = await db.execute(select(AssetInventory).where(AssetInventory.asset_id == asset_id))
    asset = result.scalar_one_or_none()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    return asset


@router.patch("/isms/assets/{asset_id}", response_model=AssetResponse)
async def update_asset(
    asset_id: int,
    update_data: AssetUpdate,
    current_user: User = Depends(require_permission("controls", "update")),
    db: AsyncSession = Depends(get_db),
):
    """Update asset information."""
    result = await db.execute(select(AssetInventory).where(AssetInventory.asset_id == asset_id))
    asset = result.scalar_one_or_none()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    for field, value in update_data.model_dump(exclude_unset=True).items():
        setattr(asset, field, value)

    setattr(asset, "last_review_date", datetime.utcnow())
    await db.commit()
    await db.refresh(asset)
    return asset
