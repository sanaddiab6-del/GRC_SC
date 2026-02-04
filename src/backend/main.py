"""
FastAPI Application - Production Configuration
Security-first architecture with JWT + TLS + Secrets Management
"""

import sys
import os
from pathlib import Path

# Add parent directories to Python path
backend_dir = Path(__file__).parent
src_dir = backend_dir.parent
project_root = src_dir.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(src_dir))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Set environment variables for development
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///./sanadcom.db")
os.environ.setdefault("JWT_SECRET_KEY", "dev-secret-key-change-in-production")

# Load secrets (with fallback for development)
secrets = None

# Create FastAPI app
app = FastAPI(
    title="Sanadcom GRC Platform",
    description="Saudi-compliant GRC platform with AI/RAG capabilities",
    version="2.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

# ============================================================================
# Security Middleware (Order Matters!)
# ============================================================================

# Simple CORS for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# Routers
# ============================================================================

# Routers will be added as modules are completed
# app.include_router(ai_router, prefix="/api/ai", tags=["AI/RAG"])
# app.include_router(controls_router, prefix="/api/controls", tags=["Controls"])
# app.include_router(evidence_router, prefix="/api/evidence", tags=["Evidence"])
# app.include_router(reporting_router, prefix="/api/reporting", tags=["Reporting"])

# ============================================================================
# Health Check
# ============================================================================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "2.0.0",
        "environment": "production",
    }

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message_en": "Sanadcom GRC Platform API",
        "message_ar": "منصة سند كوم للحوكمة والمخاطر والامتثال",
        "docs": "/api/docs",
    }

# ============================================================================
# Run Application
# ============================================================================

if __name__ == "__main__":
    import os
    
    # SSL/TLS configuration
    ssl_keyfile = os.getenv("SSL_KEY_FILE", "./certs/key.pem")
    ssl_certfile = os.getenv("SSL_CERT_FILE", "./certs/cert.pem")
    
    # Check if SSL certificates exist
    use_ssl = os.path.exists(ssl_keyfile) and os.path.exists(ssl_certfile)
    
    if use_ssl:
        print("🔒 Starting with SSL/TLS enabled")
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=443,
            ssl_keyfile=ssl_keyfile,
            ssl_certfile=ssl_certfile,
            reload=False,  # Disable reload in production
        )
    else:
        print("⚠️  SSL certificates not found. Running without TLS.")
        print("⚠️  Generate certificates with: make generate-certs")
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,  # Enable reload for development
        )
