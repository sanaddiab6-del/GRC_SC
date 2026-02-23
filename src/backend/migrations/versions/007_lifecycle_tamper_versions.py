"""Add lifecycle tracking, evidence tamper protection, and framework version register

Revision ID: 007_lifecycle_tamper_versions
Revises: 006_enhanced_controls
Create Date: 2026-02-23 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '007_lifecycle_tamper_versions'
down_revision = '006_enhanced_controls'
branch_labels = None
depends_on = None


def upgrade():
    # --- controls: lifecycle tracking ---
    op.add_column('controls', sa.Column('lifecycle_updated_at', sa.DateTime(), nullable=True))

    # --- evidence: tamper protection hash ---
    op.add_column('evidence', sa.Column('file_hash', sa.String(length=64), nullable=True))

    # --- framework_versions: regulatory version register ---
    op.create_table(
        'framework_versions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('framework', sa.String(length=20), nullable=False),
        sa.Column('version_number', sa.String(length=50), nullable=False),
        sa.Column('effective_date', sa.Date(), nullable=False),
        sa.Column('is_current', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('description_en', sa.Text(), nullable=True),
        sa.Column('description_ar', sa.Text(), nullable=True),
        sa.Column('changes_summary_en', sa.Text(), nullable=True),
        sa.Column('changes_summary_ar', sa.Text(), nullable=True),
        sa.Column('source_url', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_framework_versions_id', 'framework_versions', ['id'], unique=False)
    op.create_index('ix_framework_versions_framework', 'framework_versions', ['framework'], unique=False)
    op.create_index('ix_framework_versions_is_current', 'framework_versions', ['is_current'], unique=False)


def downgrade():
    op.drop_index('ix_framework_versions_is_current', table_name='framework_versions')
    op.drop_index('ix_framework_versions_framework', table_name='framework_versions')
    op.drop_index('ix_framework_versions_id', table_name='framework_versions')
    op.drop_table('framework_versions')
    op.drop_column('evidence', 'file_hash')
    op.drop_column('controls', 'lifecycle_updated_at')
