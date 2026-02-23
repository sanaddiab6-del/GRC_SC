"""
Controls API Router
RESTful endpoints for control management with bilingual support
Protected with NCA ECC-IS-3 authentication and RBAC authorization
"""

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from core.database import get_db
from core.crud_utils import get_by_id, check_exists, update_model, delete_by_id
from controls.models import Control, FrameworkType, ControlStatus, LIFECYCLE_TRANSITIONS
from controls.schemas import (
    ControlCreate,
    ControlUpdate,
    ControlResponse,
    ControlListResponse,
)

router = APIRouter()


@router.get("/controls", response_model=ControlListResponse)
async def list_controls(
    framework: Optional[str] = Query(None, description="Filter by framework (ECC, CCC, PDPL)"),
    status: Optional[str] = Query(None, description="Filter by status"),
    domain: Optional[str] = Query(None, description="Filter by domain"),
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
):
    """
    Get paginated list of controls with filtering
    Supports bilingual results
    """
    query = select(Control)

    # Apply filters
    if framework:
        query = query.where(Control.framework == framework)
    if status:
        query = query.where(Control.status == status)
    if domain:
        query = query.where(Control.domain == domain)

    # Get total count efficiently
    count_query = select(func.count()).select_from(Control)
    if framework:
        count_query = count_query.where(Control.framework == framework)
    if status:
        count_query = count_query.where(Control.status == status)
    if domain:
        count_query = count_query.where(Control.domain == domain)

    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # Apply pagination in database
    query = query.offset(offset).limit(limit)
    result = await db.execute(query)
    items = result.scalars().all()

    response_items = [ControlResponse.model_validate(item) for item in items]
    return ControlListResponse(
        total=total,
        offset=offset,
        limit=limit,
        items=response_items,
    )


@router.get("/controls/{control_id}", response_model=ControlResponse)
async def get_control(
    control_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get a specific control by ID (e.g., ECC-GV-1)."""
    control = await get_by_id(
        db=db,
        model=Control,
        id_field_name="control_id",
        id_value=control_id,
        error_message_en=f"Control {control_id} not found",
        error_message_ar=f"لم يتم العثور على الضابط {control_id}",
    )
    return control


@router.post("/controls", response_model=ControlResponse, status_code=201)
async def create_control(
    control_data: ControlCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new control. Requires controls:create permission (Admin or Compliance Officer)."""
    # Check if control_id already exists
    await check_exists(
        db=db,
        model=Control,
        id_field_name="control_id",
        id_value=control_data.control_id,
        error_message_en=f"Control {control_data.control_id} already exists",
        error_message_ar=f"الضابط {control_data.control_id} موجود بالفعل",
    )

    control = Control(**control_data.model_dump())
    db.add(control)
    await db.commit()
    await db.refresh(control)

    return control


@router.patch("/controls/{control_id}", response_model=ControlResponse)
async def update_control(
    control_id: str,
    control_data: ControlUpdate,
    db: AsyncSession = Depends(get_db),
):
    """
    Update an existing control (partial update).
    Enforces lifecycle transition rules when status is changed.
    """
    control = await get_by_id(
        db=db,
        model=Control,
        id_field_name="control_id",
        id_value=control_id,
        error_message_en=f"Control {control_id} not found",
        error_message_ar=f"لم يتم العثور على الضابط {control_id}",
    )

    # Enforce lifecycle transition rules
    if control_data.status is not None:
        new_status = ControlStatus(control_data.status)
        current_status = ControlStatus(
            control.status if isinstance(control.status, str) else control.status.value
        )
        allowed = LIFECYCLE_TRANSITIONS.get(current_status, set())
        if new_status not in allowed:
            raise HTTPException(
                status_code=422,
                detail={
                    "message_en": (
                        f"Invalid lifecycle transition: cannot move from "
                        f"'{current_status.value}' to '{new_status.value}'. "
                        f"Allowed transitions: {[s.value for s in allowed]}"
                    ),
                    "message_ar": (
                        f"انتقال دورة حياة غير صالح: لا يمكن الانتقال من "
                        f"'{current_status.value}' إلى '{new_status.value}'"
                    ),
                },
            )
        # Stamp the lifecycle change timestamp
        setattr(control, "lifecycle_updated_at", datetime.utcnow())

    control = await update_model(item=control, update_data=control_data, db=db)
    
    # Update only provided fields
    update_data = control_data.model_dump(exclude_unset=True)

    # Enforce strict lifecycle transitions for status/state
    if "status" in update_data:
        from core.lifecycle_transitions import CONTROL_TRANSITIONS
        current_status = getattr(control, "status")
        new_status = update_data["status"]
        allowed = CONTROL_TRANSITIONS.get(current_status, [])
        if new_status != current_status and new_status not in allowed:
            # Tooltip explanation
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
        setattr(control, field, value)

    await db.commit()
    await db.refresh(control)

    return control


@router.delete("/controls/{control_id}", status_code=204)
async def delete_control(
    control_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Delete a control. Requires controls:delete permission (Admin or Compliance Officer only)."""
    await delete_by_id(
        db=db,
        model=Control,
        id_field_name="control_id",
        id_value=control_id,
        error_message_en=f"Control {control_id} not found",
        error_message_ar=f"لم يتم العثور على الضابط {control_id}",
    )
