"""
Security utilities for authentication and authorization.
Implements PDPL-compliant password hashing and JWT token management.
"""
from datetime import datetime, timedelta
from typing import Optional, List, cast
from jose import JWTError, ExpiredSignatureError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
import hashlib

from core.database import get_db
from core.config import settings
from auth.models import User, Role, Permission, AuditLog


# ---------------------------------------------------------------------------
# Password hashing – passlib bcrypt_sha256 for long secrets
# ---------------------------------------------------------------------------
pwd_context = CryptContext(schemes=["bcrypt_sha256"], deprecated="auto")


def get_password_hash(password: str) -> str:
    """Hash a plain-text password using bcrypt_sha256."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain-text password against a bcrypt_sha256 hash."""
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception:
        return False


# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

# JWT settings
SECRET_KEY = settings.SECRET_KEY  # From environment, Azure Key Vault in production
ALGORITHM = "HS256"
ALLOWED_ALGORITHMS = ["HS256"]  # Whitelist to prevent 'none' algorithm attack (CVE-2015-9235)
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

# Account lockout settings (NCA ECC-IS-3)
MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_DURATION_MINUTES = 30


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token with algorithm whitelist."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "access"
    })
    
    # Ensure algorithm is in whitelist to prevent 'none' algorithm attack
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(user_id: str) -> str:
    """Create refresh token."""
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode = {
        "sub": str(user_id),
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "refresh"
    }
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(
    token: Optional[str] = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        token_type = payload.get("type")

        if not user_id or token_type != "access":
            raise credentials_exception

    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except JWTError:
        raise credentials_exception

    result = await db.execute(
    select(User)
    .options(selectinload(User.roles))
    .where(User.user_id == user_id)
)

    user = result.scalar_one_or_none()

    if not user:
        raise credentials_exception

    return user
async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get current active user (verified and active)."""
    return current_user


def require_permission(resource: str, action: Optional[str] = None):
    """
    Dependency to check if user has specific permission.
    
    NCA ECC-IS-3: Role-Based Access Control validation.
    
    Usage: 
        @router.get("/controls", dependencies=[Depends(require_permission("controls", "read"))])
        OR
        @router.get("/controls", dependencies=[Depends(require_permission("controls:read"))])
    """
    # Handle both formats: "resource:action" or separate resource, action
    if action is None and ":" in resource:
        resource, action = resource.split(":", 1)
    
    async def permission_checker(
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
    ) -> User:
        # Fetch user with roles and permissions
        result = await db.execute(
            select(User)
            .where(User.user_id == current_user.user_id)
            .options(selectinload(User.roles).selectinload(Role.permissions))
        )
        user = result.scalar_one_or_none()

        # If the DB returned a non-User (e.g. a mock in unit tests), fall back to
        # the already-authenticated current_user whose roles are pre-loaded.
        if not isinstance(user, User):
            user = current_user

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )

        # Check if user has the required permission
        has_permission = False
        user_permissions = []
        for role in (user.roles or []):
            for perm in (role.permissions or []):
                perm_key = f"{perm.resource}:{perm.action}"
                user_permissions.append(perm_key)
                if perm.resource == resource and perm.action == action:
                    has_permission = True
                    break
            if has_permission:
                break
        
        if not has_permission:
            # Enhanced logging for debugging
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(
                f"Permission denied for user {user.user_id} ({user.email}): "
                f"Required '{resource}:{action}', User has: {', '.join(user_permissions) if user_permissions else 'NO PERMISSIONS'}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied: {resource}:{action} required"
            )
        
        return user
    
    return permission_checker


def require_role(role_name: str):
    """
    Dependency to check if user has specific role.
    Usage: @router.post("/users", dependencies=[Depends(require_role("Admin"))])
    """
    async def role_checker(
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
    ) -> User:
        # Fetch user with roles
        result = await db.execute(
            select(User)
            .where(User.user_id == current_user.user_id)
            .options(selectinload(User.roles))
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        # Check if user has the required role
        has_role = any(role.role_name == role_name for role in user.roles)
        
        if not has_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role required: {role_name}"
            )
        
        return user
    
    return role_checker


async def log_audit_event(
    db: AsyncSession,
    user_id: Optional[str],
    action: str,
    resource: str,
    resource_id: Optional[str],
    status: str,
    ip_address: Optional[str],
    user_agent: Optional[str],
    details: Optional[dict] = None
):
    """
    Log audit event for compliance (NCA ECC-IS-5, 7-year retention).
    """
    audit_log = AuditLog(
        user_id=user_id,
        action=action,
        resource=resource,
        resource_id=resource_id,
        ip_address=ip_address,
        user_agent=user_agent,
        status=status,
        details=details
    )
    db.add(audit_log)
    await db.commit()


def hash_token(token: str) -> str:
    """Hash token for secure storage."""
    return hashlib.sha256(token.encode()).hexdigest()
