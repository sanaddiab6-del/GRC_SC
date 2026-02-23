"""
Security Middleware for FastAPI
TLS/HTTPS enforcement, security headers, rate limiting
Compliant with: NCA ECC-IS-3, PDPL Article 23, ISO 27001 A.8.9
"""

from __future__ import annotations

import time
from collections import defaultdict
from typing import Callable

from fastapi import Request, Response, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware


# ============================================================================
# HTTPS Redirect Middleware
# ============================================================================

class HTTPSRedirectMiddleware(BaseHTTPMiddleware):
    """
    Redirect HTTP requests to HTTPS
    Force secure connections
    """
    
    def __init__(self, app, enabled: bool = True):
        """
        Initialize HTTPS redirect middleware
        
        Args:
            app: FastAPI application
            enabled: Enable HTTPS redirect (disable for local development)
        """
        super().__init__(app)
        self.enabled = enabled
    
    async def dispatch(self, request: Request, call_next: Callable):
        """Process request and redirect if needed"""
        if self.enabled:
            # Check if request is HTTPS
            if request.url.scheme != "https":
                # Build HTTPS URL
                https_url = request.url.replace(scheme="https")
                
                return JSONResponse(
                    status_code=status.HTTP_301_MOVED_PERMANENTLY,
                    content={
                        "message_en": "HTTPS required. Redirecting to secure connection.",
                        "message_ar": "HTTPS مطلوب. إعادة التوجيه إلى اتصال آمن.",
                        "redirect_url": str(https_url),
                    },
                    headers={
                        "Location": str(https_url),
                    },
                )
        
        # Continue with HTTPS request
        response = await call_next(request)
        return response


# ============================================================================
# Security Headers Middleware
# ============================================================================

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Add security headers to all responses
    
    Headers added:
    - Strict-Transport-Security (HSTS)
    - X-Content-Type-Options
    - X-Frame-Options
    - X-XSS-Protection
    - Content-Security-Policy
    - Referrer-Policy
    - Permissions-Policy
    """
    
    def __init__(
        self,
        app,
        hsts_max_age: int = 31536000,  # 1 year
        hsts_include_subdomains: bool = True,
        hsts_preload: bool = True,
    ):
        """
        Initialize security headers middleware
        
        Args:
            app: FastAPI application
            hsts_max_age: HSTS max-age in seconds
            hsts_include_subdomains: Include subdomains in HSTS
            hsts_preload: Enable HSTS preload
        """
        super().__init__(app)
        self.hsts_max_age = hsts_max_age
        self.hsts_include_subdomains = hsts_include_subdomains
        self.hsts_preload = hsts_preload
    
    async def dispatch(self, request: Request, call_next: Callable):
        """Add security headers to response"""
        response = await call_next(request)
        
        # Strict-Transport-Security (HSTS)
        hsts_value = f"max-age={self.hsts_max_age}"
        if self.hsts_include_subdomains:
            hsts_value += "; includeSubDomains"
        if self.hsts_preload:
            hsts_value += "; preload"
        response.headers["Strict-Transport-Security"] = hsts_value
        
        # Prevent MIME type sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"
        
        # Prevent clickjacking
        response.headers["X-Frame-Options"] = "DENY"
        
        # XSS protection (legacy, but still used)
        response.headers["X-XSS-Protection"] = "1; mode=block"
        
        # Content Security Policy
        csp = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self' data:; "
            "connect-src 'self'; "
            "frame-ancestors 'none'; "
            "base-uri 'self'; "
            "form-action 'self'"
        )
        response.headers["Content-Security-Policy"] = csp
        
        # Referrer policy
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # Permissions policy (disable dangerous features)
        permissions = (
            "geolocation=(), "
            "microphone=(), "
            "camera=(), "
            "payment=(), "
            "usb=(), "
            "magnetometer=(), "
            "gyroscope=(), "
            "accelerometer=()"
        )
        response.headers["Permissions-Policy"] = permissions
        
        return response


# ============================================================================
# Rate Limiting Middleware
# ============================================================================

class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting middleware
    Prevent abuse and DoS attacks
    
    Note: In production, use Redis for distributed rate limiting
    """
    
    def __init__(
        self,
        app,
        requests_per_minute: int = 60,
        burst_size: int = 10,
        enabled: bool = True,
    ):
        """
        Initialize rate limiting middleware
        
        Args:
            app: FastAPI application
            requests_per_minute: Maximum requests per minute per IP
            burst_size: Allow burst of requests
            enabled: Enable rate limiting
        """
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.burst_size = burst_size
        self.enabled = enabled
        
        # In-memory storage (use Redis in production)
        self.request_counts: dict[str, list[float]] = defaultdict(list)
    
    async def dispatch(self, request: Request, call_next: Callable):
        """Check rate limit and process request"""
        if not self.enabled:
            return await call_next(request)
        
        # Get client IP
        client_ip = request.client.host if request.client else "unknown"
        
        # Current timestamp
        now = time.time()
        
        # Clean old requests (older than 1 minute)
        self.request_counts[client_ip] = [
            ts for ts in self.request_counts[client_ip]
            if now - ts < 60
        ]
        
        # Check rate limit
        request_count = len(self.request_counts[client_ip])
        
        if request_count >= self.requests_per_minute:
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "message_en": "Rate limit exceeded. Please try again later.",
                    "message_ar": "تم تجاوز الحد الأقصى للطلبات. يرجى المحاولة لاحقاً.",
                    "retry_after": 60,
                },
                headers={
                    "Retry-After": "60",
                    "X-RateLimit-Limit": str(self.requests_per_minute),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(int(now) + 60),
                },
            )
        
        # Add current request
        self.request_counts[client_ip].append(now)
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers
        remaining = self.requests_per_minute - len(self.request_counts[client_ip])
        response.headers["X-RateLimit-Limit"] = str(self.requests_per_minute)
        response.headers["X-RateLimit-Remaining"] = str(max(0, remaining))
        response.headers["X-RateLimit-Reset"] = str(int(now) + 60)
        
        return response


# ============================================================================
# Request Logging Middleware
# ============================================================================

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Log all requests for security auditing
    Compliant with NCA ECC logging requirements
    """
    
    async def dispatch(self, request: Request, call_next: Callable):
        """Log request and response"""
        # Start time
        start_time = time.time()
        
        # Get client info
        client_ip = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "unknown")
        
        # Log request
        print(
            f"📥 {request.method} {request.url.path} "
            f"from {client_ip} "
            f"[{user_agent}]"
        )
        
        # Process request
        try:
            response = await call_next(request)
            
            # Calculate duration
            duration_ms = (time.time() - start_time) * 1000
            
            # Log response
            print(
                f"📤 {request.method} {request.url.path} "
                f"-> {response.status_code} "
                f"({duration_ms:.2f}ms)"
            )
            
            # Add timing header
            response.headers["X-Response-Time"] = f"{duration_ms:.2f}ms"
            
            return response
        
        except Exception as e:
            # Log error
            print(
                f"❌ {request.method} {request.url.path} "
                f"-> ERROR: {str(e)}"
            )
            raise


# ============================================================================
# CORS Security Middleware
# ============================================================================

def get_cors_config(allowed_origins: list[str] = None):
    """
    Get CORS configuration for production
    
    Args:
        allowed_origins: List of allowed origins
    
    Returns:
        CORS configuration dict
    """
    if allowed_origins is None:
        allowed_origins = [
            "https://sanadcom.sa",
            "https://www.sanadcom.sa",
            "https://app.sanadcom.sa",
        ]
    
    return {
        "allow_origins": allowed_origins,
        "allow_credentials": True,
        "allow_methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": [
            "Authorization",
            "Content-Type",
            "X-Request-ID",
            "X-Tenant-ID",
        ],
        "expose_headers": [
            "X-RateLimit-Limit",
            "X-RateLimit-Remaining",
            "X-RateLimit-Reset",
            "X-Response-Time",
        ],
        "max_age": 3600,  # 1 hour
    }


# ============================================================================
# Example Usage
# ============================================================================

"""
# In your FastAPI app (main.py):

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.backend.middleware.security import (
    HTTPSRedirectMiddleware,
    SecurityHeadersMiddleware,
    RateLimitMiddleware,
    RequestLoggingMiddleware,
    get_cors_config,
)

app = FastAPI()

# Add security middleware (order matters!)

# 1. HTTPS redirect (first)
app.add_middleware(
    HTTPSRedirectMiddleware,
    enabled=True,  # Set to False for local development
)

# 2. Security headers
app.add_middleware(
    SecurityHeadersMiddleware,
    hsts_max_age=31536000,  # 1 year
    hsts_include_subdomains=True,
    hsts_preload=True,
)

# 3. Rate limiting
app.add_middleware(
    RateLimitMiddleware,
    requests_per_minute=60,
    burst_size=10,
    enabled=True,
)

# 4. Request logging
app.add_middleware(RequestLoggingMiddleware)

# 5. CORS (last)
cors_config = get_cors_config()
app.add_middleware(CORSMiddleware, **cors_config)

# SSL/TLS Configuration (for development):

import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=443,
        ssl_keyfile="./certs/key.pem",
        ssl_certfile="./certs/cert.pem",
    )

# Generate self-signed certificate for development:

openssl req -x509 -newkey rsa:4096 -nodes \\
    -keyout certs/key.pem \\
    -out certs/cert.pem \\
    -days 365 \\
    -subj "/C=SA/ST=Riyadh/L=Riyadh/O=Sanadcom/CN=localhost"

# Production TLS termination (nginx):

server {
    listen 443 ssl http2;
    server_name sanadcom.sa;
    
    ssl_certificate /etc/ssl/certs/sanadcom.crt;
    ssl_certificate_key /etc/ssl/private/sanadcom.key;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    
    location / {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

server {
    listen 80;
    server_name sanadcom.sa;
    return 301 https://$host$request_uri;
}
"""
