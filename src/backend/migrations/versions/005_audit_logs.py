"""Add audit logs table with cryptographic integrity

Revision ID: 005
Revises: d3a6b7c9e2f4
Create Date: 2026-02-12 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision = '005_audit_logs'
down_revision = 'd3a6b7c9e2f4'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Check if table already exists (idempotent migration)
    conn = op.get_bind()
    inspector = inspect(conn)
    existing_tables = inspector.get_table_names()
    
    if 'audit_logs' in existing_tables:
        print("⚠️ Table 'audit_logs' already exists. Skipping creation.")
        return
    
    # Create audit_logs table
    op.create_table(
        'audit_logs',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False, index=True),
        sa.Column('event_type', sa.String(length=100), nullable=False, index=True),
        
        # Actor information
        sa.Column('user_id', sa.String(length=100), nullable=True, index=True),
        sa.Column('username', sa.String(length=200), nullable=True),
        sa.Column('role', sa.String(length=100), nullable=True),
        sa.Column('tenant_id', sa.String(length=100), nullable=True, index=True),
        
        # Action details
        sa.Column('resource_type', sa.String(length=100), nullable=True, index=True),
        sa.Column('resource_id', sa.String(length=200), nullable=True, index=True),
        sa.Column('action', sa.String(length=50), nullable=True),
        
        # Request context
        sa.Column('ip_address', sa.String(length=50), nullable=True),
        sa.Column('user_agent', sa.String(length=500), nullable=True),
        sa.Column('request_id', sa.String(length=100), nullable=True, index=True),
        
        # Result
        sa.Column('success', sa.Boolean(), nullable=False, default=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        
        # Additional data
        sa.Column('metadata', sa.JSON(), nullable=True),
        
        # Cryptographic integrity
        sa.Column('previous_hash', sa.String(length=64), nullable=True),
        sa.Column('current_hash', sa.String(length=64), nullable=False, index=True),
        
        # Retention (7 years per NCA ECC)
        sa.Column('retention_until', sa.DateTime(), nullable=False),
        sa.Column('is_archived', sa.Boolean(), default=False, index=True),
        
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for common queries
    op.create_index(op.f('ix_audit_logs_timestamp_event'), 'audit_logs', ['timestamp', 'event_type'])
    op.create_index(op.f('ix_audit_logs_user_timestamp'), 'audit_logs', ['user_id', 'timestamp'])
    op.create_index(op.f('ix_audit_logs_resource'), 'audit_logs', ['resource_type', 'resource_id'])


def downgrade() -> None:
    # Check if table exists before dropping
    conn = op.get_bind()
    inspector = inspect(conn)
    existing_tables = inspector.get_table_names()
    
    if 'audit_logs' not in existing_tables:
        print("⚠️ Table 'audit_logs' does not exist. Skipping drop.")
        return
    
    # Drop indexes first
    try:
        op.drop_index(op.f('ix_audit_logs_resource'), table_name='audit_logs')
        op.drop_index(op.f('ix_audit_logs_user_timestamp'), table_name='audit_logs')
        op.drop_index(op.f('ix_audit_logs_timestamp_event'), table_name='audit_logs')
    except Exception as e:
        print(f"⚠️ Error dropping indexes: {e}")
    
    # Drop table
    op.drop_table('audit_logs')
