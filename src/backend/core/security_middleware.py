"""
Security middleware for SICO GRC Platform.
Implements NCA ECC and PDPL security requirements.
"""
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware
import time
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Dict, Tuple
import logging

from core.config import settings


logger = logging.getLogger(__name__)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Add security headers to all responses.
    Implements OWASP security best practices and NCA ECC-IS-3 requirements.
    """
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # OWASP recommended security headers (NCA ECC-IS-3)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"  # HSTS with preload
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        
        # Content Security Policy - Restrictive (adjust for your frontend)
        # Production: Use nonce-based CSP instead of 'unsafe-inline' and 'unsafe-eval'
        csp_policy = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "  # TODO: Replace with nonce
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com; "
            "img-src 'self' data: https:; "
            "connect-src 'self'; "
            "frame-ancestors 'none'; "
            "base-uri 'self'; "
            "form-action 'self'; "
            "upgrade-insecure-requests"  # Force HTTPS
        )
        response.headers["Content-Security-Policy"] = csp_policy
        
        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting middleware to prevent brute force attacks.
    Implements NCA ECC-IS-3 requirements.
    """
    
    def __init__(self, app, requests_per_minute: int = 60, requests_per_hour: int = 1000):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour
        
        # In-memory storage (use Redis in production)
        self.minute_requests: Dict[str, list] = defaultdict(list)
        self.hour_requests: Dict[str, list] = defaultdict(list)
    
    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address, considering X-Forwarded-For header."""
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host if request.client else "unknown"
    
    def _clean_old_requests(self, requests: list, window_seconds: int):
        """Remove requests older than the time window."""
        current_time = time.time()
        return [req_time for req_time in requests if current_time - req_time < window_seconds]
    
    async def dispatch(self, request: Request, call_next):
        if not settings.RATE_LIMIT_ENABLED:
            return await call_next(request)
        
        client_ip = self._get_client_ip(request)
        current_time = time.time()
        
        # Clean old requests
        self.minute_requests[client_ip] = self._clean_old_requests(
            self.minute_requests[client_ip], 60
        )
        self.hour_requests[client_ip] = self._clean_old_requests(
            self.hour_requests[client_ip], 3600
        )
        
        # Check rate limits
        if len(self.minute_requests[client_ip]) >= self.requests_per_minute:
            logger.warning(f"Rate limit exceeded (per minute) for IP: {client_ip}")
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "detail": "Too many requests. Please try again later.",
                    "detail_ar": "عدد كبير جدًا من الطلبات. يرجى المحاولة مرة أخرى لاحقًا."
                },
                headers={"Retry-After": "60"}
            )
        
        if len(self.hour_requests[client_ip]) >= self.requests_per_hour:
            logger.warning(f"Rate limit exceeded (per hour) for IP: {client_ip}")
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "detail": "Hourly rate limit exceeded. Please try again later.",
                    "detail_ar": "تم تجاوز الحد الساعي. يرجى المحاولة مرة أخرى لاحقًا."
                },
                headers={"Retry-After": "3600"}
            )
        
        # Add current request
        self.minute_requests[client_ip].append(current_time)
        self.hour_requests[client_ip].append(current_time)
        
        return await call_next(request)


class AuditLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware to log all API requests for audit trail.
    Implements NCA ECC-IS-5 requirements (7-year retention).
    """
    
    async def dispatch(self, request: Request, call_next):
        # Log request
        start_time = time.time()
        
        # Extract request details
        client_ip = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "unknown")
        method = request.method
        path = request.url.path
        
        try:
            response = await call_next(request)
            status_code = response.status_code
            processing_time = time.time() - start_time
            
            # Log successful request
            logger.info(
                f"API Request: {method} {path} | "
                f"Status: {status_code} | "
                f"Time: {processing_time:.3f}s | "
                f"IP: {client_ip} | "
                f"UA: {user_agent}"
            )
            
            # Add processing time header
            response.headers["X-Process-Time"] = str(processing_time)
            
            return response
            
        except Exception as e:
            processing_time = time.time() - start_time
            
            # Log failed request
            logger.error(
                f"API Request Failed: {method} {path} | "
                f"Error: {str(e)} | "
                f"Time: {processing_time:.3f}s | "
                f"IP: {client_ip}"
            )
            
            raise


class InputValidationMiddleware(BaseHTTPMiddleware):
    """
    Middleware to validate and sanitize input data.
    Prevents common injection attacks (SQL, XSS, etc.).
    """
    
    SUSPICIOUS_PATTERNS = [
        "<script",
        "javascript:",
        "onerror=",
        "onclick=",
        "'; DROP TABLE",
        "'; DELETE FROM",
        "UNION SELECT",
        "../../../",
        "{{",
        "${",
    ]
    
    async def dispatch(self, request: Request, call_next):
        # Check URL for suspicious patterns
        if any(pattern.lower() in request.url.path.lower() for pattern in self.SUSPICIOUS_PATTERNS):
            logger.warning(f"Suspicious URL pattern detected: {request.url.path}")
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "detail": "Invalid request",
                    "detail_ar": "طلب غير صالح"
                }
            )
        
        # Check query parameters
        for key, value in request.query_params.items():
            if any(pattern.lower() in str(value).lower() for pattern in self.SUSPICIOUS_PATTERNS):
                logger.warning(f"Suspicious query parameter detected: {key}={value}")
                return JSONResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    content={
                        "detail": "Invalid query parameter",
                        "detail_ar": "معامل استعلام غير صالح"
                    }
                )
        
        return await call_next(request)


def setup_security_middleware(app):
    """
    Configure all security middleware for the application.
    Call this in main.py after creating the FastAPI app.
    """
    
    # CORS (must be first)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["X-Process-Time"]
    )
    
    # Trusted Host (prevent host header injection)
    if settings.is_production:
        allowed_hosts = ["sico-grc.com", "*.sico-grc.com"]
    else:
        allowed_hosts = [
            "localhost",
            "127.0.0.1",
            "test",
            "testserver",
            "*.sico-grc.com",
            "sico-grc.com",
        ]

    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=allowed_hosts
    )
    
    # Custom security middleware
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(RateLimitMiddleware, 
                      requests_per_minute=settings.RATE_LIMIT_PER_MINUTE,
                      requests_per_hour=settings.RATE_LIMIT_PER_HOUR)
    app.add_middleware(AuditLoggingMiddleware)
    app.add_middleware(InputValidationMiddleware)
    
    logger.info("Security middleware configured successfully")
