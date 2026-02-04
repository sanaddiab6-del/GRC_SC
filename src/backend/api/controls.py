"""
Controls API Module
Provides REST endpoints for control management
Wraps the controls router for API v1
"""

from fastapi import APIRouter
from src.backend.controls.router import router as controls_router

router = APIRouter()

# Include all control endpoints
router.include_router(controls_router, tags=["controls"])

__all__ = ["router"]
