"""Add authentication and authorization tables

Revision ID: 002_auth_tables
Revises: 001_initial_migration
Create Date: 2026-02-09

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = '002_auth_tables'
down_revision = '001_initial_migration'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create users table
    op.create_table(
        'users',
        sa.Column('user_id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('email', sa.String(255), nullable=False, unique=True, index=True),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('full_name_en', sa.String(255)),
        sa.Column('full_name_ar', sa.String(255)),
        sa.Column('is_active', sa.Boolean, default=True),
        sa.Column('is_verified', sa.Boolean, default=False),
        sa.Column('last_login_at', sa.DateTime),
        sa.Column('failed_login_attempts', sa.Integer, default=0),
        sa.Column('locked_until', sa.DateTime),
        sa.Column('created_at', sa.DateTime, default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, default=sa.func.now(), onupdate=sa.func.now()),
    )
    
    # Create roles table
    op.create_table(
        'roles',
        sa.Column('role_id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('role_name', sa.String(50), nullable=False, unique=True),
        sa.Column('display_name_en', sa.String(100), nullable=False),
        sa.Column('display_name_ar', sa.String(100), nullable=False),
        sa.Column('description_en', sa.String(500)),
        sa.Column('description_ar', sa.String(500)),
        sa.Column('is_system', sa.Boolean, default=False),
        sa.Column('created_at', sa.DateTime, default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, default=sa.func.now(), onupdate=sa.func.now()),
    )
    
    # Create permissions table
    op.create_table(
        'permissions',
        sa.Column('permission_id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('permission_name', sa.String(100), nullable=False, unique=True),
        sa.Column('display_name_en', sa.String(100), nullable=False),
        sa.Column('display_name_ar', sa.String(100), nullable=False),
        sa.Column('resource', sa.String(50), nullable=False),
        sa.Column('action', sa.String(50), nullable=False),
        sa.Column('created_at', sa.DateTime, default=sa.func.now()),
    )
    
    # Create user_roles association table
    op.create_table(
        'user_roles',
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.user_id', ondelete='CASCADE'), primary_key=True),
        sa.Column('role_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('roles.role_id', ondelete='CASCADE'), primary_key=True),
        sa.Column('assigned_at', sa.DateTime, default=sa.func.now()),
        sa.Column('assigned_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.user_id')),
    )
    
    # Create role_permissions association table
    op.create_table(
        'role_permissions',
        sa.Column('role_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('roles.role_id', ondelete='CASCADE'), primary_key=True),
        sa.Column('permission_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('permissions.permission_id', ondelete='CASCADE'), primary_key=True),
    )
    
    # Create refresh_tokens table
    op.create_table(
        'refresh_tokens',
        sa.Column('token_id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False),
        sa.Column('token_hash', sa.String(255), nullable=False, unique=True, index=True),
        sa.Column('expires_at', sa.DateTime, nullable=False),
        sa.Column('is_revoked', sa.Boolean, default=False),
        sa.Column('created_at', sa.DateTime, default=sa.func.now()),
    )
    
    # Create audit_logs table (NCA ECC-IS-5: 7-year retention)
    op.create_table(
        'audit_logs',
        sa.Column('log_id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.user_id'), nullable=True),
        sa.Column('action', sa.String(100), nullable=False, index=True),
        sa.Column('resource', sa.String(100), index=True),
        sa.Column('resource_id', sa.String(100), index=True),
        sa.Column('ip_address', sa.String(50)),
        sa.Column('user_agent', sa.String(500)),
        sa.Column('status', sa.String(20), nullable=False),  # success, failure
        sa.Column('details', sa.JSON),
        sa.Column('timestamp', sa.DateTime, default=sa.func.now(), index=True),
    )
    
    # Create indexes for performance
    op.create_index('idx_users_email', 'users', ['email'])
    op.create_index('idx_audit_logs_timestamp', 'audit_logs', ['timestamp'])
    op.create_index('idx_audit_logs_user_action', 'audit_logs', ['user_id', 'action'])


def downgrade() -> None:
    op.drop_table('audit_logs')
    op.drop_table('refresh_tokens')
    op.drop_table('role_permissions')
    op.drop_table('user_roles')
    op.drop_table('permissions')
    op.drop_table('roles')
    op.drop_table('users')
