"""
Authentication and authorization routes.
Implements NCA ECC-IS-3 and PDPL Article 29 requirements.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timedelta
from typing import List, Optional, cast

from core.database import get_db
from auth import schemas
from auth.models import User, Role, Permission, RefreshToken
from auth.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    create_refresh_token,
    get_current_user,
    get_current_active_user,
    require_role,
    log_audit_event,
    hash_token,
    MAX_LOGIN_ATTEMPTS,
    LOCKOUT_DURATION_MINUTES,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    REFRESH_TOKEN_EXPIRE_DAYS
)


router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: schemas.UserCreate,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Register a new user.
    Implements PDPL-compliant password hashing.
    """
    # Check if user already exists
    result = await db.execute(select(User).where(User.email == user_data.email))
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        email=user_data.email,
        password_hash=hashed_password,
        full_name_en=user_data.full_name_en,
        full_name_ar=user_data.full_name_ar
    )
    
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    # Audit log
    await log_audit_event(
        db=db,
        user_id=str(new_user.user_id),
        action="register",
        resource="users",
        resource_id=str(new_user.user_id),
        status="success",
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent")
    )
    
    return new_user


@router.post("/login", response_model=schemas.TokenResponse)
async def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """
    User login with JWT token issuance.
    Implements account lockout after failed attempts (NCA ECC-IS-3).
    """
    # Fetch user
    result = await db.execute(select(User).where(User.email == form_data.username))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Check account lockout
    locked_until = cast(Optional[datetime], getattr(user, "locked_until"))
    if locked_until and locked_until > datetime.utcnow():
        remaining_minutes = int((locked_until - datetime.utcnow()).total_seconds() / 60)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Account locked. Try again in {remaining_minutes} minutes"
        )
    
    # Verify password
    if not verify_password(form_data.password, cast(str, getattr(user, "password_hash"))):
        # Increment failed login attempts
        failed_attempts = int(getattr(user, "failed_login_attempts") or 0) + 1
        setattr(user, "failed_login_attempts", failed_attempts)
        
        if failed_attempts >= MAX_LOGIN_ATTEMPTS:
            setattr(user, "locked_until", datetime.utcnow() + timedelta(minutes=LOCKOUT_DURATION_MINUTES))
        
        await db.commit()
        
        # Audit log
        await log_audit_event(
            db=db,
            user_id=str(user.user_id),
            action="login",
            resource="auth",
            resource_id=str(user.user_id),
            status="failure",
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
            details={"reason": "incorrect_password"}
        )
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Check if user is active
    if not bool(getattr(user, "is_active")):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive"
        )
    
    # Reset failed login attempts
    setattr(user, "failed_login_attempts", 0)
    setattr(user, "locked_until", None)
    setattr(user, "last_login_at", datetime.utcnow())
    
    # Create tokens
    user_id_value = str(getattr(user, "user_id"))
    access_token = create_access_token(data={"sub": user_id_value})
    refresh_token_str = create_refresh_token(user_id_value)
    
    # Store refresh token
    refresh_token = RefreshToken(
        user_id=getattr(user, "user_id"),
        token_hash=hash_token(refresh_token_str),
        expires_at=datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    )
    db.add(refresh_token)
    
    await db.commit()
    
    # Audit log
    await log_audit_event(
        db=db,
        user_id=str(user.user_id),
        action="login",
        resource="auth",
        resource_id=str(user.user_id),
        status="success",
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent")
    )
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token_str,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }


@router.post("/refresh", response_model=schemas.TokenResponse)
async def refresh_token(
    token_data: schemas.TokenRefresh,
    db: AsyncSession = Depends(get_db)
):
    """Refresh access token using refresh token."""
    from jose import jwt, JWTError
    from auth.security import SECRET_KEY, ALGORITHM
    
    try:
        payload = jwt.decode(token_data.refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        token_type = payload.get("type")
        
        if token_type != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type"
            )
        
        # Verify refresh token in database
        token_hash = hash_token(token_data.refresh_token)
        result = await db.execute(
            select(RefreshToken).where(
                RefreshToken.token_hash == token_hash,
                RefreshToken.revoked_at.is_(None),
                RefreshToken.expires_at > datetime.utcnow()
            )
        )
        stored_token = result.scalar_one_or_none()
        
        if not stored_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token"
            )
        
        # Create new access token
        access_token = create_access_token(data={"sub": user_id})
        
        return {
            "access_token": access_token,
            "refresh_token": token_data.refresh_token,
            "token_type": "bearer",
            "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }
        
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )


@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Logout user by revoking all refresh tokens.
    """
    # Revoke all refresh tokens for this user
    result = await db.execute(
        select(RefreshToken).where(
            RefreshToken.user_id == current_user.user_id,
            RefreshToken.revoked_at.is_(None)
        )
    )
    tokens = result.scalars().all()
    
    for token in tokens:
        setattr(token, "revoked_at", datetime.utcnow())
    
    await db.commit()
    
    # Audit log
    await log_audit_event(
        db=db,
        user_id=str(current_user.user_id),
        action="logout",
        resource="auth",
        resource_id=str(current_user.user_id),
        status="success",
        ip_address=None,
        user_agent=None
    )
    
    return {"message": "Successfully logged out"}


@router.get("/me", response_model=schemas.UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get current user information."""
    # Fetch user with roles
    result = await db.execute(select(User).where(User.user_id == current_user.user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Get role names
    role_names = [role.role_name for role in user.roles]
    
    response = schemas.UserResponse(
        user_id=getattr(user, "user_id"),
        email=cast(str, getattr(user, "email")),
        full_name_en=getattr(user, "full_name_en"),
        full_name_ar=getattr(user, "full_name_ar"),
        is_active=bool(getattr(user, "is_active")),
        is_verified=bool(getattr(user, "is_verified")),
        last_login_at=getattr(user, "last_login_at"),
        created_at=getattr(user, "created_at"),
        roles=role_names
    )
    
    return response


@router.post("/change-password")
async def change_password(
    password_data: schemas.PasswordChange,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Change user password."""
    # Verify old password
    if not verify_password(password_data.old_password, cast(str, getattr(current_user, "password_hash"))):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect old password"
        )
    
    # Update password
    setattr(current_user, "password_hash", get_password_hash(password_data.new_password))
    await db.commit()
    
    # Audit log
    await log_audit_event(
        db=db,
        user_id=str(current_user.user_id),
        action="change_password",
        resource="users",
        resource_id=str(current_user.user_id),
        status="success",
        ip_address=None,
        user_agent=None
    )
    
    return {"message": "Password changed successfully"}


# Admin endpoints
@router.get("/users", response_model=List[schemas.UserResponse])
async def list_users(
    current_user: User = Depends(require_role("Admin")),
    db: AsyncSession = Depends(get_db)
):
    """List all users (Admin only)."""
    result = await db.execute(select(User))
    users = result.scalars().all()
    
    return [
        schemas.UserResponse(
            user_id=getattr(user, "user_id"),
            email=cast(str, getattr(user, "email")),
            full_name_en=getattr(user, "full_name_en"),
            full_name_ar=getattr(user, "full_name_ar"),
            is_active=bool(getattr(user, "is_active")),
            is_verified=bool(getattr(user, "is_verified")),
            last_login_at=getattr(user, "last_login_at"),
            created_at=getattr(user, "created_at"),
            roles=[role.role_name for role in user.roles]
        )
        for user in users
    ]


@router.post("/users/{user_id}/roles")
async def assign_roles_to_user(
    user_id: str,
    role_assignment: schemas.UserRoleAssignment,
    current_user: User = Depends(require_role("Admin")),
    db: AsyncSession = Depends(get_db)
):
    """Assign roles to a user (Admin only)."""
    # Fetch user
    result = await db.execute(select(User).where(User.user_id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Fetch roles
    roles = []
    for role_id in role_assignment.role_ids:
        result = await db.execute(select(Role).where(Role.role_id == role_id))
        role = result.scalar_one_or_none()
        if role:
            roles.append(role)
    
    # Assign roles
    user.roles = roles
    await db.commit()
    
    # Audit log
    await log_audit_event(
        db=db,
        user_id=str(current_user.user_id),
        action="assign_roles",
        resource="users",
        resource_id=str(user_id),
        status="success",
        ip_address=None,
        user_agent=None,
        details={"role_ids": [str(r) for r in role_assignment.role_ids]}
    )
    
    return {"message": "Roles assigned successfully"}
