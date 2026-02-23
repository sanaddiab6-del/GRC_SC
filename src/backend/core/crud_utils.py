"""
CRUD Utility Functions
Common database operations to reduce code duplication across routers
"""

from typing import TypeVar, Generic, Type, Optional, Dict, Any, List
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import DeclarativeMeta
from pydantic import BaseModel

ModelType = TypeVar("ModelType", bound=DeclarativeMeta)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


async def get_by_id(
    db: AsyncSession,
    model: Type[ModelType],
    id_field_name: str,
    id_value: Any,
    error_message_en: str,
    error_message_ar: str,
) -> ModelType:
    """
    Generic get by ID with bilingual error handling
    
    Args:
        db: Database session
        model: SQLAlchemy model class
        id_field_name: Name of the ID field (e.g., "control_id", "evidence_id")
        id_value: Value to search for
        error_message_en: English error message if not found
        error_message_ar: Arabic error message if not found
    
    Returns:
        Model instance
        
    Raises:
        HTTPException: 404 if not found
    """
    id_field = getattr(model, id_field_name)
    query = select(model).where(id_field == id_value)
    result = await db.execute(query)
    item = result.scalar_one_or_none()
    
    if not item:
        raise HTTPException(
            status_code=404,
            detail={
                "message_en": error_message_en,
                "message_ar": error_message_ar,
            },
        )
    
    return item


async def check_exists(
    db: AsyncSession,
    model: Type[ModelType],
    id_field_name: str,
    id_value: Any,
    error_message_en: str,
    error_message_ar: str,
) -> None:
    """
    Check if an item already exists and raise error if it does
    
    Args:
        db: Database session
        model: SQLAlchemy model class
        id_field_name: Name of the ID field
        id_value: Value to check
        error_message_en: English error message if exists
        error_message_ar: Arabic error message if exists
        
    Raises:
        HTTPException: 400 if item already exists
    """
    id_field = getattr(model, id_field_name)
    query = select(model).where(id_field == id_value)
    result = await db.execute(query)
    existing = result.scalar_one_or_none()
    
    if existing:
        raise HTTPException(
            status_code=400,
            detail={
                "message_en": error_message_en,
                "message_ar": error_message_ar,
            },
        )


async def update_model(
    item: ModelType,
    update_data: UpdateSchemaType,
    db: AsyncSession,
) -> ModelType:
    """
    Generic update function for partial updates
    
    Args:
        item: Model instance to update
        update_data: Pydantic update schema
        db: Database session
        
    Returns:
        Updated model instance
    """
    # Update only provided fields
    update_dict = update_data.model_dump(exclude_unset=True)
    for field, value in update_dict.items():
        setattr(item, field, value)
    
    await db.commit()
    await db.refresh(item)
    
    return item


async def delete_by_id(
    db: AsyncSession,
    model: Type[ModelType],
    id_field_name: str,
    id_value: Any,
    error_message_en: str,
    error_message_ar: str,
) -> None:
    """
    Generic delete by ID with bilingual error handling
    
    Args:
        db: Database session
        model: SQLAlchemy model class
        id_field_name: Name of the ID field
        id_value: Value to delete
        error_message_en: English error message if not found
        error_message_ar: Arabic error message if not found
        
    Raises:
        HTTPException: 404 if not found
    """
    item = await get_by_id(
        db=db,
        model=model,
        id_field_name=id_field_name,
        id_value=id_value,
        error_message_en=error_message_en,
        error_message_ar=error_message_ar,
    )
    
    await db.delete(item)
    await db.commit()


def create_bilingual_error(
    resource_name_en: str,
    resource_name_ar: str,
    resource_id: str,
    error_type: str = "not_found"
) -> Dict[str, str]:
    """
    Create standardized bilingual error messages
    
    Args:
        resource_name_en: Resource name in English (e.g., "Control", "Evidence")
        resource_name_ar: Resource name in Arabic (e.g., "الضابط", "الدليل")
        resource_id: ID of the resource
        error_type: Type of error ("not_found", "already_exists")
        
    Returns:
        Dictionary with message_en and message_ar
    """
    if error_type == "not_found":
        return {
            "message_en": f"{resource_name_en} {resource_id} not found",
            "message_ar": f"لم يتم العثور على {resource_name_ar} {resource_id}",
        }
    elif error_type == "already_exists":
        return {
            "message_en": f"{resource_name_en} {resource_id} already exists",
            "message_ar": f"{resource_name_ar} {resource_id} موجود بالفعل",
        }
    else:
        return {
            "message_en": f"Error with {resource_name_en} {resource_id}",
            "message_ar": f"خطأ في {resource_name_ar} {resource_id}",
        }
