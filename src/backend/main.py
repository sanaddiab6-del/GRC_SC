"""
SICO GRC Platform - Main FastAPI Application
Backend API for Saudi Regulatory Compliance (ECC, CCC, PDPL)
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.backend.core.config import settings
from src.backend.core.database import init_db
from src.backend.controls import router as controls_router
from src.backend.evidence import router as evidence_router
from src.backend.reporting import router as reporting_router
from src.backend import ai_router
from src.backend.api import assessments, controls as api_controls


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize services on startup"""
    await init_db()
    yield
    # Cleanup on shutdown


app = FastAPI(
    title="SICO GRC Platform API",
    description="Bilingual Saudi Regulatory Compliance Engine (ECC, CCC, PDPL)",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoint
@app.get("/", tags=["Health"])
async def root():
    """Root endpoint - API health check"""
    return JSONResponse(
        content={
            "name": "SICO GRC Platform API",
            "version": "0.1.0",
            "status": "operational",
            "frameworks": ["ECC", "CCC", "PDPL"],
            "message_en": "Saudi Regulatory Compliance Engine",
            "message_ar": "محرك الامتثال التنظيمي السعودي"
        }
    )


@app.get("/health", tags=["Health"])
async def health_check_simple():
    """Simple health check endpoint"""
    return JSONResponse(
        content={
            "status": "healthy"
        }
    )


@app.get("/api/v1/health", tags=["Health"])
async def health_check():
    """Detailed health check with bilingual response"""
    return JSONResponse(
        content={
            "status": "healthy",
            "frameworks": ["ECC", "CCC", "PDPL"],
            "features": {
                "bilingual": True,
                "ai_rag": True,
                "soc_integration": True
            },
            "message_en": "All systems operational",
            "message_ar": "جميع الأنظمة تعمل"
        }
    )


@app.get("/api/v1/frameworks", tags=["Frameworks"])
async def list_frameworks():
    """List all supported compliance frameworks"""
    return JSONResponse(
        content={
            "frameworks": [
                {
                    "id": "ecc",
                    "name": "Essential Cybersecurity Controls",
                    "name_ar": "الضوابط الأساسية للأمن السيبراني",
                    "authority": "NCA",
                    "total_controls": 114
                },
                {
                    "id": "ccc",
                    "name": "Cloud Cybersecurity Controls",
                    "name_ar": "ضوابط الأمن السيبراني السحابي",
                    "authority": "NCA",
                    "total_controls": 180
                },
                {
                    "id": "pdpl",
                    "name": "Personal Data Protection Law",
                    "name_ar": "نظام حماية البيانات الشخصية",
                    "authority": "SDAIA",
                    "total_controls": 42
                }
            ]
        }
    )


# Register routers with versioned prefix
app.include_router(controls_router.router, prefix="/api/v1", tags=["Controls"])
app.include_router(evidence_router.router, prefix="/api/v1", tags=["Evidence"])
app.include_router(reporting_router.router, prefix="/api/v1", tags=["Reporting"])
app.include_router(ai_router.router, prefix="/api/v1", tags=["AI/RAG"])
# Register additional API routers from api/ directory
app.include_router(assessments.router, tags=["Assessments"])
app.include_router(api_controls.router, tags=["API Controls"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
