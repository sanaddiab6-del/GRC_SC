"""
Pydantic schemas for authentication and authorization.
"""
from pydantic import BaseModel, EmailStr, Field, ConfigDict, field_validator
from typing import Optional, List
from datetime import datetime
from uuid import UUID
import re


class UserBase(BaseModel):
    """Base user schema."""
    email: EmailStr
    full_name_en: Optional[str] = None
    full_name_ar: Optional[str] = None


class UserCreate(UserBase):
    """Schema for user creation."""
    password: str = Field(..., min_length=12)
    organization_name: Optional[str] = None
    
    @field_validator('password')
    @classmethod
    def password_strength(cls, v: str) -> str:
        """
        Validate password strength (PDPL Article 29 + NCA ECC-IS-3).
        Requirements:
        - Min 12 characters
        - At least 1 uppercase
        - At least 1 lowercase
        - At least 1 digit
        - At least 1 special character
        """
        if len(v) < 12:
            raise ValueError('Password must be at least 12 characters long')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'[0-9]', v):
            raise ValueError('Password must contain at least one digit')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password must contain at least one special character')
        return v


class UserLogin(BaseModel):
    """Schema for user login."""
    email: EmailStr
    password: str


class UserResponse(UserBase):
    """Schema for user response."""
    user_id: UUID
    is_active: bool
    is_verified: bool
    organization_name: Optional[str] = None
    last_login_at: Optional[datetime]
    created_at: datetime
    roles: List[str] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class UserUpdate(BaseModel):
    """Schema for user update (Admin only)."""
    full_name_en: Optional[str] = None
    full_name_ar: Optional[str] = None
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None


class AdminUserCreate(UserCreate):
    """Schema for admin-created users."""
    role_name: Optional[str] = None
    is_active: bool = True
    is_verified: bool = True


class TokenResponse(BaseModel):
    """Schema for token response."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenRefresh(BaseModel):
    """Schema for token refresh request."""
    refresh_token: str


class PasswordReset(BaseModel):
    """Schema for password reset."""
    email: EmailStr


class PasswordChange(BaseModel):
    """Schema for password change."""
    old_password: str
    new_password: str = Field(..., min_length=12)
    
    @field_validator('new_password')
    @classmethod
    def password_strength(cls, v: str) -> str:
        """Validate new password strength."""
        if len(v) < 12:
            raise ValueError('Password must be at least 12 characters long')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'[0-9]', v):
            raise ValueError('Password must contain at least one digit')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password must contain at least one special character')
        return v


class RoleBase(BaseModel):
    """Base role schema."""
    role_name: str
    description_en: Optional[str] = None
    description_ar: Optional[str] = None


class RoleCreate(RoleBase):
    """Schema for role creation."""
    pass


class RoleResponse(RoleBase):
    """Schema for role response."""
    role_id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PermissionBase(BaseModel):
    """Base permission schema."""
    permission_name: str
    resource: str
    action: str
    description_en: Optional[str] = None
    description_ar: Optional[str] = None


class PermissionCreate(PermissionBase):
    """Schema for permission creation."""
    pass


class PermissionResponse(PermissionBase):
    """Schema for permission response."""
    permission_id: UUID

    model_config = ConfigDict(from_attributes=True)


class UserRoleAssignment(BaseModel):
    """Schema for assigning roles to users."""
    user_id: UUID
    role_ids: List[UUID]


class AdminStatsResponse(BaseModel):
    """Aggregated admin dashboard stats."""
    total_users: int
    active_users: int
    total_controls: int
    total_evidence: int
    total_reports: int


class SystemStatusResponse(BaseModel):
    """System status summary for admin dashboard."""
    backend_ok: bool
    database_ok: bool
    security_ok: bool
    database_size_bytes: Optional[int] = None


class AuditLogResponse(BaseModel):
    """Schema for audit log response."""
    log_id: UUID
    user_id: Optional[UUID]
    action: str
    resource: str
    resource_id: Optional[str]
    ip_address: Optional[str]
    status: str
    details: Optional[dict]
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)
