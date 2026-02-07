"""
Database migration: Add authentication and authorization tables.
Implements NCA ECC-IS-3 and PDPL Article 29 requirements.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB
from datetime import datetime


# revision identifiers
revision = '002_auth_system'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade():
    """Create authentication and authorization tables."""
    
    # Users table
    op.create_table(
        'users',
        sa.Column('user_id', UUID(as_uuid=True), primary_key=True),
        sa.Column('email', sa.String(255), unique=True, nullable=False, index=True),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('full_name_en', sa.String(255)),
        sa.Column('full_name_ar', sa.String(255)),
        sa.Column('is_active', sa.Boolean, default=True),
        sa.Column('is_verified', sa.Boolean, default=False),
        sa.Column('last_login_at', sa.DateTime),
        sa.Column('failed_login_attempts', sa.Integer, default=0),
        sa.Column('locked_until', sa.DateTime),
        sa.Column('created_at', sa.DateTime, default=datetime.utcnow),
        sa.Column('updated_at', sa.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    )
    
    # Roles table
    op.create_table(
        'roles',
        sa.Column('role_id', UUID(as_uuid=True), primary_key=True),
        sa.Column('role_name', sa.String(50), unique=True, nullable=False),
        sa.Column('description_en', sa.String),
        sa.Column('description_ar', sa.String),
        sa.Column('created_at', sa.DateTime, default=datetime.utcnow)
    )
    
    # Permissions table
    op.create_table(
        'permissions',
        sa.Column('permission_id', UUID(as_uuid=True), primary_key=True),
        sa.Column('permission_name', sa.String(100), unique=True, nullable=False),
        sa.Column('resource', sa.String(50), nullable=False),
        sa.Column('action', sa.String(20), nullable=False),
        sa.Column('description_en', sa.String),
        sa.Column('description_ar', sa.String)
    )
    
    # User-Role mapping
    op.create_table(
        'user_roles',
        sa.Column('user_id', UUID(as_uuid=True), sa.ForeignKey('users.user_id', ondelete='CASCADE'), primary_key=True),
        sa.Column('role_id', UUID(as_uuid=True), sa.ForeignKey('roles.role_id', ondelete='CASCADE'), primary_key=True),
        sa.Column('assigned_at', sa.DateTime, default=datetime.utcnow),
        sa.Column('assigned_by', UUID(as_uuid=True), sa.ForeignKey('users.user_id'))
    )
    
    # Role-Permission mapping
    op.create_table(
        'role_permissions',
        sa.Column('role_id', UUID(as_uuid=True), sa.ForeignKey('roles.role_id', ondelete='CASCADE'), primary_key=True),
        sa.Column('permission_id', UUID(as_uuid=True), sa.ForeignKey('permissions.permission_id', ondelete='CASCADE'), primary_key=True)
    )
    
    # Refresh tokens table
    op.create_table(
        'refresh_tokens',
        sa.Column('token_id', UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', UUID(as_uuid=True), sa.ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False),
        sa.Column('token_hash', sa.String(255), nullable=False),
        sa.Column('expires_at', sa.DateTime, nullable=False),
        sa.Column('created_at', sa.DateTime, default=datetime.utcnow),
        sa.Column('revoked_at', sa.DateTime)
    )
    
    # API keys table
    op.create_table(
        'api_keys',
        sa.Column('api_key_id', UUID(as_uuid=True), primary_key=True),
        sa.Column('key_hash', sa.String(255), nullable=False, unique=True),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('description', sa.String),
        sa.Column('scopes', JSONB),
        sa.Column('expires_at', sa.DateTime),
        sa.Column('last_used_at', sa.DateTime),
        sa.Column('created_by', UUID(as_uuid=True), sa.ForeignKey('users.user_id')),
        sa.Column('created_at', sa.DateTime, default=datetime.utcnow),
        sa.Column('revoked_at', sa.DateTime)
    )
    
    # Audit logs table (NCA ECC-IS-5, 7-year retention)
    op.create_table(
        'audit_logs',
        sa.Column('log_id', UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', UUID(as_uuid=True), sa.ForeignKey('users.user_id')),
        sa.Column('action', sa.String(100), nullable=False),
        sa.Column('resource', sa.String(50), nullable=False),
        sa.Column('resource_id', sa.String(255)),
        sa.Column('ip_address', sa.String(45)),  # IPv6 support
        sa.Column('user_agent', sa.String(500)),
        sa.Column('status', sa.String(20)),
        sa.Column('details', JSONB),
        sa.Column('created_at', sa.DateTime, default=datetime.utcnow, index=True)
    )
    
    # Create indexes for performance
    op.create_index('idx_audit_logs_user_id', 'audit_logs', ['user_id'])
    op.create_index('idx_audit_logs_resource', 'audit_logs', ['resource'])
    op.create_index('idx_audit_logs_created_at', 'audit_logs', ['created_at'])
    op.create_index('idx_refresh_tokens_user_id', 'refresh_tokens', ['user_id'])
    op.create_index('idx_refresh_tokens_expires_at', 'refresh_tokens', ['expires_at'])


def downgrade():
    """Drop authentication and authorization tables."""
    
    # Drop indexes
    op.drop_index('idx_refresh_tokens_expires_at')
    op.drop_index('idx_refresh_tokens_user_id')
    op.drop_index('idx_audit_logs_created_at')
    op.drop_index('idx_audit_logs_resource')
    op.drop_index('idx_audit_logs_user_id')
    
    # Drop tables (order matters due to foreign keys)
    op.drop_table('audit_logs')
    op.drop_table('api_keys')
    op.drop_table('refresh_tokens')
    op.drop_table('role_permissions')
    op.drop_table('user_roles')
    op.drop_table('permissions')
    op.drop_table('roles')
    op.drop_table('users')
