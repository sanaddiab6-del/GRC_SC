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
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession

# Ensure the backend directory is on sys.path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from core.config import settings
from core.database import init_db, get_db, AsyncSessionLocal
from core.security_middleware import setup_security_middleware
from controls import router as controls_router
from evidence import router as evidence_router
from reporting import router as reporting_router
from auth.router import router as auth_router
from auth.rbac_setup import initialize_rbac
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

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to known origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security middleware (rate limiting, headers, etc.)
setup_security_middleware(app)
logger.info("✓ Security middleware configured")


# ============================================================================
# Health check endpoints (public, no auth required)
# ============================================================================

@app.get("/", tags=["Health"])
async def root():
    """Root endpoint - API health check."""
    return JSONResponse(
        content={
            "status": "healthy",
            "service": "SICO GRC Platform API",
            "version": "2.4.0",
            "message_en": "Saudi Regulatory Compliance Engine - Operational",
            "message_ar": "محرك الامتثال التنظيمي السعودي - يعمل",
        }
    )


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
# Register all routers with versioned prefix
# ============================================================================

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
