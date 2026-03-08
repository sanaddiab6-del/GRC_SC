"""
JWT/OAuth2 Authentication & Authorization
Production-grade authentication system
Compliant with: NCA ECC-IS-3, PDPL Article 23, ISO 27001
"""

from __future__ import annotations

import base64
import hashlib
import os
from datetime import datetime, timedelta
from typing import Optional, TYPE_CHECKING

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from passlib.context import CryptContext
from pydantic import BaseModel, Field

# Try to import AI security - may not be available in all environments
AI_SECURITY_AVAILABLE = False

if TYPE_CHECKING:
    from ai.security.ai_security import AIRole, AIPermission, QueryContext
else:
    try:
        from ai.security.ai_security import AIRole, AIPermission, QueryContext
        AI_SECURITY_AVAILABLE = True
    except ImportError:
        # Define placeholder classes when AI module is not available
        AIRole = None
        AIPermission = None
        QueryContext = None
        AI_SECURITY_AVAILABLE = False

# JWT Configuration
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
JWT_ALGORITHM = "HS256"
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
JWT_REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("JWT_REFRESH_TOKEN_EXPIRE_DAYS", "7"))

# Password hashing — plain bcrypt scheme with manual SHA-256 pre-hash.
# passlib 1.7.4's built-in bcrypt_sha256 handler is incompatible with
# bcrypt ≥ 5.0 (its internal wrap-bug probe sends >72-byte payloads that
# bcrypt 5.0 rejects).  We replicate the same security property manually:
# SHA-256 compresses any-length password to a fixed 32-byte digest which,
# base64-encoded, is always 44 chars — well under bcrypt's 72-byte limit.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def _prehash_password(password: str) -> str:
    """SHA-256 pre-hash a password so bcrypt never sees >72 bytes."""
    return base64.b64encode(
        hashlib.sha256(password.encode("utf-8")).digest()
    ).decode("ascii")

# HTTP Bearer token scheme
security = HTTPBearer()


# ============================================================================
# Token Models
# ============================================================================

class TokenPayload(BaseModel):
    """JWT token payload structure"""
    sub: str = Field(..., description="User ID (subject)")
    tenant_id: str = Field(..., description="Tenant/client ID")
    role: str = Field(..., description="User role")
    permissions: list[str] = Field(default_factory=list, description="User permissions")
    exp: datetime = Field(..., description="Expiration time")
    iat: datetime = Field(default_factory=datetime.utcnow, description="Issued at")
    jti: Optional[str] = Field(None, description="JWT ID (unique identifier)")


class Token(BaseModel):
    """Token response model"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds


class TokenData(BaseModel):
    """Decoded token data"""
    user_id: str
    tenant_id: str
    role: AIRole
    permissions: set[AIPermission]


# ============================================================================
# Password Utilities
# ============================================================================

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash"""
    return pwd_context.verify(_prehash_password(plain_password), hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password using SHA-256 pre-hash + bcrypt (safe for any length)."""
    return pwd_context.hash(_prehash_password(password))


# ============================================================================
# JWT Token Generation
# ============================================================================

def create_access_token(
    user_id: str,
    tenant_id: str,
    role: AIRole,
    permissions: set[AIPermission],
    expires_delta: Optional[timedelta] = None,
) -> str:
    """
    Create JWT access token
    
    Args:
        user_id: User identifier
        tenant_id: Tenant identifier
        role: User role
        permissions: User permissions
        expires_delta: Token expiration time
    
    Returns:
        Encoded JWT token
    """
    if expires_delta is None:
        expires_delta = timedelta(minutes=JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    
    expire = datetime.utcnow() + expires_delta
    
    payload = {
        "sub": user_id,
        "tenant_id": tenant_id,
        "role": role.value,
        "permissions": [p.value for p in permissions],
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "access",
    }
    
    encoded_jwt = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt


def create_refresh_token(
    user_id: str,
    tenant_id: str,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """
    Create JWT refresh token
    
    Args:
        user_id: User identifier
        tenant_id: Tenant identifier
        expires_delta: Token expiration time
    
    Returns:
        Encoded JWT refresh token
    """
    if expires_delta is None:
        expires_delta = timedelta(days=JWT_REFRESH_TOKEN_EXPIRE_DAYS)
    
    expire = datetime.utcnow() + expires_delta
    
    payload = {
        "sub": user_id,
        "tenant_id": tenant_id,
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "refresh",
    }
    
    encoded_jwt = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt


def create_token_pair(
    user_id: str,
    tenant_id: str,
    role: AIRole,
    permissions: set[AIPermission],
) -> Token:
    """
    Create access + refresh token pair
    
    Args:
        user_id: User identifier
        tenant_id: Tenant identifier
        role: User role
        permissions: User permissions
    
    Returns:
        Token pair
    """
    access_token = create_access_token(user_id, tenant_id, role, permissions)
    refresh_token = create_refresh_token(user_id, tenant_id)
    
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


# ============================================================================
# JWT Token Validation
# ============================================================================

def decode_token(token: str) -> dict:
    """
    Decode and validate JWT token
    
    Args:
        token: JWT token string
    
    Returns:
        Decoded payload
    
    Raises:
        HTTPException: If token is invalid or expired
    """
    try:
        payload = jwt.decode(
            token,
            JWT_SECRET_KEY,
            algorithms=[JWT_ALGORITHM],
        )
        return payload
    
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "message_en": "Token has expired",
                "message_ar": "انتهت صلاحية الرمز",
            },
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "message_en": "Invalid authentication token",
                "message_ar": "رمز المصادقة غير صالح",
            },
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_token_data(token: str) -> TokenData:
    """
    Extract user data from token
    
    Args:
        token: JWT token string
    
    Returns:
        TokenData with user information
    
    Raises:
        HTTPException: If token is invalid
    """
    payload = decode_token(token)
    
    # Extract fields
    user_id: str = payload.get("sub")
    tenant_id: str = payload.get("tenant_id")
    role_str: str = payload.get("role")
    permissions_list: list = payload.get("permissions", [])
    
    # Validate required fields
    if not user_id or not tenant_id or not role_str:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "message_en": "Invalid token payload",
                "message_ar": "محتوى الرمز غير صالح",
            },
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Convert to enums
    try:
        role = AIRole(role_str)
        permissions = {AIPermission(p) for p in permissions_list}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "message_en": f"Invalid role or permissions: {str(e)}",
                "message_ar": f"دور أو صلاحيات غير صالحة: {str(e)}",
            },
        )
    
    return TokenData(
        user_id=user_id,
        tenant_id=tenant_id,
        role=role,
        permissions=permissions,
    )


# ============================================================================
# FastAPI Dependencies
# ============================================================================

async def get_current_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> str:
    """
    Extract JWT token from Authorization header
    
    Returns:
        JWT token string
    """
    return credentials.credentials


async def get_current_user(
    token: str = Depends(get_current_token),
) -> TokenData:
    """
    Get current authenticated user from token
    
    Returns:
        TokenData with user information
    """
    return get_token_data(token)


async def get_query_context(
    token_data: TokenData = Depends(get_current_user),
    # Request object for IP address (optional, add if needed)
    # request: Request,
) -> QueryContext:
    """
    Build QueryContext from authenticated token
    
    This replaces the header-based authentication
    
    Returns:
        QueryContext for AI security layer
    """
    return QueryContext(
        user_id=token_data.user_id,
        tenant_id=token_data.tenant_id,
        role=token_data.role,
        permissions=token_data.permissions,
        ip_address="0.0.0.0",  # Get from request.client.host if needed
        user_agent="unknown",  # Get from request.headers.get("user-agent") if needed
        session_id=token_data.user_id,  # Use user_id as session_id or generate unique
    )


# ============================================================================
# Role-Based Authorization Helpers
# ============================================================================

def require_role(required_role: AIRole):
    """
    Dependency to require specific role
    
    Usage:
        @router.get("/admin", dependencies=[Depends(require_role(AIRole.AI_ADMIN))])
    """
    async def role_checker(token_data: TokenData = Depends(get_current_user)):
        if token_data.role != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "message_en": f"Role {required_role.value} required",
                    "message_ar": f"الدور {required_role.value} مطلوب",
                },
            )
        return token_data
    
    return role_checker


def require_permission(required_permission: AIPermission):
    """
    Dependency to require specific permission
    
    Usage:
        @router.post("/query", dependencies=[Depends(require_permission(AIPermission.QUERY_RAG))])
    """
    async def permission_checker(token_data: TokenData = Depends(get_current_user)):
        if required_permission not in token_data.permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "message_en": f"Permission {required_permission.value} required",
                    "message_ar": f"الصلاحية {required_permission.value} مطلوبة",
                },
            )
        return token_data
    
    return permission_checker


# ============================================================================
# OAuth2 Integration (Azure AD Example)
# ============================================================================

class AzureADConfig(BaseModel):
    """Azure AD OAuth2 configuration"""
    tenant_id: str
    client_id: str
    client_secret: str
    authority: str = Field(default_factory=lambda: "https://login.microsoftonline.com")
    scope: list[str] = Field(default_factory=lambda: ["openid", "profile", "email"])


def validate_azure_ad_token(token: str, config: AzureADConfig) -> dict:
    """
    Validate Azure AD token (placeholder)
    
    In production, use microsoft-identity-web or msal library
    
    Args:
        token: Azure AD token
        config: Azure AD configuration
    
    Returns:
        Validated token payload
    """
    # TODO: Implement Azure AD token validation
    # from msal import ConfidentialClientApplication
    # 
    # app = ConfidentialClientApplication(
    #     config.client_id,
    #     authority=f"{config.authority}/{config.tenant_id}",
    #     client_credential=config.client_secret,
    # )
    # 
    # result = app.acquire_token_silent(config.scope, account=None)
    # Validate result and extract user info
    
    raise NotImplementedError(
        "Azure AD integration not yet implemented. "
        "Use JWT tokens for now or implement Azure AD validation."
    )


# ============================================================================
# Security Utilities
# ============================================================================

def is_token_blacklisted(token: str) -> bool:
    """
    Check if token is blacklisted (revoked)
    
    In production, use Redis or database for token blacklist
    
    Args:
        token: JWT token
    
    Returns:
        True if token is blacklisted
    """
    # TODO: Implement token blacklist check
    # Example with Redis:
    # return redis_client.exists(f"blacklist:{token}")
    return False


def blacklist_token(token: str, expires_in: int):
    """
    Add token to blacklist (revoke)
    
    Args:
        token: JWT token
        expires_in: TTL in seconds
    """
    # TODO: Implement token blacklisting
    # Example with Redis:
    # redis_client.setex(f"blacklist:{token}", expires_in, "1")
    pass


# ============================================================================
# Example Usage
# ============================================================================

"""
# In your FastAPI app:

from src.backend.core.auth import get_query_context, create_token_pair
from ai.security.ai_security import AIRole, AIPermission

# Login endpoint
@router.post("/auth/login")
async def login(username: str, password: str):
    # Validate user credentials (from database)
    user = authenticate_user(username, password)
    
    if not user:
        raise HTTPException(401, detail="Invalid credentials")
    
    # Create token pair
    tokens = create_token_pair(
        user_id=user.id,
        tenant_id=user.tenant_id,
        role=user.role,
        permissions=user.permissions,
    )
    
    return tokens

# Protected endpoint
@router.post("/ai/query")
async def secure_query(
    request: QueryRequest,
    context: QueryContext = Depends(get_query_context),
):
    # context now has validated user from JWT token
    # Proceed with AI query with security layers
    pass

# Role-protected endpoint
@router.get("/admin", dependencies=[Depends(require_role(AIRole.AI_ADMIN))])
async def admin_endpoint():
    return {"message": "Admin access granted"}

# Permission-protected endpoint
@router.post("/export", dependencies=[Depends(require_permission(AIPermission.EXPORT_DATA))])
async def export_data():
    return {"message": "Export access granted"}
"""
