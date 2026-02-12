"""Enhanced control model with subdomain, source tracking, and cross-framework mappings

Revision ID: 006
Revises: 005
Create Date: 2024-02-12 15:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '006_enhanced_controls'
down_revision = '005_audit_logs'
branch_labels = None
depends_on = None


def upgrade():
    """Add enhanced fields to controls table for official NCA regulatory data"""
    
    # Add new columns for enhanced control structure
    op.add_column('controls', sa.Column('framework_version', sa.String(50), nullable=True))
    op.add_column('controls', sa.Column('subdomain', sa.String(300), nullable=True))
    op.add_column('controls', sa.Column('control_clause_en', sa.Text, nullable=True))
    op.add_column('controls', sa.Column('control_clause_ar', sa.Text, nullable=True))
    op.add_column('controls', sa.Column('evidence_examples', sa.Text, nullable=True))
    
    # Add source tracking columns
    op.add_column('controls', sa.Column('source_pdf', sa.String(200), nullable=True))
    op.add_column('controls', sa.Column('source_page', sa.Integer, nullable=True))
    
    # Add cross-framework mapping columns
    op.add_column('controls', sa.Column('mapping_ecc', sa.String(500), nullable=True))
    op.add_column('controls', sa.Column('mapping_ccc', sa.String(500), nullable=True))
    op.add_column('controls', sa.Column('mapping_pdpl', sa.String(500), nullable=True))
    op.add_column('controls', sa.Column('mapping_dcc', sa.String(500), nullable=True))
    
    # Make description fields nullable (control_clause is the primary field)
    op.alter_column('controls', 'description_en', nullable=True)
    op.alter_column('controls', 'description_ar', nullable=True)
    
    # Update domain column length to match official NCA structure
    op.alter_column('controls', 'domain', type_=sa.String(200))
    
    # Create indexes for performance
    op.create_index('ix_controls_subdomain', 'controls', ['subdomain'])
    op.create_index('ix_controls_framework_version', 'controls', ['framework_version'])
    op.create_index('ix_controls_source_pdf', 'controls', ['source_pdf'])


def downgrade():
    """Revert enhanced control fields"""
    
    # Drop indexes
    op.drop_index('ix_controls_source_pdf', 'controls')
    op.drop_index('ix_controls_framework_version', 'controls')
    op.drop_index('ix_controls_subdomain', 'controls')
    
    # Revert domain column length
    op.alter_column('controls', 'domain', type_=sa.String(100))
    
    # Make description fields required again
    op.alter_column('controls', 'description_ar', nullable=False)
    op.alter_column('controls', 'description_en', nullable=False)
    
    # Drop cross-framework mapping columns
    op.drop_column('controls', 'mapping_dcc')
    op.drop_column('controls', 'mapping_pdpl')
    op.drop_column('controls', 'mapping_ccc')
    op.drop_column('controls', 'mapping_ecc')
    
    # Drop source tracking columns
    op.drop_column('controls', 'source_page')
    op.drop_column('controls', 'source_pdf')
    
    # Drop enhanced structure columns
    op.drop_column('controls', 'evidence_examples')
    op.drop_column('controls', 'control_clause_ar')
    op.drop_column('controls', 'control_clause_en')
    op.drop_column('controls', 'subdomain')
    op.drop_column('controls', 'framework_version')
