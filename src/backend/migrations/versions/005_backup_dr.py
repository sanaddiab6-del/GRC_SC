"""Add backup and disaster recovery tables

Revision ID: 005_backup_dr
Revises: 004_privacy_data_protection
Create Date: 2024-02-10

Implements NCA ECC-BC-1, ECC-BC-2 requirements
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '005_backup_dr'
down_revision = '007_lifecycle_tamper_versions'
branch_labels = None
depends_on = None


def upgrade():
    # Create backup_jobs table
    op.create_table(
        'backup_jobs',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('job_name', sa.String(), nullable=False),
        sa.Column('job_name_ar', sa.String(), nullable=False),
        sa.Column('backup_type', sa.Enum('full', 'incremental', 'differential', name='backuptype'), nullable=False),
        sa.Column('status', sa.Enum('pending', 'in_progress', 'completed', 'failed', 'archived', name='backupstatus'), nullable=False),
        sa.Column('database_name', sa.String(), nullable=False),
        sa.Column('backup_size_mb', sa.Float(), nullable=True),
        sa.Column('backup_location', sa.String(), nullable=False),
        sa.Column('encrypted', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('encryption_algorithm', sa.String(), nullable=True, server_default='AES-256'),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('duration_seconds', sa.Integer(), nullable=True),
        sa.Column('retention_days', sa.Integer(), nullable=False, server_default='90'),
        sa.Column('expiry_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('backup_metadata', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('created_by', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_backup_jobs_job_name', 'backup_jobs', ['job_name'])
    op.create_index('ix_backup_jobs_status', 'backup_jobs', ['status'])
    op.create_index('ix_backup_jobs_created_at', 'backup_jobs', ['created_at'])
    
    # Create recovery_tests table
    op.create_table(
        'recovery_tests',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('test_name', sa.String(), nullable=False),
        sa.Column('test_name_ar', sa.String(), nullable=False),
        sa.Column('backup_job_id', sa.String(), nullable=False),
        sa.Column('test_type', sa.String(), nullable=False),
        sa.Column('status', sa.Enum('scheduled', 'in_progress', 'successful', 'failed', name='recoverystatus'), nullable=False),
        sa.Column('rto_target_minutes', sa.Integer(), nullable=False),
        sa.Column('rpo_target_minutes', sa.Integer(), nullable=False),
        sa.Column('actual_recovery_minutes', sa.Integer(), nullable=True),
        sa.Column('rto_met', sa.Boolean(), nullable=True),
        sa.Column('rpo_met', sa.Boolean(), nullable=True),
        sa.Column('scheduled_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('success_rate', sa.Float(), nullable=True),
        sa.Column('test_findings', sa.Text(), nullable=True),
        sa.Column('test_findings_ar', sa.Text(), nullable=True),
        sa.Column('corrective_actions', sa.Text(), nullable=True),
        sa.Column('corrective_actions_ar', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('conducted_by', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_recovery_tests_backup_job_id', 'recovery_tests', ['backup_job_id'])
    op.create_index('ix_recovery_tests_scheduled_date', 'recovery_tests', ['scheduled_date'])
    op.create_index('ix_recovery_tests_status', 'recovery_tests', ['status'])
    
    # Create disaster_recovery_plans table
    op.create_table(
        'disaster_recovery_plans',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('plan_name', sa.String(), nullable=False),
        sa.Column('plan_name_ar', sa.String(), nullable=False),
        sa.Column('version', sa.String(), nullable=False),
        sa.Column('scope', sa.Text(), nullable=False),
        sa.Column('scope_ar', sa.Text(), nullable=False),
        sa.Column('overall_rto_hours', sa.Integer(), nullable=False),
        sa.Column('overall_rpo_hours', sa.Integer(), nullable=False),
        sa.Column('critical_systems', postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column('recovery_procedures', postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column('emergency_contacts', postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column('test_frequency_days', sa.Integer(), nullable=False, server_default='90'),
        sa.Column('last_tested', sa.DateTime(timezone=True), nullable=True),
        sa.Column('next_test_due', sa.DateTime(timezone=True), nullable=True),
        sa.Column('approved', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('approved_by', sa.String(), nullable=True),
        sa.Column('approved_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_by', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_dr_plans_active', 'disaster_recovery_plans', ['active'])
    op.create_index('ix_dr_plans_approved', 'disaster_recovery_plans', ['approved'])
    op.create_index('ix_dr_plans_version', 'disaster_recovery_plans', ['version'])


def downgrade():
    # Drop tables
    op.drop_index('ix_dr_plans_version', 'disaster_recovery_plans')
    op.drop_index('ix_dr_plans_approved', 'disaster_recovery_plans')
    op.drop_index('ix_dr_plans_active', 'disaster_recovery_plans')
    op.drop_table('disaster_recovery_plans')
    
    op.drop_index('ix_recovery_tests_status', 'recovery_tests')
    op.drop_index('ix_recovery_tests_scheduled_date', 'recovery_tests')
    op.drop_index('ix_recovery_tests_backup_job_id', 'recovery_tests')
    op.drop_table('recovery_tests')
    
    op.drop_index('ix_backup_jobs_created_at', 'backup_jobs')
    op.drop_index('ix_backup_jobs_status', 'backup_jobs')
    op.drop_index('ix_backup_jobs_job_name', 'backup_jobs')
    op.drop_table('backup_jobs')
    
    # Drop enums
    op.execute('DROP TYPE IF EXISTS backuptype')
    op.execute('DROP TYPE IF EXISTS backupstatus')
    op.execute('DROP TYPE IF EXISTS recoverystatus')
