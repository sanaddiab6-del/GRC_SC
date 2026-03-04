"""
Authentication and authorization routes.
Implements NCA ECC-IS-3 and PDPL Article 29 requirements.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, text
from sqlalchemy.orm import selectinload
from datetime import datetime, timedelta
from typing import List, Optional, cast

from core.database import get_db
from auth import schemas
from auth.models import User, Role, Permission, RefreshToken, AuditLog
from controls.models import Control
from evidence.models import Evidence
from reporting.models import Report
from core.email import send_account_approved_email, send_account_denied_email
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


def _to_user_response(user: User) -> schemas.UserResponse:
    """Convert ORM User to API-safe DTO (no lazy loading during serialization)."""
    role_names = [role.role_name for role in getattr(user, "roles", [])]
    return schemas.UserResponse(
        user_id=getattr(user, "user_id"),
        email=cast(str, getattr(user, "email")),
        full_name_en=getattr(user, "full_name_en"),
        full_name_ar=getattr(user, "full_name_ar"),
        organization_name=getattr(user, "organization_name"),
        is_active=bool(getattr(user, "is_active")),
        is_verified=bool(getattr(user, "is_verified")),
        last_login_at=getattr(user, "last_login_at"),
        created_at=getattr(user, "created_at"),
        roles=role_names,
    )


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
        # 409 Conflict: distinguishable from 422 validation errors on the frontend
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )
    
    # Create new user – inactive until an admin approves the request
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        email=user_data.email,
        password_hash=hashed_password,
        full_name_en=user_data.full_name_en,
        full_name_ar=user_data.full_name_ar,
        organization_name=user_data.organization_name,
        is_active=False,       # pending admin approval
        is_verified=False,
    )
    
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    # Re-load with eager relationships for async-safe response serialization
    result = await db.execute(
        select(User)
        .where(User.user_id == new_user.user_id)
        .options(selectinload(User.roles))
    )
    user_with_roles = result.scalar_one()
    
    # Audit log
    await log_audit_event(
        db=db,
        user_id=str(user_with_roles.user_id),
        action="register",
        resource="users",
        resource_id=str(user_with_roles.user_id),
        status="success",
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent")
    )

    return _to_user_response(user_with_roles)


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
    
    # Check if user is active / pending approval
    if not bool(getattr(user, "is_active")):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account pending admin approval"
        )
    
    # Reset failed login attempts
    setattr(user, "failed_login_attempts", 0)
    setattr(user, "locked_until", None)
    setattr(user, "last_login_at", datetime.utcnow())
    
    # Create tokens
    user_id_value = str(getattr(user, "user_id"))
    email_value = cast(str, getattr(user, "email"))
    access_token = create_access_token(data={"sub": user_id_value, "email": email_value})
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
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get current user information."""
    # Fetch user with roles
    result = await db.execute(
        select(User)
        .where(User.user_id == current_user.user_id)
        .options(selectinload(User.roles))
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return _to_user_response(user)


@router.get("/me/admin", response_model=schemas.UserResponse)
async def get_current_admin_info(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get current user info (SuperAdmin only)."""
    # Fetch user with roles
    result = await db.execute(
        select(User)
        .where(User.user_id == current_user.user_id)
        .options(selectinload(User.roles))
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    if not _is_super_admin(user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="SuperAdmin access required"
        )

    return _to_user_response(user)


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
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """List all active users (Admin / super_admin only)."""
    if not _is_admin(current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    result = await db.execute(
        select(User)
        .where(User.is_active == True)  # noqa: E712
        .options(selectinload(User.roles))
    )
    users = result.scalars().all()
    return [_to_user_response(user) for user in users]


@router.post("/users", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user_admin(
    user_data: schemas.AdminUserCreate,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new user as an admin (active by default)."""
    if not _is_admin(current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")

    result = await db.execute(select(User).where(User.email == user_data.email))
    existing_user = result.scalar_one_or_none()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    role_name = (user_data.role_name or "Analyst").strip()
    role = None
    if role_name:
        role_result = await db.execute(select(Role).where(Role.role_name == role_name))
        role = role_result.scalar_one_or_none()
        if not role:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Role not found")

    new_user = User(
        email=user_data.email,
        password_hash=get_password_hash(user_data.password),
        full_name_en=user_data.full_name_en,
        full_name_ar=user_data.full_name_ar,
        organization_name=user_data.organization_name,
        is_active=user_data.is_active,
        is_verified=user_data.is_verified,
    )
    if role is not None:
        new_user.roles.append(role)

    db.add(new_user)
    await db.flush()

    await db.commit()

    result = await db.execute(
        select(User)
        .where(User.user_id == new_user.user_id)
        .options(selectinload(User.roles))
    )
    user_with_roles = result.scalar_one()

    await log_audit_event(
        db=db,
        user_id=str(current_user.user_id),
        action="create_user",
        resource="users",
        resource_id=str(user_with_roles.user_id),
        status="success",
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        details={"email": user_with_roles.email, "role": role_name},
    )

    return _to_user_response(user_with_roles)


@router.post("/users/{user_id}/roles")
async def assign_roles_to_user(
    user_id: str,
    role_assignment: schemas.UserRoleAssignment,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Assign roles to a user (Admin / super_admin only)."""
    if not _is_admin(current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")    # Fetch user
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


@router.patch("/users/{user_id}")
async def update_user(
    user_id: str,
    user_update: schemas.UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Update user details (Admin / super_admin only)."""
    if not _is_admin(current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    result = await db.execute(select(User).where(User.user_id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Update fields if provided
    update_data = user_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)
    
    await db.commit()
    await db.refresh(user)

    # Eager-load roles before serializing response
    result = await db.execute(
        select(User)
        .where(User.user_id == user.user_id)
        .options(selectinload(User.roles))
    )
    updated_user = result.scalar_one()
    
    # Audit log
    await log_audit_event(
        db=db,
        user_id=str(current_user.user_id),
        action="update_user",
        resource="users",
        resource_id=str(user_id),
        status="success",
        ip_address=None,
        user_agent=None,
        details=update_data
    )
    
    return {
        "message": "User updated successfully",
        "user": _to_user_response(updated_user).model_dump(),
    }


@router.patch("/users/{user_id}/deactivate")
async def deactivate_user(
    user_id: str,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Deactivate a user account (Admin only)."""
    if not _is_admin(current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")

    result = await db.execute(select(User).where(User.user_id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if not bool(getattr(user, "is_active")):
        return {"message": "User already inactive", "user_id": user_id}

    setattr(user, "is_active", False)
    await db.commit()

    await log_audit_event(
        db=db,
        user_id=str(current_user.user_id),
        action="deactivate_user",
        resource="users",
        resource_id=str(user_id),
        status="success",
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )

    return {"message": "User deactivated", "user_id": user_id}


@router.get("/roles", response_model=List[schemas.RoleResponse])
async def list_roles(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """List all roles (Admin / super_admin only)."""
    if not _is_admin(current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    result = await db.execute(select(Role))
    roles = result.scalars().all()
    return roles


@router.get("/admin/stats", response_model=schemas.AdminStatsResponse)
async def get_admin_stats(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Aggregate admin dashboard stats from the database."""
    if not _is_admin(current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")

    total_users = await db.scalar(select(func.count()).select_from(User)) or 0
    active_users = await db.scalar(
        select(func.count()).select_from(User).where(User.is_active == True)  # noqa: E712
    ) or 0
    total_controls = await db.scalar(select(func.count()).select_from(Control)) or 0
    total_evidence = await db.scalar(select(func.count()).select_from(Evidence)) or 0
    total_reports = await db.scalar(select(func.count()).select_from(Report)) or 0

    return schemas.AdminStatsResponse(
        total_users=total_users,
        active_users=active_users,
        total_controls=total_controls,
        total_evidence=total_evidence,
        total_reports=total_reports,
    )


@router.get("/admin/system-status", response_model=schemas.SystemStatusResponse)
async def get_system_status(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Return backend, database, and security subsystem status."""
    if not _is_admin(current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")

    database_ok = True
    database_size_bytes = None
    security_ok = True

    try:
        await db.execute(text("SELECT 1"))
        size_result = await db.execute(text("SELECT pg_database_size(current_database())"))
        database_size_bytes = int(size_result.scalar() or 0)
    except Exception:
        database_ok = False

    try:
        await db.execute(select(func.count()).select_from(AuditLog))
    except Exception:
        security_ok = False

    return schemas.SystemStatusResponse(
        backend_ok=True,
        database_ok=database_ok,
        security_ok=security_ok,
        database_size_bytes=database_size_bytes,
    )


@router.get("/admin/audit-logs", response_model=List[schemas.AuditLogResponse])
async def list_audit_logs(
    limit: int = 50,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """List recent audit log entries (Admin only)."""
    if not _is_admin(current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")

    result = await db.execute(
        select(AuditLog)
        .order_by(AuditLog.timestamp.desc())
        .limit(limit)
    )
    return result.scalars().all()


# ── Registration approval endpoints (SuperAdmin only) ────────────────────────

def _is_admin(user: User) -> bool:
    """Return True if user has Admin or super_admin role."""
    role_names = [r.role_name for r in getattr(user, "roles", [])]
    return bool({"Admin", "admin", "super_admin"} & set(role_names))


def _is_super_admin(user: User) -> bool:
    """Return True if user has SuperAdmin (case variants) or super_admin role."""
    role_names = [r.role_name for r in getattr(user, "roles", [])]
    return bool({"SuperAdmin", "super_admin"} & set(role_names))


@router.get("/pending-registrations", response_model=List[schemas.UserResponse])
async def list_pending_registrations(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Return all users whose accounts are pending admin approval (is_active=False)."""
    if not _is_admin(current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")

    result = await db.execute(
        select(User)
        .where(User.is_active == False)  # noqa: E712
        .options(selectinload(User.roles))
        .order_by(User.created_at.desc())
    )
    pending = result.scalars().all()
    return [_to_user_response(u) for u in pending]


@router.post("/users/{user_id}/approve")
async def approve_registration(
    user_id: str,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Approve a pending registration.
    Sets is_active=True, assigns default Analyst role if no roles, sends email.
    """
    if not _is_admin(current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")

    result = await db.execute(
        select(User)
        .where(User.user_id == user_id)
        .options(selectinload(User.roles))
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if bool(getattr(user, "is_active")):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User is already active")

    # Activate + verify
    setattr(user, "is_active", True)
    setattr(user, "is_verified", True)

    # Assign Analyst role if the user has none
    if not getattr(user, "roles", []):
        role_result = await db.execute(select(Role).where(Role.role_name == "Analyst"))
        analyst_role = role_result.scalar_one_or_none()
        if analyst_role:
            user.roles.append(analyst_role)

    await db.commit()

    # Send approval email (non-blocking — failure is logged but not raised)
    email_addr = str(getattr(user, "email"))
    full_name = str(getattr(user, "full_name_en") or email_addr)
    send_account_approved_email(to_address=email_addr, full_name=full_name)

    await log_audit_event(
        db=db,
        user_id=str(current_user.user_id),
        action="approve_registration",
        resource="users",
        resource_id=str(user_id),
        status="success",
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )

    return {"message": "User approved successfully", "user_id": user_id}


@router.post("/users/{user_id}/deny")
async def deny_registration(
    user_id: str,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Deny a pending registration.
    Deletes the user record and sends a rejection email.
    """
    if not _is_admin(current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")

    result = await db.execute(
        select(User).where(User.user_id == user_id)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if bool(getattr(user, "is_active")):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot deny an already active user")

    email_addr = str(getattr(user, "email"))
    full_name = str(getattr(user, "full_name_en") or email_addr)

    await db.delete(user)
    await db.commit()

    # Send rejection email (non-blocking)
    send_account_denied_email(to_address=email_addr, full_name=full_name)

    await log_audit_event(
        db=db,
        user_id=str(current_user.user_id),
        action="deny_registration",
        resource="users",
        resource_id=str(user_id),
        status="success",
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )

    return {"message": "User denied and removed", "user_id": user_id}


@router.post("/users/{user_id}/reject")
async def reject_registration(
    user_id: str,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Alias for deny_registration to support legacy clients."""
    return await deny_registration(user_id, request, current_user, db)

