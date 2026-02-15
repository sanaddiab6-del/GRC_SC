"""
Authentication models compliant with NCA ECC and PDPL.
Implements secure password storage and token management.
"""
from sqlalchemy import Column, String, Boolean, DateTime, Integer, ForeignKey, Table, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from core.database import Base


# Association tables
user_roles = Table(
    "user_roles",
    Base.metadata,
    Column("user_id", UUID(as_uuid=True), ForeignKey("users.user_id", ondelete="CASCADE"), primary_key=True),
    Column("role_id", UUID(as_uuid=True), ForeignKey("roles.role_id", ondelete="CASCADE"), primary_key=True),
    Column("assigned_at", DateTime, default=datetime.utcnow),
    Column("assigned_by", UUID(as_uuid=True), ForeignKey("users.user_id"))
)

role_permissions = Table(
    "role_permissions",
    Base.metadata,
    Column("role_id", UUID(as_uuid=True), ForeignKey("roles.role_id", ondelete="CASCADE"), primary_key=True),
    Column("permission_id", UUID(as_uuid=True), ForeignKey("permissions.permission_id", ondelete="CASCADE"), primary_key=True)
)


class User(Base):
    """User model with bilingual support and security features."""
    __tablename__ = "users"
    
    user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name_en = Column(String(255))
    full_name_ar = Column(String(255))
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    last_login_at = Column(DateTime)
    failed_login_attempts = Column(Integer, default=0)
    locked_until = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    roles = relationship(
        "Role",
        secondary=user_roles,
        primaryjoin=user_id == user_roles.c.user_id,
        secondaryjoin="Role.role_id == user_roles.c.role_id",
        foreign_keys=[user_roles.c.user_id, user_roles.c.role_id],
        back_populates="users",
    )
    refresh_tokens = relationship("RefreshToken", back_populates="user", cascade="all, delete-orphan")
    # audit_logs relationship available but not actively used


class Role(Base):
    """Role model for RBAC implementation."""
    __tablename__ = "roles"
    
    role_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    role_name = Column(String(50), unique=True, nullable=False)
    description_en = Column(String)
    description_ar = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    users = relationship(
        "User",
        secondary=user_roles,
        primaryjoin=role_id == user_roles.c.role_id,
        secondaryjoin="User.user_id == user_roles.c.user_id",
        foreign_keys=[user_roles.c.role_id, user_roles.c.user_id],
        back_populates="roles",
    )
    permissions = relationship("Permission", secondary="role_permissions", back_populates="roles")


class Permission(Base):
    """Permission model for granular access control."""
    __tablename__ = "permissions"
    
    permission_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    permission_name = Column(String(100), unique=True, nullable=False)
    resource = Column(String(50), nullable=False)  # controls, evidence, reports
    action = Column(String(20), nullable=False)  # create, read, update, delete
    description_en = Column(String)
    description_ar = Column(String)
    
    # Relationships
    roles = relationship("Role", secondary="role_permissions", back_populates="permissions")



class RefreshToken(Base):
    """Refresh token model for secure session management."""
    __tablename__ = "refresh_tokens"
    
    token_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)
    token_hash = Column(String(255), nullable=False)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    revoked_at = Column(DateTime)
    
    # Relationships
    user = relationship("User", back_populates="refresh_tokens")


class APIKey(Base):
    """API Key model for service-to-service authentication."""
    __tablename__ = "api_keys"
    
    api_key_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    key_hash = Column(String(255), nullable=False, unique=True)
    name = Column(String(100), nullable=False)
    description = Column(String)
    scopes = Column(JSON)  # ["controls:read", "evidence:write"]
    expires_at = Column(DateTime)
    last_used_at = Column(DateTime)
    created_by = Column(UUID(as_uuid=True), ForeignKey('users.user_id'))
    created_at = Column(DateTime, default=datetime.utcnow)
    revoked_at = Column(DateTime)

# AuditLog defined in core.audit_logger with extend_existing=True
# Simplified version here for auth module compatibility

class AuditLog(Base):
    """Audit log model for compliance tracking (NCA ECC-IS-5, 7-year retention)."""
    __tablename__ = "audit_logs"
    __table_args__ = {'extend_existing': True}  # Allow redefinition for compatibility
    
    log_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id'), nullable=True)
    action = Column(String(100), nullable=False)
    resource = Column(String(50), nullable=False)
    details = Column(JSON)

