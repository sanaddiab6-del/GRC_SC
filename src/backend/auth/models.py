"""
Authentication models compliant with NCA ECC and PDPL.
Implements secure password storage and token management.
"""
from sqlalchemy import Column, String, Boolean, DateTime, Integer, ForeignKey, Table
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from core.database import Base


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
    roles = relationship("Role", secondary="user_roles", back_populates="users")
    refresh_tokens = relationship("RefreshToken", back_populates="user", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="user")


class Role(Base):
    """Role model for RBAC implementation."""
    __tablename__ = "roles"
    
    role_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    role_name = Column(String(50), unique=True, nullable=False)
    description_en = Column(String)
    description_ar = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    users = relationship("User", secondary="user_roles", back_populates="roles")
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


# Association tables
user_roles = Table(
    'user_roles',
    Base.metadata,
    Column('user_id', UUID(as_uuid=True), ForeignKey('users.user_id', ondelete='CASCADE'), primary_key=True),
    Column('role_id', UUID(as_uuid=True), ForeignKey('roles.role_id', ondelete='CASCADE'), primary_key=True),
    Column('assigned_at', DateTime, default=datetime.utcnow),
    Column('assigned_by', UUID(as_uuid=True), ForeignKey('users.user_id'))
)

role_permissions = Table(
    'role_permissions',
    Base.metadata,
    Column('role_id', UUID(as_uuid=True), ForeignKey('roles.role_id', ondelete='CASCADE'), primary_key=True),
    Column('permission_id', UUID(as_uuid=True), ForeignKey('permissions.permission_id', ondelete='CASCADE'), primary_key=True)
)


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
    scopes = Column(JSONB)  # ["controls:read", "evidence:write"]
    expires_at = Column(DateTime)
    last_used_at = Column(DateTime)
    created_by = Column(UUID(as_uuid=True), ForeignKey('users.user_id'))
    created_at = Column(DateTime, default=datetime.utcnow)
    revoked_at = Column(DateTime)


class AuditLog(Base):
    """Audit log model for compliance tracking (NCA ECC-IS-5, 7-year retention)."""
    __tablename__ = "audit_logs"
    
    log_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id'), nullable=True)
    action = Column(String(100), nullable=False)  # login, logout, create, update, delete
    resource = Column(String(50), nullable=False)  # controls, evidence, users
    resource_id = Column(String(255))
    ip_address = Column(String(45))  # IPv6 support
    user_agent = Column(String(500))
    status = Column(String(20))  # success, failure
    details = Column(JSONB)  # Additional context
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    user = relationship("User", back_populates="audit_logs")
