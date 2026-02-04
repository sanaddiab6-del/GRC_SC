"""
SICO GRC Platform - Main FastAPI Application
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging

from api.controls import router as controls_router
from api.assessments import router as assessments_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="SICO GRC Platform API",
    description="Saudi Regulatory Compliance Engine (ECC/CCC/PDPL)",
    version="0.1.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include routers
app.include_router(controls_router)
app.include_router(assessments_router)


@app.on_event("startup")
async def startup_event():
    """Initialize application on startup"""
    logger.info("Starting SICO GRC Platform API...")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down SICO GRC Platform API...")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "SICO GRC Platform API",
        "version": "0.1.0",
        "status": "operational",
        "frameworks": ["ECC", "CCC", "PDPL"]
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "sico-grc-api"
    }


@app.get("/api/v1/frameworks")
async def list_frameworks():
    """List supported regulatory frameworks"""
    return {
        "frameworks": [
            {
                "id": "ecc",
                "name": "Essential Cybersecurity Controls",
                "authority": "NCA - National Cybersecurity Authority",
                "version": "2.0",
                "controls_count": 114
            },
            {
                "id": "ccc",
                "name": "Cloud Cybersecurity Controls",
                "authority": "NCA - National Cybersecurity Authority",
                "version": "1.0",
                "controls_count": 180
            },
            {
                "id": "pdpl",
                "name": "Personal Data Protection Law",
                "authority": "SDAIA - Saudi Data & AI Authority",
                "version": "2021",
                "controls_count": 42
            }
        ]
    }


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc) if app.debug else "An error occurred"
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
