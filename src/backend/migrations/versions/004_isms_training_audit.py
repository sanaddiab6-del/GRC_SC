"""
Phase 2.4 Database Migration: ISMS, Training & Audit Management

Creates tables for:
- ISMS Policy Management (ISO 27001 A.5)
- Security Training & Awareness (ISO 27001 A.6.3)
- External Audit Management (ISO 27001 Clause 9.2)

Revision ID: 004_isms_training_audit
Revises: c1f0b0a7d5e1
Create Date: 2026-02-09
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import uuid

# revision identifiers
revision = '004_isms_training_audit'
down_revision = 'c1f0b0a7d5e1'
branch_labels = None
depends_on = None

class GUID(sa.TypeDecorator):
    """Platform-independent GUID type."""
    impl = sa.CHAR
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(postgresql.UUID())
        else:
            return dialect.type_descriptor(sa.CHAR(32))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return str(value)
        else:
            if isinstance(value, uuid.UUID):
                return "%.32x" % value.int
            else:
                return "%.32x" % uuid.UUID(value).int

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        else:
            if not isinstance(value, uuid.UUID):
                value = uuid.UUID(value)
            return value

def upgrade():
    """Create Phase 2.4 tables"""
    
    # ============================================================================
    # ISMS POLICY MANAGEMENT TABLES
    # ============================================================================
    
    # ISMSPolicy table
    op.create_table(
        'isms_policies',
        sa.Column('policy_id', sa.Integer(), nullable=False),
        sa.Column('policy_number', sa.String(50), nullable=False),
        sa.Column('policy_type', sa.String(50), nullable=False),
        sa.Column('title_en', sa.String(500), nullable=False),
        sa.Column('title_ar', sa.String(500), nullable=False),
        sa.Column('purpose_en', sa.Text(), nullable=False),
        sa.Column('purpose_ar', sa.Text(), nullable=False),
        sa.Column('scope_en', sa.Text(), nullable=False),
        sa.Column('scope_ar', sa.Text(), nullable=False),
        sa.Column('policy_statement_en', sa.Text(), nullable=False),
        sa.Column('policy_statement_ar', sa.Text(), nullable=False),
        sa.Column('version', sa.String(20), nullable=False, default='1.0'),
        sa.Column('status', sa.String(50), nullable=False, default='draft'),
        sa.Column('classification', sa.String(50), nullable=False, default='internal'),
        sa.Column('author_id', GUID(), nullable=False),
        sa.Column('reviewer_id', GUID(), nullable=True),
        sa.Column('approver_id', GUID(), nullable=True),
        sa.Column('draft_date', sa.DateTime(), nullable=False),
        sa.Column('review_date', sa.DateTime(), nullable=True),
        sa.Column('approval_date', sa.DateTime(), nullable=True),
        sa.Column('publication_date', sa.DateTime(), nullable=True),
        sa.Column('effective_date', sa.DateTime(), nullable=True),
        sa.Column('review_frequency_days', sa.Integer(), nullable=False, default=365),
        sa.Column('next_review_date', sa.DateTime(), nullable=True),
        sa.Column('expiry_date', sa.DateTime(), nullable=True),
        sa.Column('iso27001_controls', sa.JSON(), nullable=True),
        sa.Column('nca_ecc_controls', sa.JSON(), nullable=True),
        sa.Column('nca_ccc_controls', sa.JSON(), nullable=True),
        sa.Column('pdpl_articles', sa.JSON(), nullable=True),
        sa.Column('nist_csf_functions', sa.JSON(), nullable=True),
        sa.Column('related_procedures', sa.JSON(), nullable=True),
        sa.Column('related_policies', sa.JSON(), nullable=True),
        sa.Column('related_controls', sa.JSON(), nullable=True),
        sa.Column('tags', sa.JSON(), nullable=True),
        sa.Column('keywords_en', sa.Text(), nullable=True),
        sa.Column('keywords_ar', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['author_id'], ['users.user_id']),
        sa.ForeignKeyConstraint(['reviewer_id'], ['users.user_id']),
        sa.ForeignKeyConstraint(['approver_id'], ['users.user_id']),
        sa.PrimaryKeyConstraint('policy_id')
    )
    op.create_index('ix_isms_policies_policy_id', 'isms_policies', ['policy_id'])
    op.create_index('ix_isms_policies_policy_number', 'isms_policies', ['policy_number'], unique=True)
    op.create_index('ix_isms_policies_status', 'isms_policies', ['status'])
    op.create_index('ix_isms_policies_policy_type', 'isms_policies', ['policy_type'])
    
    # PolicyAcknowledgement table
    op.create_table(
        'policy_acknowledgements',
        sa.Column('acknowledgement_id', sa.Integer(), nullable=False),
        sa.Column('policy_id', sa.Integer(), nullable=False),
        sa.Column('user_id', GUID(), nullable=False),
        sa.Column('policy_version', sa.String(20), nullable=False),
        sa.Column('acknowledged_at', sa.DateTime(), nullable=False),
        sa.Column('acknowledgement_method', sa.String(50), nullable=False),
        sa.Column('ip_address', sa.String(50), nullable=True),
        sa.Column('user_agent', sa.String(500), nullable=True),
        sa.Column('confirmation_text_shown_en', sa.Text(), nullable=True),
        sa.Column('confirmation_text_shown_ar', sa.Text(), nullable=True),
        sa.Column('user_confirmed', sa.Boolean(), nullable=False, default=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['policy_id'], ['isms_policies.policy_id']),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id']),
        sa.PrimaryKeyConstraint('acknowledgement_id')
    )
    op.create_index('ix_policy_acks_policy_id', 'policy_acknowledgements', ['policy_id'])
    op.create_index('ix_policy_acks_user_id', 'policy_acknowledgements', ['user_id'])
    
    # PolicyException table
    op.create_table(
        'policy_exceptions',
        sa.Column('exception_id', sa.Integer(), nullable=False),
        sa.Column('exception_number', sa.String(50), nullable=False),
        sa.Column('policy_id', sa.Integer(), nullable=False),
        sa.Column('title_en', sa.String(500), nullable=False),
        sa.Column('title_ar', sa.String(500), nullable=False),
        sa.Column('justification_en', sa.Text(), nullable=False),
        sa.Column('justification_ar', sa.Text(), nullable=False),
        sa.Column('compensating_controls_en', sa.Text(), nullable=False),
        sa.Column('compensating_controls_ar', sa.Text(), nullable=False),
        sa.Column('risk_acceptance_en', sa.Text(), nullable=False),
        sa.Column('risk_acceptance_ar', sa.Text(), nullable=False),
        sa.Column('requested_by_id', GUID(), nullable=False),
        sa.Column('approved_by_id', GUID(), nullable=True),
        sa.Column('status', sa.String(50), nullable=False, default='pending'),
        sa.Column('requested_date', sa.DateTime(), nullable=False),
        sa.Column('approval_date', sa.DateTime(), nullable=True),
        sa.Column('effective_date', sa.DateTime(), nullable=True),
        sa.Column('expiry_date', sa.DateTime(), nullable=False),
        sa.Column('review_date', sa.DateTime(), nullable=True),
        sa.Column('residual_risk_score', sa.Integer(), nullable=True),
        sa.Column('risk_owner_id', GUID(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['policy_id'], ['isms_policies.policy_id']),
        sa.ForeignKeyConstraint(['requested_by_id'], ['users.user_id']),
        sa.ForeignKeyConstraint(['approved_by_id'], ['users.user_id']),
        sa.ForeignKeyConstraint(['risk_owner_id'], ['users.user_id']),
        sa.PrimaryKeyConstraint('exception_id')
    )
    op.create_index('ix_policy_exceptions_exception_number', 'policy_exceptions', ['exception_number'], unique=True)
    op.create_index('ix_policy_exceptions_status', 'policy_exceptions', ['status'])
    
    # DocumentVersion table
    op.create_table(
        'document_versions',
        sa.Column('version_id', sa.Integer(), nullable=False),
        sa.Column('policy_id', sa.Integer(), nullable=False),
        sa.Column('version_number', sa.String(20), nullable=False),
        sa.Column('change_summary_en', sa.Text(), nullable=False),
        sa.Column('change_summary_ar', sa.Text(), nullable=False),
        sa.Column('change_type', sa.String(50), nullable=False),
        sa.Column('changed_by_id', GUID(), nullable=False),
        sa.Column('document_content_json', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('superseded_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['policy_id'], ['isms_policies.policy_id']),
        sa.ForeignKeyConstraint(['changed_by_id'], ['users.user_id']),
        sa.PrimaryKeyConstraint('version_id')
    )
    op.create_index('ix_doc_versions_policy_id', 'document_versions', ['policy_id'])
    
    # AssetInventory table
    op.create_table(
        'asset_inventory',
        sa.Column('asset_id', sa.Integer(), nullable=False),
        sa.Column('asset_number', sa.String(50), nullable=False),
        sa.Column('asset_name_en', sa.String(500), nullable=False),
        sa.Column('asset_name_ar', sa.String(500), nullable=False),
        sa.Column('description_en', sa.Text(), nullable=True),
        sa.Column('description_ar', sa.Text(), nullable=True),
        sa.Column('asset_type', sa.String(100), nullable=False),
        sa.Column('asset_category', sa.String(100), nullable=False),
        sa.Column('classification', sa.String(50), nullable=False, default='internal'),
        sa.Column('confidentiality_rating', sa.Integer(), nullable=False, default=3),
        sa.Column('integrity_rating', sa.Integer(), nullable=False, default=3),
        sa.Column('availability_rating', sa.Integer(), nullable=False, default=3),
        sa.Column('owner_id', GUID(), nullable=False),
        sa.Column('custodian_id', GUID(), nullable=True),
        sa.Column('location', sa.String(500), nullable=True),
        sa.Column('ip_address', sa.String(50), nullable=True),
        sa.Column('hostname', sa.String(200), nullable=True),
        sa.Column('operating_system', sa.String(200), nullable=True),
        sa.Column('software_version', sa.String(100), nullable=True),
        sa.Column('is_in_scope_iso27001', sa.Boolean(), nullable=False, default=True),
        sa.Column('is_in_scope_pdpl', sa.Boolean(), nullable=False, default=False),
        sa.Column('is_in_scope_ecc', sa.Boolean(), nullable=False, default=True),
        sa.Column('processes_personal_data', sa.Boolean(), nullable=False, default=False),
        sa.Column('acquisition_date', sa.DateTime(), nullable=True),
        sa.Column('last_review_date', sa.DateTime(), nullable=True),
        sa.Column('next_review_date', sa.DateTime(), nullable=True),
        sa.Column('disposal_date', sa.DateTime(), nullable=True),
        sa.Column('risk_score', sa.Integer(), nullable=True),
        sa.Column('vulnerabilities_found', sa.Integer(), nullable=False, default=0),
        sa.Column('tags', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['owner_id'], ['users.user_id']),
        sa.ForeignKeyConstraint(['custodian_id'], ['users.user_id']),
        sa.PrimaryKeyConstraint('asset_id')
    )
    op.create_index('ix_asset_inventory_asset_number', 'asset_inventory', ['asset_number'], unique=True)
    op.create_index('ix_asset_inventory_asset_type', 'asset_inventory', ['asset_type'])
    op.create_index('ix_asset_inventory_classification', 'asset_inventory', ['classification'])

    # AuditEngagement table
    op.create_table(
        'audit_engagements',
        sa.Column('engagement_id', sa.Integer(), nullable=False),
        sa.Column('engagement_code', sa.String(50), nullable=False),
        sa.Column('program_id', sa.Integer(), nullable=False),
        sa.Column('title_en', sa.String(500), nullable=False),
        sa.Column('title_ar', sa.String(500), nullable=False),
        sa.Column('status', sa.String(50), nullable=False, default='planned'),
        sa.Column('lead_auditor_id', GUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['lead_auditor_id'], ['users.user_id']),
        sa.PrimaryKeyConstraint('engagement_id')
    )

    # AuditEvidence table
    op.create_table(
        'audit_evidence',
        sa.Column('evidence_id', sa.Integer(), nullable=False),
        sa.Column('evidence_reference', sa.String(100), nullable=False),
        sa.Column('engagement_id', sa.Integer(), nullable=False),
        sa.Column('requested_by_id', GUID(), nullable=False),
        sa.Column('provided_by_id', GUID(), nullable=True),
        sa.Column('status', sa.String(50), nullable=False, default='pending'),
        sa.Column('reviewed_by_id', GUID(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['engagement_id'], ['audit_engagements.engagement_id']),
        sa.ForeignKeyConstraint(['requested_by_id'], ['users.user_id']),
        sa.ForeignKeyConstraint(['provided_by_id'], ['users.user_id']),
        sa.ForeignKeyConstraint(['reviewed_by_id'], ['users.user_id']),
        sa.PrimaryKeyConstraint('evidence_id')
    )

    # AuditFinding table
    op.create_table(
        'audit_findings',
        sa.Column('finding_id', sa.Integer(), nullable=False),
        sa.Column('finding_number', sa.String(100), nullable=False),
        sa.Column('title_en', sa.String(500), nullable=False),
        sa.Column('title_ar', sa.String(500), nullable=False),
        sa.Column('severity', sa.String(50), nullable=False),
        sa.Column('status', sa.String(50), nullable=False, default='open'),
        sa.Column('owner_id', GUID(), nullable=False),
        sa.Column('responsible_person_id', GUID(), nullable=True),
        sa.Column('verified_by_id', GUID(), nullable=True),
        sa.Column('escalated_to_id', GUID(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['owner_id'], ['users.user_id']),
        sa.ForeignKeyConstraint(['responsible_person_id'], ['users.user_id']),
        sa.ForeignKeyConstraint(['verified_by_id'], ['users.user_id']),
        sa.ForeignKeyConstraint(['escalated_to_id'], ['users.user_id']),
        sa.PrimaryKeyConstraint('finding_id')
    )

    # CorrectiveAction table
    op.create_table(
        'corrective_actions',
        sa.Column('action_id', sa.Integer(), nullable=False),
        sa.Column('finding_id', sa.Integer(), nullable=False),
        sa.Column('action_number', sa.String(100), nullable=False),
        sa.Column('title_en', sa.String(500), nullable=False),
        sa.Column('title_ar', sa.String(500), nullable=False),
        sa.Column('owner_id', GUID(), nullable=False),
        sa.Column('status', sa.String(50), nullable=False, default='planned'),
        sa.Column('verified_by_id', GUID(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['finding_id'], ['audit_findings.finding_id']),
        sa.ForeignKeyConstraint(['owner_id'], ['users.user_id']),
        sa.ForeignKeyConstraint(['verified_by_id'], ['users.user_id']),
        sa.PrimaryKeyConstraint('action_id')
    )

def downgrade():
    """Drop Phase 2.4 tables"""
    op.drop_table('corrective_actions')
    op.drop_table('audit_findings')
    op.drop_table('audit_evidence')
    op.drop_table('audit_engagements')
    op.drop_table('asset_inventory')
    op.drop_table('document_versions')
    op.drop_table('policy_exceptions')
    op.drop_table('policy_acknowledgements')
    op.drop_table('isms_policies')
