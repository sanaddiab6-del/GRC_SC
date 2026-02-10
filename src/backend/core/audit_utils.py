"""
Audit Logging Utilities
Common audit logging patterns to reduce code duplication
"""

from typing import Optional, Dict, Any
from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession
from auth.security import log_audit_event


async def log_create_event(
    db: AsyncSession,
    user_id: str,
    resource: str,
    resource_id: str,
    request: Optional[Request] = None,
    details: Optional[Dict[str, Any]] = None,
) -> None:
    """
    Log a create event
    
    Args:
        db: Database session
        user_id: ID of user performing the action
        resource: Resource type (e.g., "control", "evidence")
        resource_id: ID of created resource
        request: FastAPI request object (optional)
        details: Additional details to log (optional)
    """
    await log_audit_event(
        db=db,
        user_id=user_id,
        action=f"{resource}.created",
        resource=resource,
        resource_id=resource_id,
        status="success",
        ip_address=request.client.host if request and request.client else None,
        user_agent=request.headers.get("user-agent") if request else None,
        details=details,
    )


async def log_update_event(
    db: AsyncSession,
    user_id: str,
    resource: str,
    resource_id: str,
    request: Optional[Request] = None,
    details: Optional[Dict[str, Any]] = None,
) -> None:
    """
    Log an update event
    
    Args:
        db: Database session
        user_id: ID of user performing the action
        resource: Resource type
        resource_id: ID of updated resource
        request: FastAPI request object (optional)
        details: Additional details to log (optional)
    """
    await log_audit_event(
        db=db,
        user_id=user_id,
        action=f"{resource}.updated",
        resource=resource,
        resource_id=resource_id,
        status="success",
        ip_address=request.client.host if request and request.client else None,
        user_agent=request.headers.get("user-agent") if request else None,
        details=details,
    )


async def log_delete_event(
    db: AsyncSession,
    user_id: str,
    resource: str,
    resource_id: str,
    request: Optional[Request] = None,
) -> None:
    """
    Log a delete event
    
    Args:
        db: Database session
        user_id: ID of user performing the action
        resource: Resource type
        resource_id: ID of deleted resource
        request: FastAPI request object (optional)
    """
    await log_audit_event(
        db=db,
        user_id=user_id,
        action=f"{resource}.deleted",
        resource=resource,
        resource_id=resource_id,
        status="success",
        ip_address=request.client.host if request and request.client else None,
        user_agent=request.headers.get("user-agent") if request else None,
    )


def extract_request_metadata(request: Optional[Request]) -> Dict[str, Optional[str]]:
    """
    Extract common metadata from request
    
    Args:
        request: FastAPI request object
        
    Returns:
        Dictionary with ip_address and user_agent
    """
    if not request:
        return {"ip_address": None, "user_agent": None}
    
    return {
        "ip_address": request.client.host if request.client else None,
        "user_agent": request.headers.get("user-agent"),
    }
