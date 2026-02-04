"""
FastAPI Application - Production Configuration
Security-first architecture with JWT + TLS + Secrets Management
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Import routers
from src.backend.ai_router_secure import router as ai_router
from src.backend.controls.router import router as controls_router
from src.backend.evidence.router import router as evidence_router
from src.backend.reporting.router import router as reporting_router

# Import security middleware
from src.backend.middleware.security import (
    HTTPSRedirectMiddleware,
    SecurityHeadersMiddleware,
    RateLimitMiddleware,
    RequestLoggingMiddleware,
    get_cors_config,
)

# Import secrets management
from src.backend.core.secrets import get_app_secrets

# Load secrets
secrets = get_app_secrets()

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

# 1. HTTPS Redirect (First - redirect before any processing)
app.add_middleware(
    HTTPSRedirectMiddleware,
    enabled=True,  # Set to False for local development
)

# 2. Security Headers (Add security headers to all responses)
app.add_middleware(
    SecurityHeadersMiddleware,
    hsts_max_age=31536000,  # 1 year
    hsts_include_subdomains=True,
    hsts_preload=True,
)

# 3. Rate Limiting (Prevent abuse)
app.add_middleware(
    RateLimitMiddleware,
    requests_per_minute=60,
    burst_size=10,
    enabled=True,
)

# 4. Request Logging (Audit all requests)
app.add_middleware(RequestLoggingMiddleware)

# 5. CORS (Last - handles preflight requests)
cors_config = get_cors_config(
    allowed_origins=[
        "https://sanadcom.sa",
        "https://www.sanadcom.sa",
        "https://app.sanadcom.sa",
        "http://localhost:3000",  # Development frontend
    ]
)
app.add_middleware(CORSMiddleware, **cors_config)

# ============================================================================
# Routers
# ============================================================================

app.include_router(ai_router, prefix="/api/ai", tags=["AI/RAG"])
app.include_router(controls_router, prefix="/api/controls", tags=["Controls"])
app.include_router(evidence_router, prefix="/api/evidence", tags=["Evidence"])
app.include_router(reporting_router, prefix="/api/reporting", tags=["Reporting"])

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
