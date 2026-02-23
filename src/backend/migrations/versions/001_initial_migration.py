"""Initial migration - create controls, evidence, and reports tables

Revision ID: 001
Revises: 
Create Date: 2026-02-04 14:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create controls table
    op.create_table(
        'controls',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('control_id', sa.String(length=50), nullable=False),
        sa.Column('framework', sa.String(length=10), nullable=False),
        sa.Column('domain', sa.String(length=100), nullable=False),
        sa.Column('title_en', sa.String(length=500), nullable=False),
        sa.Column('title_ar', sa.String(length=500), nullable=False),
        sa.Column('description_en', sa.Text(), nullable=False),
        sa.Column('description_ar', sa.Text(), nullable=False),
        sa.Column('policy_guidance_en', sa.Text(), nullable=True),
        sa.Column('policy_guidance_ar', sa.Text(), nullable=True),
        sa.Column('procedure_guidance_en', sa.Text(), nullable=True),
        sa.Column('procedure_guidance_ar', sa.Text(), nullable=True),
        sa.Column('priority', sa.String(length=20), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=True),
        sa.Column('maturity_level', sa.Integer(), nullable=True),
        sa.Column('evidence_types', sa.JSON(), nullable=True),
        sa.Column('related_controls', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_controls_control_id'), 'controls', ['control_id'], unique=True)
    op.create_index(op.f('ix_controls_framework'), 'controls', ['framework'], unique=False)
    op.create_index(op.f('ix_controls_id'), 'controls', ['id'], unique=False)

    # Create evidence table
    op.create_table(
        'evidence',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('evidence_id', sa.String(length=100), nullable=False),
        sa.Column('control_id', sa.String(length=50), nullable=False),
        sa.Column('evidence_type', sa.String(length=50), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=True),
        sa.Column('title_en', sa.String(length=500), nullable=False),
        sa.Column('title_ar', sa.String(length=500), nullable=False),
        sa.Column('description_en', sa.Text(), nullable=True),
        sa.Column('description_ar', sa.Text(), nullable=True),
        sa.Column('file_path', sa.String(length=1000), nullable=True),
        sa.Column('file_name', sa.String(length=500), nullable=True),
        sa.Column('file_size', sa.Integer(), nullable=True),
        sa.Column('file_format', sa.String(length=50), nullable=True),
        sa.Column('validated_by', sa.String(length=200), nullable=True),
        sa.Column('validated_at', sa.DateTime(), nullable=True),
        sa.Column('validation_notes', sa.Text(), nullable=True),
        sa.Column('collection_date', sa.DateTime(), nullable=True),
        sa.Column('expiry_date', sa.DateTime(), nullable=True),
        sa.Column('retention_period_days', sa.Integer(), nullable=True),
        sa.Column('additional_metadata', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('created_by', sa.String(length=200), nullable=True),
        sa.ForeignKeyConstraint(['control_id'], ['controls.control_id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_evidence_evidence_id'), 'evidence', ['evidence_id'], unique=True)
    op.create_index(op.f('ix_evidence_id'), 'evidence', ['id'], unique=False)

    # Create reports table
    op.create_table(
        'reports',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('report_id', sa.String(length=100), nullable=False),
        sa.Column('report_type', sa.String(length=50), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=True),
        sa.Column('title_en', sa.String(length=500), nullable=False),
        sa.Column('title_ar', sa.String(length=500), nullable=False),
        sa.Column('framework_filter', sa.JSON(), nullable=True),
        sa.Column('date_range_start', sa.DateTime(), nullable=True),
        sa.Column('date_range_end', sa.DateTime(), nullable=True),
        sa.Column('report_data', sa.JSON(), nullable=True),
        sa.Column('file_path', sa.String(length=1000), nullable=True),
        sa.Column('file_format', sa.String(length=50), nullable=True),
        sa.Column('generated_by', sa.String(length=200), nullable=True),
        sa.Column('generated_at', sa.DateTime(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_reports_id'), 'reports', ['id'], unique=False)
    op.create_index(op.f('ix_reports_report_id'), 'reports', ['report_id'], unique=True)


def downgrade() -> None:
    op.drop_index(op.f('ix_reports_report_id'), table_name='reports')
    op.drop_index(op.f('ix_reports_id'), table_name='reports')
    op.drop_table('reports')
    op.drop_index(op.f('ix_evidence_id'), table_name='evidence')
    op.drop_index(op.f('ix_evidence_evidence_id'), table_name='evidence')
    op.drop_table('evidence')
    op.drop_index(op.f('ix_controls_id'), table_name='controls')
    op.drop_index(op.f('ix_controls_framework'), table_name='controls')
    op.drop_index(op.f('ix_controls_control_id'), table_name='controls')
    op.drop_table('controls')
    


