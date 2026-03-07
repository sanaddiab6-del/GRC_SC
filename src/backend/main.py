"""
SICO GRC Platform - Main FastAPI Application
Backend API for Saudi Regulatory Compliance (ECC, CCC, PDPL)
Enhanced with NCA ECC-IS-3 and PDPL Article 29 security controls
"""

import sys
import os
import logging
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List

# Ensure the backend directory is on sys.path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from core.config import settings
from core.database import init_db, validate_db_startup, get_db, AsyncSessionLocal
from core.security_middleware import setup_security_middleware
from controls import router as controls_router
from evidence import router as evidence_router
from reporting import router as reporting_router
from auth.router import router as auth_router
from auth.web_router import router as web_router
from auth.seeder import seed_admin_user
from auth.rbac_setup import initialize_rbac
from auth.security import get_current_active_user
from auth.models import User
import ai_router
from privacy import router as privacy_router
from incident import router as incident_router
from risk import router as risk_router
from ai_governance import router as ai_governance_router
from monitoring import router as monitoring_router
from backup import router as backup_router
import enterprise_router
from isms import router as isms_router
from audit import router as audit_router
from assessment.router import router as assessment_router
from dynamic_config.router import router as config_router

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize services on startup with graceful degradation."""
    logger.info("Starting SICO GRC Platform...")

    # Initialize database with error handling
    try:
        await init_db()
        logger.info("✓ Database initialized")

        # Validate connectivity and migration state; never raises.
        await validate_db_startup()

        try:
            from startup_init_data import check_and_initialize_data
            check_and_initialize_data()
        except Exception as e:
            logger.warning(f"⚠️ Data initialization warning: {str(e)}")

        try:
            async with AsyncSessionLocal() as db:
                await initialize_rbac(db)
            logger.info("✓ RBAC system initialized")
        except Exception as e:
            logger.warning(f"⚠️ RBAC initialization failed: {str(e)}")

        try:
            async with AsyncSessionLocal() as db:
                await seed_admin_user(db)
            logger.info("✓ Admin user seeder complete")
        except Exception as e:
            logger.warning(f"⚠️ Admin seeder warning: {str(e)}")
    except Exception as e:
        logger.error(f"⚠️ Database connection failed: {str(e)}")
        logger.warning("   Server running in API-only mode (no database)")

    # Start privacy automation background tasks
    try:
        from privacy.background_tasks import privacy_scheduler
        privacy_scheduler.start()
        logger.info("✓ Privacy automation started")
    except Exception as e:
        logger.warning(f"⚠️ Privacy automation failed: {str(e)}")

    # Start Phase 2.3 automation
    try:
        from phase23_background_tasks import phase23_scheduler
        phase23_scheduler.start()
        logger.info("✓ AI Governance & SIEM automation started")
    except Exception as e:
        logger.warning(f"⚠️ Phase 2.3 automation failed: {str(e)}")

    # Start backup automation
    try:
        from backup.background_tasks import backup_scheduler, initialize_backup_automation
        if not backup_scheduler.running:
            backup_scheduler.start()
            initialize_backup_automation()
        logger.info("✓ Backup automation started")
    except Exception as e:
        logger.warning(f"⚠️ Backup automation failed: {str(e)}")

    logger.info("✓ SICO GRC Platform started")
    yield

    # Cleanup on shutdown
    logger.info("Shutting down SICO GRC Platform...")

    for scheduler_path, name in [
        ("privacy.background_tasks.privacy_scheduler", "Privacy automation"),
        ("phase23_background_tasks.phase23_scheduler", "Phase 2.3 automation"),
        ("backup.background_tasks.backup_scheduler", "Backup automation"),
    ]:
        try:
            module_path, attr = scheduler_path.rsplit(".", 1)
            import importlib
            mod = importlib.import_module(module_path)
            scheduler = getattr(mod, attr)
            scheduler.shutdown()
            logger.info(f"✓ {name} stopped")
        except Exception as e:
            logger.warning(f"⚠️ {name} shutdown warning: {str(e)}")


app = FastAPI(
    title="SICO GRC Platform API",
    description="Bilingual Saudi Regulatory Compliance Engine (ECC, CCC, PDPL, SDAIA AI) with NCA Security Controls",
    version="2.4.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS must be registered immediately after app creation (before any custom middleware)
raw_origins = settings.CORS_ORIGINS
if isinstance(raw_origins, str):
    cors_origins = [o.strip() for o in raw_origins.split(",") if o.strip()]
else:
    cors_origins = [str(o).strip() for o in raw_origins if str(o).strip()]

for dev_origin in [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]:
    if dev_origin not in cors_origins:
        cors_origins.append(dev_origin)
# Security middleware (rate limiting, headers, etc.)
setup_security_middleware(app)
logger.info("✓ Security middleware configured")

# Local dev CORS: explicit origins required when credentials are enabled.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Process-Time"],
)

# Security middleware (rate limiting, headers, etc.)

# ============================================================================
# Health check endpoints (public, no auth required)
# ============================================================================

@app.get("/", tags=["Health"], include_in_schema=False)
async def root():
    """Root path redirects to the web login page."""
    return RedirectResponse(url="/auth/login", status_code=302)


@app.get("/health", tags=["Health"])
async def health_check_simple():
    """Simple health check endpoint."""
    return JSONResponse(content={"status": "healthy"})


@app.get("/api/v1/health", tags=["Health"])
async def health_check():
    """Detailed health check with bilingual response (public endpoint)."""
    return JSONResponse(
        content={
            "status": "healthy",
            "frameworks": ["ECC", "CCC", "PDPL", "SDAIA AI"],
            "features": {
                "bilingual": True,
                "ai_rag": True,
                "soc_integration": True,
                "authentication": True,
                "authorization": True,
                "encryption": True,
                "audit_logging": True,
                "rate_limiting": True,
                "privacy_management": True,
                "incident_response": True,
                "risk_management": True,
                "ai_governance": True,
                "backup_disaster_recovery": True,
                "security_monitoring": True,
                "control_lifecycle": True,
                "evidence_tamper_protection": True,
                "regulatory_version_register": True,
                "commercial_packs": True,
                "assessment_execution": True,
            },
            "message_en": "All systems operational - Phase 2.4 complete",
            "message_ar": "جميع الأنظمة تعمل - المرحلة 2.4 مكتملة",
        }
    )


@app.get("/api/v1/frameworks", tags=["Frameworks"])
async def list_frameworks():
    """List all supported compliance frameworks."""
    return JSONResponse(
        content={
            "frameworks": [
                {
                    "id": "ecc",
                    "name": "Essential Cybersecurity Controls",
                    "name_ar": "الضوابط الأساسية للأمن السيبراني",
                    "authority": "NCA",
                    "total_controls": 114,
                },
                {
                    "id": "ccc",
                    "name": "Cloud Cybersecurity Controls",
                    "name_ar": "ضوابط الأمن السيبراني السحابي",
                    "authority": "NCA",
                    "total_controls": 180,
                },
                {
                    "id": "pdpl",
                    "name": "Personal Data Protection Law",
                    "name_ar": "نظام حماية البيانات الشخصية",
                    "authority": "SDAIA",
                    "total_controls": 42,
                },
            ]
        }
    )


@app.get("/api/v1/security-status", tags=["Security"])
async def security_status():
    """Security configuration status (public endpoint for transparency)."""
    return JSONResponse(
        content={
            "authentication": {
                "jwt_enabled": True,
                "oauth2_ready": True,
                "token_expiry_minutes": settings.ACCESS_TOKEN_EXPIRE_MINUTES,
            },
            "authorization": {
                "rbac_enabled": True,
                "roles": ["Admin", "Compliance Officer", "Auditor", "Analyst", "Viewer"],
            },
            "encryption": {
                "tls_enabled": settings.TLS_ENABLED,
                "field_level_encryption": True,
                "algorithm": "AES-256",
            },
            "audit_logging": {
                "enabled": True,
                "retention_years": settings.AUDIT_LOG_RETENTION_YEARS,
            },
            "rate_limiting": {
                "enabled": settings.RATE_LIMIT_ENABLED,
                "per_minute": settings.RATE_LIMIT_PER_MINUTE,
                "per_hour": settings.RATE_LIMIT_PER_HOUR,
            },
        }
    )


# ============================================================================
# Common API endpoints (no sub-prefix)
# ============================================================================

@app.get("/api/v1/users", tags=["Users"])
async def list_users_simple(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
    limit: int = 100
):
    """Get list of active users (any authenticated user can call this)."""
    result = await db.execute(
        select(User)
        .where(User.is_active == True)  # noqa: E712
        .options(selectinload(User.roles))
        .limit(limit)
    )
    users = result.scalars().all()
    
    # Return simple user data for dropdowns
    return [
        {
            "user_id": str(user.user_id),
            "name": user.full_name_en or user.email.split('@')[0],  # Fallback to email username
            "email": user.email,
            "role": user.roles[0].role_name if user.roles else "Viewer",  # Get first role name
        }
        for user in users
    ]


@app.get("/api/v1/debug/user-permissions", tags=["Debug"])
async def debug_user_permissions(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Debug endpoint to show current user's roles and permissions."""
    result = await db.execute(
        select(User)
        .where(User.user_id == current_user.user_id)
        .options(selectinload(User.roles).selectinload(Role.permissions))
    )
    user = result.scalar_one_or_none()
    
    roles_data = []
    for role in user.roles:
        permissions = [
            {
                "name": perm.permission_name,
                "resource": perm.resource,
                "action": perm.action
            }
            for perm in role.permissions
        ]
        roles_data.append({
            "role_name": role.role_name,
            "permissions": permissions,
            "permission_count": len(permissions)
        })
    
    return {
        "user_id": str(user.user_id),
        "email": user.email,
        "roles": roles_data,
        "total_roles": len(user.roles)
    }


# ============================================================================
# 
# ============================================================================
# Register all routers with versioned prefix
# ============================================================================

# Web UI routes (no /api/v1 prefix – full-page HTML responses)
app.include_router(web_router)

app.include_router(auth_router, prefix="/api/v1", tags=["Authentication"])
app.include_router(controls_router, prefix="/api/v1", tags=["Controls"])
app.include_router(evidence_router, prefix="/api/v1", tags=["Evidence"])
app.include_router(reporting_router, prefix="/api/v1", tags=["Reporting"])
app.include_router(ai_router.router, prefix="/api/v1", tags=["AI/RAG"])
app.include_router(privacy_router, prefix="/api/v1", tags=["Privacy & PDPL"])
app.include_router(incident_router, prefix="/api/v1", tags=["Incident Response"])
app.include_router(risk_router, prefix="/api/v1", tags=["Risk Management"])
app.include_router(ai_governance_router, prefix="/api/v1", tags=["AI Governance"])
app.include_router(monitoring_router, prefix="/api/v1", tags=["Monitoring & Observability"])
app.include_router(backup_router, prefix="/api/v1", tags=["Backup & Disaster Recovery"])
app.include_router(enterprise_router.router, prefix="/api/v1", tags=["Enterprise GRC"])
app.include_router(isms_router, prefix="/api/v1", tags=["ISMS & ISO 27001"])
app.include_router(audit_router, prefix="/api/v1", tags=["Audit Management"])
app.include_router(assessment_router, prefix="/api/v1", tags=["Assessment Execution"])
app.include_router(config_router, prefix="/api/v1", tags=["Configuration"])

# Regulatory version register and commercial packs are loaded dynamically
try:
    from regulatory_versions import router as reg_versions_router
    app.include_router(reg_versions_router, prefix="/api/v1", tags=["Regulatory Version Register"])
    logger.info("✓ Regulatory version register loaded")
except Exception as e:
    logger.warning(f"⚠️ Regulatory version register not loaded: {str(e)}")

try:
    from packs_router import router as packs_router_obj
    app.include_router(packs_router_obj, prefix="/api/v1", tags=["Commercial Packs"])
    logger.info("✓ Commercial packs router loaded")
except Exception as e:
    logger.warning(f"⚠️ Commercial packs router not loaded: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
