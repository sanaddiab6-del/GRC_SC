"""
Web UI router – handles browser-facing routes that delegate to the
React frontend.

The backend API lives at /api/v1/...
All human-facing pages are rendered by the Next.js frontend.
This router simply redirects browser requests for known UI paths
to the correct React URL so that the root "/" -> "/auth/login"
redirect in main.py works end-to-end.
"""
import os
import logging

from fastapi import APIRouter
from fastapi.responses import RedirectResponse

logger = logging.getLogger(__name__)

# Build the frontend origin once at module load time.
# Override FRONTEND_URL in your .env file for non-default setups.
_FRONTEND_URL: str = os.environ.get("FRONTEND_URL", "http://localhost:3000").rstrip("/")

router = APIRouter(tags=["Web UI"])


@router.get("/auth/login", include_in_schema=False)
async def redirect_to_login():
    """Redirect browser to the React login page."""
    return RedirectResponse(url=f"{_FRONTEND_URL}/en/login", status_code=302)


@router.get("/auth/register", include_in_schema=False)
async def redirect_to_register():
    """Redirect browser to the React registration page."""
    return RedirectResponse(url=f"{_FRONTEND_URL}/en/register", status_code=302)


@router.get("/dashboard", include_in_schema=False)
async def redirect_to_dashboard():
    """Redirect browser to the React dashboard."""
    return RedirectResponse(url=f"{_FRONTEND_URL}/en/dashboard", status_code=302)
