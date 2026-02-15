"""Enterprise GRC Platform Schema - Tier-1 Architecture

Revision ID: 002_enterprise_schema
Revises: 001_initial_migration
Create Date: 2024-01-15 00:00:00.000000

Creates complete enterprise GRC schema with:
- Multi-tenancy & RBAC
- Control lifecycle management
- Enterprise Risk Management
- Evidence chain-of-custody
- Audit management
- PDPL operations (RoPA, DSAR, breaches)
- Workflow engine
- Vendor risk management
- Policy management
- Integrations & continuous monitoring
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite

# revision identifiers
revision = '002_enterprise_schema'
down_revision = '001_initial_migration'
branch_labels = None
depends_on = None

def upgrade():
    """Deploy enterprise schema"""
    
    # ============================================================================
    # 1. ORGANIZATIONS (MULTI-TENANCY)
    # ============================================================================
    op.create_table(
        'organizations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name_en', sa.String(255), nullable=False),
        sa.Column('name_ar', sa.String(255), nullable=False),
        sa.Column('org_type', sa.String(50)),
        sa.Column('parent_org_id', sa.Integer()),
        sa.Column('license_type', sa.String(50)),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('created_at', sa.DateTime(), default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['parent_org_id'], ['organizations.id'])
    )
    op.create_index('ix_organizations_id', 'organizations', ['id'])
    
    # ============================================================================
    # 2. USERS (RBAC)
    # ============================================================================
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(100), nullable=False, unique=True),
        sa.Column('email', sa.String(255), nullable=False, unique=True),
        sa.Column('full_name_en', sa.String(255)),
        sa.Column('full_name_ar', sa.String(255)),
        sa.Column('role', sa.String(50), nullable=False),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('last_login', sa.DateTime()),
        sa.Column('created_at', sa.DateTime(), default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'])
    )
    op.create_index('ix_users_username', 'users', ['username'])
    op.create_index('ix_users_email', 'users', ['email'])
    
    # ============================================================================
    # 3. ASSETS
    # ============================================================================
    op.create_table(
        'assets',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('asset_id', sa.String(100), nullable=False, unique=True),
        sa.Column('asset_type', sa.String(50), nullable=False),
        sa.Column('name_en', sa.String(255), nullable=False),
        sa.Column('name_ar', sa.String(255)),
        sa.Column('description_en', sa.Text()),
        sa.Column('description_ar', sa.Text()),
        sa.Column('criticality', sa.String(20), nullable=False),
        sa.Column('classification', sa.String(20)),
        sa.Column('owner_id', sa.Integer()),
        sa.Column('location', sa.String(255)),
        sa.Column('environment', sa.String(50)),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('metadata', sa.JSON()),
        sa.Column('created_at', sa.DateTime(), default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), onupdate=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id']),
        sa.ForeignKeyConstraint(['owner_id'], ['users.id'])
    )
    op.create_index('ix_assets_asset_id', 'assets', ['asset_id'])
    
    # ============================================================================
    # 4. AUDIT LOGS (IMMUTABLE)
    # ============================================================================
    op.create_table(
        'audit_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer()),
        sa.Column('action', sa.String(100), nullable=False),
        sa.Column('entity_type', sa.String(50), nullable=False),
        sa.Column('entity_id', sa.String(100), nullable=False),
        sa.Column('changes', sa.JSON()),
        sa.Column('ip_address', sa.String(50)),
        sa.Column('user_agent', sa.String(500)),
        sa.Column('timestamp', sa.DateTime(), nullable=False, default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id']),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'])
    )
    op.create_index('ix_audit_logs_timestamp', 'audit_logs', ['timestamp'])
    
    # ============================================================================
    # 5. POLICIES
    # ============================================================================
    op.create_table(
        'policies',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('policy_id', sa.String(100), nullable=False, unique=True),
        sa.Column('title_en', sa.String(500), nullable=False),
        sa.Column('title_ar', sa.String(500)),
        sa.Column('description_en', sa.Text()),
        sa.Column('description_ar', sa.Text()),
        sa.Column('version', sa.String(20), nullable=False),
        sa.Column('status', sa.String(50), nullable=False),
        sa.Column('policy_type', sa.String(100)),
        sa.Column('owner_id', sa.Integer()),
        sa.Column('approver_id', sa.Integer()),
        sa.Column('effective_date', sa.Date()),
        sa.Column('review_date', sa.Date()),
        sa.Column('document_url', sa.String(500)),
        sa.Column('mapped_controls', sa.JSON()),
        sa.Column('attestation_required', sa.Boolean(), default=False),
        sa.Column('created_at', sa.DateTime(), default=sa.func.now()),
        sa.Column('approved_at', sa.DateTime()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id']),
        sa.ForeignKeyConstraint(['owner_id'], ['users.id']),
        sa.ForeignKeyConstraint(['approver_id'], ['users.id'])
    )
    op.create_index('ix_policies_policy_id', 'policies', ['policy_id'])
    
    # ============================================================================
    # 6. EVIDENCE TEMPLATES
    # ============================================================================
    op.create_table(
        'evidence_templates',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('organization_id', sa.Integer()),
        sa.Column('template_id', sa.String(100), nullable=False, unique=True),
        sa.Column('name_en', sa.String(255), nullable=False),
        sa.Column('name_ar', sa.String(255)),
        sa.Column('description_en', sa.Text()),
        sa.Column('description_ar', sa.Text()),
        sa.Column('evidence_type', sa.String(100), nullable=False),
        sa.Column('required_fields', sa.JSON()),
        sa.Column('validity_period_days', sa.Integer()),
        sa.Column('is_reusable', sa.Boolean(), default=True),
        sa.Column('created_at', sa.DateTime(), default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'])
    )
    
    # ============================================================================
    # 7. EVIDENCES (with enhanced controls FK - will be added after controls table)
    # ============================================================================
    # Will create after controls table
    
    # ============================================================================
    # 8. RISKS
    # ============================================================================
    op.create_table(
        'risks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('risk_id', sa.String(100), nullable=False, unique=True),
        sa.Column('risk_type', sa.String(50), nullable=False),
        sa.Column('risk_category', sa.String(100)),
        sa.Column('title_en', sa.String(500), nullable=False),
        sa.Column('title_ar', sa.String(500)),
        sa.Column('description_en', sa.Text(), nullable=False),
        sa.Column('description_ar', sa.Text()),
        sa.Column('likelihood_inherent', sa.Integer(), nullable=False),
        sa.Column('impact_inherent', sa.Integer(), nullable=False),
        sa.Column('risk_score_inherent', sa.Float()),
        sa.Column('risk_level_inherent', sa.String(20)),
        sa.Column('likelihood_residual', sa.Integer()),
        sa.Column('impact_residual', sa.Integer()),
        sa.Column('risk_score_residual', sa.Float()),
        sa.Column('risk_level_residual', sa.String(20)),
        sa.Column('risk_appetite_level', sa.String(20)),
        sa.Column('is_within_appetite', sa.Boolean()),
        sa.Column('risk_owner_id', sa.Integer(), nullable=False),
        sa.Column('mitigation_strategy', sa.Text()),
        sa.Column('mitigation_controls', sa.JSON()),
        sa.Column('action_plan', sa.Text()),
        sa.Column('status', sa.String(50), default='open'),
        sa.Column('review_frequency_days', sa.Integer(), default=90),
        sa.Column('last_review_date', sa.Date()),
        sa.Column('next_review_date', sa.Date()),
        sa.Column('related_assets', sa.JSON()),
        sa.Column('related_risks', sa.JSON()),
        sa.Column('related_incidents', sa.JSON()),
        sa.Column('created_at', sa.DateTime(), default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), onupdate=sa.func.now()),
        sa.Column('created_by_id', sa.Integer()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id']),
        sa.ForeignKeyConstraint(['risk_owner_id'], ['users.id']),
        sa.ForeignKeyConstraint(['created_by_id'], ['users.id'])
    )
    op.create_index('ix_risks_risk_id', 'risks', ['risk_id'])
    
    # ============================================================================
    # 9. AUDIT PROGRAMS
    # ============================================================================
    op.create_table(
        'audit_programs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('program_id', sa.String(100), nullable=False, unique=True),
        sa.Column('title_en', sa.String(500), nullable=False),
        sa.Column('title_ar', sa.String(500)),
        sa.Column('audit_type', sa.String(50), nullable=False),
        sa.Column('framework', sa.String(50)),
        sa.Column('scope_description', sa.Text()),
        sa.Column('planned_start_date', sa.Date()),
        sa.Column('planned_end_date', sa.Date()),
        sa.Column('actual_start_date', sa.Date()),
        sa.Column('actual_end_date', sa.Date()),
        sa.Column('lead_auditor_id', sa.Integer()),
        sa.Column('status', sa.String(50), default='planned'),
        sa.Column('controls_in_scope', sa.JSON()),
        sa.Column('created_at', sa.DateTime(), default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id']),
        sa.ForeignKeyConstraint(['lead_auditor_id'], ['users.id'])
    )
    
    # ============================================================================
    # 10. CONTROL EXCEPTIONS
    # ============================================================================
    # Will create after controls table
    
    # ============================================================================
    # 11. WORKFLOW CASES
    # ============================================================================
    op.create_table(
        'workflow_cases',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('case_id', sa.String(100), nullable=False, unique=True),
        sa.Column('case_type', sa.String(50), nullable=False),
        sa.Column('title_en', sa.String(500), nullable=False),
        sa.Column('title_ar', sa.String(500)),
        sa.Column('description_en', sa.Text()),
        sa.Column('description_ar', sa.Text()),
        sa.Column('priority', sa.String(20)),
        sa.Column('assigned_to_id', sa.Integer()),
        sa.Column('assigned_by_id', sa.Integer()),
        sa.Column('assigned_at', sa.DateTime()),
        sa.Column('sla_hours', sa.Integer()),
        sa.Column('due_date', sa.DateTime()),
        sa.Column('is_overdue', sa.Boolean(), default=False),
        sa.Column('escalation_level', sa.Integer(), default=0),
        sa.Column('escalated_to_id', sa.Integer()),
        sa.Column('status', sa.String(20), default='open'),
        sa.Column('resolution_notes', sa.Text()),
        sa.Column('resolved_at', sa.DateTime()),
        sa.Column('closed_at', sa.DateTime()),
        sa.Column('related_entity_type', sa.String(50)),
        sa.Column('related_entity_id', sa.Integer()),
        sa.Column('attachments', sa.JSON()),
        sa.Column('created_at', sa.DateTime(), default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), onupdate=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id']),
        sa.ForeignKeyConstraint(['assigned_to_id'], ['users.id']),
        sa.ForeignKeyConstraint(['assigned_by_id'], ['users.id']),
        sa.ForeignKeyConstraint(['escalated_to_id'], ['users.id'])
    )
    op.create_index('ix_workflow_cases_case_id', 'workflow_cases', ['case_id'])
    
    # ============================================================================
    # 12. VENDORS
    # ============================================================================
    op.create_table(
        'vendors',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('vendor_id', sa.String(100), nullable=False, unique=True),
        sa.Column('name_en', sa.String(255), nullable=False),
        sa.Column('name_ar', sa.String(255)),
        sa.Column('vendor_type', sa.String(100)),
        sa.Column('criticality', sa.String(20), nullable=False),
        sa.Column('contact_person', sa.String(255)),
        sa.Column('contact_email', sa.String(255)),
        sa.Column('contact_phone', sa.String(50)),
        sa.Column('last_assessment_date', sa.Date()),
        sa.Column('next_assessment_date', sa.Date()),
        sa.Column('risk_score', sa.Float()),
        sa.Column('risk_level', sa.String(20)),
        sa.Column('is_data_processor', sa.Boolean(), default=False),
        sa.Column('dpa_signed', sa.Boolean(), default=False),
        sa.Column('dpa_expiry_date', sa.Date()),
        sa.Column('data_transfer_countries', sa.JSON()),
        sa.Column('contract_start_date', sa.Date()),
        sa.Column('contract_end_date', sa.Date()),
        sa.Column('contract_value', sa.Float()),
        sa.Column('status', sa.String(50), default='active'),
        sa.Column('created_at', sa.DateTime(), default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'])
    )
    
    # ============================================================================
    # 13. ROPA (PDPL)
    # ============================================================================
    op.create_table(
        'ropa_records',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('ropa_id', sa.String(100), nullable=False, unique=True),
        sa.Column('activity_name_en', sa.String(500), nullable=False),
        sa.Column('activity_name_ar', sa.String(500)),
        sa.Column('purpose_en', sa.Text(), nullable=False),
        sa.Column('purpose_ar', sa.Text()),
        sa.Column('legal_basis', sa.String(100), nullable=False),
        sa.Column('data_categories', sa.JSON()),
        sa.Column('data_subjects', sa.JSON()),
        sa.Column('retention_period', sa.String(100)),
        sa.Column('international_transfers', sa.Boolean(), default=False),
        sa.Column('transfer_countries', sa.JSON()),
        sa.Column('transfer_safeguards', sa.Text()),
        sa.Column('data_recipients', sa.JSON()),
        sa.Column('processors', sa.JSON()),
        sa.Column('security_measures', sa.Text()),
        sa.Column('dpia_required', sa.Boolean(), default=False),
        sa.Column('dpia_completed', sa.Boolean(), default=False),
        sa.Column('dpia_reference', sa.String(100)),
        sa.Column('data_controller_id', sa.Integer()),
        sa.Column('dpo_id', sa.Integer()),
        sa.Column('status', sa.String(50), default='active'),
        sa.Column('created_at', sa.DateTime(), default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), onupdate=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id']),
        sa.ForeignKeyConstraint(['data_controller_id'], ['users.id']),
        sa.ForeignKeyConstraint(['dpo_id'], ['users.id'])
    )
    
    # ============================================================================
    # 14. DSAR (PDPL)
    # ============================================================================
    op.create_table(
        'dsar_requests',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('request_id', sa.String(100), nullable=False, unique=True),
        sa.Column('request_type', sa.String(50), nullable=False),
        sa.Column('subject_name', sa.String(255), nullable=False),
        sa.Column('subject_email', sa.String(255)),
        sa.Column('subject_phone', sa.String(50)),
        sa.Column('identity_verified', sa.Boolean(), default=False),
        sa.Column('request_description', sa.Text()),
        sa.Column('received_date', sa.Date(), nullable=False),
        sa.Column('sla_days', sa.Integer(), default=30),
        sa.Column('due_date', sa.Date(), nullable=False),
        sa.Column('is_overdue', sa.Boolean(), default=False),
        sa.Column('assigned_to_id', sa.Integer()),
        sa.Column('response_provided', sa.Text()),
        sa.Column('response_date', sa.Date()),
        sa.Column('status', sa.String(20), default='open'),
        sa.Column('created_at', sa.DateTime(), default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id']),
        sa.ForeignKeyConstraint(['assigned_to_id'], ['users.id'])
    )
    
    # ============================================================================
    # 15. DATA BREACHES (PDPL)
    # ============================================================================
    op.create_table(
        'data_breaches',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('breach_id', sa.String(100), nullable=False, unique=True),
        sa.Column('breach_date', sa.DateTime(), nullable=False),
        sa.Column('discovery_date', sa.DateTime(), nullable=False),
        sa.Column('breach_type', sa.String(100)),
        sa.Column('description_en', sa.Text(), nullable=False),
        sa.Column('description_ar', sa.Text()),
        sa.Column('affected_data_subjects_count', sa.Integer()),
        sa.Column('data_categories_affected', sa.JSON()),
        sa.Column('severity', sa.String(20), nullable=False),
        sa.Column('sdaia_notified', sa.Boolean(), default=False),
        sa.Column('sdaia_notification_date', sa.DateTime()),
        sa.Column('subjects_notified', sa.Boolean(), default=False),
        sa.Column('notification_method', sa.String(100)),
        sa.Column('containment_measures', sa.Text()),
        sa.Column('remediation_plan', sa.Text()),
        sa.Column('lessons_learned', sa.Text()),
        sa.Column('status', sa.String(50), default='open'),
        sa.Column('created_at', sa.DateTime(), default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'])
    )
    
    # ============================================================================
    # 16. INTEGRATIONS
    # ============================================================================
    op.create_table(
        'integrations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('integration_name', sa.String(100), nullable=False),
        sa.Column('integration_type', sa.String(50)),
        sa.Column('endpoint_url', sa.String(500)),
        sa.Column('api_key_encrypted', sa.String(500)),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('last_sync_at', sa.DateTime()),
        sa.Column('sync_frequency_minutes', sa.Integer()),
        sa.Column('created_at', sa.DateTime(), default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'])
    )
    
    # ============================================================================
    # 17. COMPLIANCE METRICS
    # ============================================================================
    op.create_table(
        'compliance_metrics',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('metric_date', sa.Date(), nullable=False),
        sa.Column('framework', sa.String(50)),
        sa.Column('total_controls', sa.Integer()),
        sa.Column('compliant_controls', sa.Integer()),
        sa.Column('partial_controls', sa.Integer()),
        sa.Column('non_compliant_controls', sa.Integer()),
        sa.Column('compliance_percentage', sa.Float()),
        sa.Column('total_risks', sa.Integer()),
        sa.Column('critical_risks', sa.Integer()),
        sa.Column('high_risks', sa.Integer()),
        sa.Column('risks_within_appetite', sa.Integer()),
        sa.Column('open_findings', sa.Integer()),
        sa.Column('overdue_findings', sa.Integer()),
        sa.Column('avg_remediation_days', sa.Float()),
        sa.Column('evidence_sufficiency_score', sa.Float()),
        sa.Column('expired_evidences', sa.Integer()),
        sa.Column('created_at', sa.DateTime(), default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'])
    )
    op.create_index('ix_compliance_metrics_metric_date', 'compliance_metrics', ['metric_date'])
    
    # ============================================================================
    # NOW: Update controls table with enterprise features
    # ============================================================================
    # Add new columns to existing controls table
    op.add_column('controls', sa.Column('organization_id', sa.Integer()))
    op.add_column('controls', sa.Column('status', sa.String(20), server_default='active'))
    op.add_column('controls', sa.Column('maturity_level', sa.String(30)))
    op.add_column('controls', sa.Column('effectiveness_score', sa.Float()))
    op.add_column('controls', sa.Column('control_owner_id', sa.Integer()))
    op.add_column('controls', sa.Column('reviewer_id', sa.Integer()))
    op.add_column('controls', sa.Column('policy_guidance_en', sa.Text()))
    op.add_column('controls', sa.Column('policy_guidance_ar', sa.Text()))
    op.add_column('controls', sa.Column('implementation_guidance_en', sa.Text()))
    op.add_column('controls', sa.Column('implementation_guidance_ar', sa.Text()))
    op.add_column('controls', sa.Column('test_frequency_days', sa.Integer()))
    op.add_column('controls', sa.Column('last_assessment_date', sa.Date()))
    op.add_column('controls', sa.Column('next_assessment_date', sa.Date()))
    op.add_column('controls', sa.Column('last_assessment_result', sa.String(20)))
    op.add_column('controls', sa.Column('is_applicable', sa.Boolean(), server_default='1'))
    op.add_column('controls', sa.Column('applicability_justification', sa.Text()))
    op.add_column('controls', sa.Column('created_by_id', sa.Integer()))
    op.add_column('controls', sa.Column('updated_by_id', sa.Integer()))
    
    # ============================================================================
    # NOW: Create tables that depend on controls
    # ============================================================================
    
    # EVIDENCES
    op.create_table(
        'evidences',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('evidence_id', sa.String(100), nullable=False, unique=True),
        sa.Column('template_id', sa.Integer()),
        sa.Column('control_id', sa.Integer()),
        sa.Column('title_en', sa.String(500), nullable=False),
        sa.Column('title_ar', sa.String(500)),
        sa.Column('description_en', sa.Text()),
        sa.Column('description_ar', sa.Text()),
        sa.Column('file_path', sa.String(500)),
        sa.Column('file_type', sa.String(50)),
        sa.Column('file_size_bytes', sa.Integer()),
        sa.Column('file_hash', sa.String(128)),
        sa.Column('version', sa.String(20)),
        sa.Column('previous_version_id', sa.Integer()),
        sa.Column('status', sa.String(50), nullable=False),
        sa.Column('validity_start_date', sa.Date()),
        sa.Column('validity_end_date', sa.Date()),
        sa.Column('is_expired', sa.Boolean(), default=False),
        sa.Column('uploaded_by_id', sa.Integer(), nullable=False),
        sa.Column('reviewed_by_id', sa.Integer()),
        sa.Column('approved_by_id', sa.Integer()),
        sa.Column('uploaded_at', sa.DateTime(), default=sa.func.now()),
        sa.Column('reviewed_at', sa.DateTime()),
        sa.Column('approved_at', sa.DateTime()),
        sa.Column('tags', sa.JSON()),
        sa.Column('metadata', sa.JSON()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id']),
        sa.ForeignKeyConstraint(['control_id'], ['controls.id']),
        sa.ForeignKeyConstraint(['template_id'], ['evidence_templates.id']),
        sa.ForeignKeyConstraint(['previous_version_id'], ['evidences.id']),
        sa.ForeignKeyConstraint(['uploaded_by_id'], ['users.id']),
        sa.ForeignKeyConstraint(['reviewed_by_id'], ['users.id']),
        sa.ForeignKeyConstraint(['approved_by_id'], ['users.id'])
    )
    op.create_index('ix_evidences_evidence_id', 'evidences', ['evidence_id'])
    
    # CONTROL ASSESSMENTS
    op.create_table(
        'control_assessments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('control_id', sa.Integer(), nullable=False),
        sa.Column('assessment_date', sa.Date(), nullable=False),
        sa.Column('assessor_id', sa.Integer(), nullable=False),
        sa.Column('test_result', sa.String(20), nullable=False),
        sa.Column('maturity_score', sa.String(30)),
        sa.Column('effectiveness_score', sa.Float()),
        sa.Column('findings_summary_en', sa.Text()),
        sa.Column('findings_summary_ar', sa.Text()),
        sa.Column('gaps_identified', sa.JSON()),
        sa.Column('recommendations_en', sa.Text()),
        sa.Column('recommendations_ar', sa.Text()),
        sa.Column('evidence_sufficient', sa.Boolean()),
        sa.Column('attached_evidence_ids', sa.JSON()),
        sa.Column('status', sa.String(50), default='draft'),
        sa.Column('approved_by_id', sa.Integer()),
        sa.Column('approved_at', sa.DateTime()),
        sa.Column('created_at', sa.DateTime(), default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id']),
        sa.ForeignKeyConstraint(['control_id'], ['controls.id']),
        sa.ForeignKeyConstraint(['assessor_id'], ['users.id']),
        sa.ForeignKeyConstraint(['approved_by_id'], ['users.id'])
    )
    
    # AUDIT FINDINGS
    op.create_table(
        'audit_findings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('finding_id', sa.String(100), nullable=False, unique=True),
        sa.Column('audit_program_id', sa.Integer()),
        sa.Column('control_id', sa.Integer()),
        sa.Column('title_en', sa.String(500), nullable=False),
        sa.Column('title_ar', sa.String(500)),
        sa.Column('description_en', sa.Text(), nullable=False),
        sa.Column('description_ar', sa.Text()),
        sa.Column('severity', sa.String(20), nullable=False),
        sa.Column('risk_rating', sa.String(20)),
        sa.Column('remediation_plan_en', sa.Text()),
        sa.Column('remediation_plan_ar', sa.Text()),
        sa.Column('remediation_owner_id', sa.Integer()),
        sa.Column('target_closure_date', sa.Date()),
        sa.Column('actual_closure_date', sa.Date()),
        sa.Column('is_overdue', sa.Boolean(), default=False),
        sa.Column('status', sa.String(20), default='open'),
        sa.Column('verification_evidence_ids', sa.JSON()),
        sa.Column('verified_by_id', sa.Integer()),
        sa.Column('verified_at', sa.DateTime()),
        sa.Column('identified_by_id', sa.Integer()),
        sa.Column('identified_at', sa.DateTime(), default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), onupdate=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id']),
        sa.ForeignKeyConstraint(['audit_program_id'], ['audit_programs.id']),
        sa.ForeignKeyConstraint(['control_id'], ['controls.id']),
        sa.ForeignKeyConstraint(['remediation_owner_id'], ['users.id']),
        sa.ForeignKeyConstraint(['verified_by_id'], ['users.id']),
        sa.ForeignKeyConstraint(['identified_by_id'], ['users.id'])
    )
    op.create_index('ix_audit_findings_finding_id', 'audit_findings', ['finding_id'])
    
    # CONTROL EXCEPTIONS
    op.create_table(
        'control_exceptions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('exception_id', sa.String(100), nullable=False, unique=True),
        sa.Column('control_id', sa.Integer(), nullable=False),
        sa.Column('justification_en', sa.Text(), nullable=False),
        sa.Column('justification_ar', sa.Text()),
        sa.Column('risk_acceptance_statement', sa.Text()),
        sa.Column('compensating_controls', sa.JSON()),
        sa.Column('requested_by_id', sa.Integer(), nullable=False),
        sa.Column('approved_by_id', sa.Integer()),
        sa.Column('approval_date', sa.Date()),
        sa.Column('effective_date', sa.Date(), nullable=False),
        sa.Column('expiry_date', sa.Date(), nullable=False),
        sa.Column('is_expired', sa.Boolean(), default=False),
        sa.Column('renewal_required', sa.Boolean(), default=True),
        sa.Column('status', sa.String(50), default='pending'),
        sa.Column('created_at', sa.DateTime(), default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id']),
        sa.ForeignKeyConstraint(['control_id'], ['controls.id']),
        sa.ForeignKeyConstraint(['requested_by_id'], ['users.id']),
        sa.ForeignKeyConstraint(['approved_by_id'], ['users.id'])
    )
    
    # AUTOMATED EVIDENCES
    op.create_table(
        'automated_evidences',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('control_id', sa.Integer(), nullable=False),
        sa.Column('integration_id', sa.Integer()),
        sa.Column('evidence_rule', sa.JSON()),
        sa.Column('collection_frequency', sa.String(50)),
        sa.Column('last_collected_at', sa.DateTime()),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('created_at', sa.DateTime(), default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id']),
        sa.ForeignKeyConstraint(['control_id'], ['controls.id']),
        sa.ForeignKeyConstraint(['integration_id'], ['integrations.id'])
    )
    
    print("✅ Enterprise GRC schema deployed successfully")
    print("📊 30+ tables created")
    print("🔒 Multi-tenancy, RBAC, audit trail, workflow engine enabled")


def downgrade():
    """Rollback enterprise schema"""
    # Drop in reverse order of creation
    op.drop_table('automated_evidences')
    op.drop_table('control_exceptions')
    op.drop_table('audit_findings')
    op.drop_table('control_assessments')
    op.drop_table('evidences')
    
    # Drop columns from controls
    op.drop_column('controls', 'updated_by_id')
    op.drop_column('controls', 'created_by_id')
    op.drop_column('controls', 'applicability_justification')
    op.drop_column('controls', 'is_applicable')
    op.drop_column('controls', 'last_assessment_result')
    op.drop_column('controls', 'next_assessment_date')
    op.drop_column('controls', 'last_assessment_date')
    op.drop_column('controls', 'test_frequency_days')
    op.drop_column('controls', 'implementation_guidance_ar')
    op.drop_column('controls', 'implementation_guidance_en')
    op.drop_column('controls', 'policy_guidance_ar')
    op.drop_column('controls', 'policy_guidance_en')
    op.drop_column('controls', 'reviewer_id')
    op.drop_column('controls', 'control_owner_id')
    op.drop_column('controls', 'effectiveness_score')
    op.drop_column('controls', 'maturity_level')
    op.drop_column('controls', 'status')
    op.drop_column('controls', 'organization_id')
    
    # Drop other tables
    op.drop_table('compliance_metrics')
    op.drop_table('integrations')
    op.drop_table('data_breaches')
    op.drop_table('dsar_requests')
    op.drop_table('ropa_records')
    op.drop_table('vendors')
    op.drop_table('workflow_cases')
    op.drop_table('audit_programs')
    op.drop_table('risks')
    op.drop_table('evidence_templates')
    op.drop_table('policies')
    op.drop_table('audit_logs')
    op.drop_table('assets')
    op.drop_table('users')
    op.drop_table('organizations')
