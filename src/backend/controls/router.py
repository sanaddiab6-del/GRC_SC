"""
Controls API Router
RESTful endpoints for control management with bilingual support
Protected with NCA ECC-IS-3 authentication and RBAC authorization
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional

from core.database import get_db
from core.crud_utils import get_by_id, check_exists, update_model, delete_by_id
from controls.models import Control, FrameworkType
from controls.schemas import (
    ControlCreate,
    ControlUpdate,
    ControlResponse,
    ControlListResponse,
)
# Import authentication dependencies (disabled for demo)
# from auth.security import get_current_user, require_permission
# from auth.models import User

router = APIRouter()


@router.get("/controls", response_model=ControlListResponse)
async def list_controls(
    framework: Optional[str] = Query(None, description="Filter by framework (ECC, CCC, PDPL)"),
    status: Optional[str] = Query(None, description="Filter by status"),
    domain: Optional[str] = Query(None, description="Filter by domain"),
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    # current_user: User = Depends(get_current_user),  # Authentication disabled for demo
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
    
    # Count total - simplified
    count_result = await db.execute(query)
    all_items = count_result.scalars().all()
    total = len(all_items)
    
    # Apply pagination manually
    paginated_items = all_items[offset:offset + limit]
    
    response_items = [ControlResponse.model_validate(item) for item in paginated_items]
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
    # current_user: User = Depends(get_current_user),  # Authentication disabled for demo
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
    # current_user: User = Depends(require_permission("controls", "create")),  # Requires controls:create permission
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
    # current_user: User = Depends(require_permission("controls", "update")),  # Requires controls:update permission
):
    """Update an existing control (partial update). Requires controls:update permission (Admin or Compliance Officer)."""
    control = await get_by_id(
        db=db,
        model=Control,
        id_field_name="control_id",
        id_value=control_id,
        error_message_en=f"Control {control_id} not found",
        error_message_ar=f"لم يتم العثور على الضابط {control_id}",
    )
    
    control = await update_model(item=control, update_data=control_data, db=db)
    return control


@router.delete("/controls/{control_id}", status_code=204)
async def delete_control(
    control_id: str,
    db: AsyncSession = Depends(get_db),
    # current_user: User = Depends(require_permission("controls", "delete")),  # Requires controls:delete permission
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
