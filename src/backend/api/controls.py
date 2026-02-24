"""Controls API module for API v1 routing."""

from fastapi import APIRouter

from controls.router import router as controls_router

router = APIRouter()
router.include_router(controls_router, tags=["controls"])

__all__ = ["router"]
