"""
Controls API Router
RESTful endpoints for control management with bilingual support
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional

from src.backend.core.database import get_db
from src.backend.controls.models import Control, FrameworkType
from src.backend.controls.schemas import (
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
    limit: int = Query(50, ge=1, le=100),
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
    
    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_query)
    
    # Apply pagination
    query = query.offset(offset).limit(limit)
    result = await db.execute(query)
    items = result.scalars().all()
    
    return ControlListResponse(
        total=total or 0,
        offset=offset,
        limit=limit,
        items=items,
    )


@router.get("/controls/{control_id}", response_model=ControlResponse)
async def get_control(
    control_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get a specific control by ID (e.g., ECC-GV-1)"""
    query = select(Control).where(Control.control_id == control_id)
    result = await db.execute(query)
    control = result.scalar_one_or_none()
    
    if not control:
        raise HTTPException(
            status_code=404,
            detail={
                "message_en": f"Control {control_id} not found",
                "message_ar": f"لم يتم العثور على الضابط {control_id}",
            },
        )
    
    return control


@router.post("/controls", response_model=ControlResponse, status_code=201)
async def create_control(
    control_data: ControlCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new control"""
    # Check if control_id already exists
    existing = await db.execute(
        select(Control).where(Control.control_id == control_data.control_id)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=400,
            detail={
                "message_en": f"Control {control_data.control_id} already exists",
                "message_ar": f"الضابط {control_data.control_id} موجود بالفعل",
            },
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
    """Update an existing control (partial update)"""
    query = select(Control).where(Control.control_id == control_id)
    result = await db.execute(query)
    control = result.scalar_one_or_none()
    
    if not control:
        raise HTTPException(
            status_code=404,
            detail={
                "message_en": f"Control {control_id} not found",
                "message_ar": f"لم يتم العثور على الضابط {control_id}",
            },
        )
    
    # Update only provided fields
    update_data = control_data.model_dump(exclude_unset=True)
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
    """Delete a control"""
    query = select(Control).where(Control.control_id == control_id)
    result = await db.execute(query)
    control = result.scalar_one_or_none()
    
    if not control:
        raise HTTPException(
            status_code=404,
            detail={
                "message_en": f"Control {control_id} not found",
                "message_ar": f"لم يتم العثور على الضابط {control_id}",
            },
        )
    
    await db.delete(control)
    await db.commit()
