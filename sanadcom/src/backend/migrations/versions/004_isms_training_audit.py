"""
Phase 2.4 Database Migration: ISMS, Training & Audit Management

Creates tables for:
- ISMS Policy Management (ISO 27001 A.5)
- Security Training & Awareness (ISO 27001 A.6.3)
- External Audit Management (ISO 27001 Clause 9.2)

Revision ID: 004_isms_training_audit
Revises: 003_ai_governance_siem
Create Date: 2026-02-09
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

# revision identifiers
revision = '004_isms_training_audit'
down_revision = '003_ai_governance_siem'
branch_labels = None
depends_on = None


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
        sa.Column('author_id', UUID(as_uuid=True), nullable=False),
        sa.Column('reviewer_id', UUID(as_uuid=True), nullable=True),
        sa.Column('approver_id', UUID(as_uuid=True), nullable=True),
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
        sa.Column('user_id', UUID(as_uuid=True), nullable=False),
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
        sa.Column('requested_by_id', UUID(as_uuid=True), nullable=False),
        sa.Column('approved_by_id', UUID(as_uuid=True), nullable=True),
        sa.Column('status', sa.String(50), nullable=False, default='pending'),
        sa.Column('requested_date', sa.DateTime(), nullable=False),
        sa.Column('approval_date', sa.DateTime(), nullable=True),
        sa.Column('effective_date', sa.DateTime(), nullable=True),
        sa.Column('expiry_date', sa.DateTime(), nullable=False),
        sa.Column('review_date', sa.DateTime(), nullable=True),
        sa.Column('residual_risk_score', sa.Integer(), nullable=True),
        sa.Column('risk_owner_id', UUID(as_uuid=True), nullable=True),
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
        sa.Column('changed_by_id', UUID(as_uuid=True), nullable=False),
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
        sa.Column('owner_id', UUID(as_uuid=True), nullable=False),
        sa.Column('custodian_id', UUID(as_uuid=True), nullable=True),
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
    
    # ============================================================================
    # SECURITY TRAINING & AWARENESS TABLES
    # ============================================================================
    
    # TrainingCourse table
    op.create_table(
        'training_courses',
        sa.Column('course_id', sa.Integer(), nullable=False),
        sa.Column('course_code', sa.String(50), nullable=False),
        sa.Column('title_en', sa.String(500), nullable=False),
        sa.Column('title_ar', sa.String(500), nullable=False),
        sa.Column('description_en', sa.Text(), nullable=False),
        sa.Column('description_ar', sa.Text(), nullable=False),
        sa.Column('learning_objectives_en', sa.JSON(), nullable=False),
        sa.Column('learning_objectives_ar', sa.JSON(), nullable=False),
        sa.Column('training_type', sa.String(50), nullable=False),
        sa.Column('category', sa.String(100), nullable=False),
        sa.Column('difficulty_level', sa.String(50), nullable=False),
        sa.Column('duration_minutes', sa.Integer(), nullable=False),
        sa.Column('is_mandatory', sa.Boolean(), nullable=False, default=False),
        sa.Column('required_for_roles', sa.JSON(), nullable=True),
        sa.Column('prerequisites', sa.JSON(), nullable=True),
        sa.Column('validity_days', sa.Integer(), nullable=True),
        sa.Column('passing_score', sa.Integer(), nullable=False, default=80),
        sa.Column('content_url_en', sa.String(1000), nullable=True),
        sa.Column('content_url_ar', sa.String(1000), nullable=True),
        sa.Column('materials_json', sa.JSON(), nullable=True),
        sa.Column('iso27001_controls', sa.JSON(), nullable=True),
        sa.Column('nca_ecc_controls', sa.JSON(), nullable=True),
        sa.Column('pdpl_articles', sa.JSON(), nullable=True),
        sa.Column('sdaia_ai_principles', sa.JSON(), nullable=True),
        sa.Column('instructor_id', UUID(as_uuid=True), nullable=True),
        sa.Column('status', sa.String(50), nullable=False, default='draft'),
        sa.Column('published_date', sa.DateTime(), nullable=True),
        sa.Column('last_updated_date', sa.DateTime(), nullable=False),
        sa.Column('total_enrollments', sa.Integer(), nullable=False, default=0),
        sa.Column('total_completions', sa.Integer(), nullable=False, default=0),
        sa.Column('average_score', sa.Float(), nullable=True),
        sa.Column('average_completion_time_minutes', sa.Integer(), nullable=True),
        sa.Column('tags', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['instructor_id'], ['users.user_id']),
        sa.PrimaryKeyConstraint('course_id')
    )
    op.create_index('ix_training_courses_course_code', 'training_courses', ['course_code'], unique=True)
    op.create_index('ix_training_courses_status', 'training_courses', ['status'])
    op.create_index('ix_training_courses_category', 'training_courses', ['category'])
    
    # TrainingEnrollment table
    op.create_table(
        'training_enrollments',
        sa.Column('enrollment_id', sa.Integer(), nullable=False),
        sa.Column('course_id', sa.Integer(), nullable=False),
        sa.Column('user_id', UUID(as_uuid=True), nullable=False),
        sa.Column('enrolled_at', sa.DateTime(), nullable=False),
        sa.Column('enrollment_method', sa.String(50), nullable=False),
        sa.Column('assigned_by_id', UUID(as_uuid=True), nullable=True),
        sa.Column('due_date', sa.DateTime(), nullable=True),
        sa.Column('status', sa.String(50), nullable=False, default='enrolled'),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('progress_percentage', sa.Integer(), nullable=False, default=0),
        sa.Column('time_spent_minutes', sa.Integer(), nullable=False, default=0),
        sa.Column('attempts_count', sa.Integer(), nullable=False, default=0),
        sa.Column('best_score', sa.Integer(), nullable=True),
        sa.Column('passing_score_required', sa.Integer(), nullable=False, default=80),
        sa.Column('passed', sa.Boolean(), nullable=False, default=False),
        sa.Column('certificate_issued', sa.Boolean(), nullable=False, default=False),
        sa.Column('certificate_number', sa.String(100), nullable=True),
        sa.Column('certificate_issued_at', sa.DateTime(), nullable=True),
        sa.Column('certificate_expires_at', sa.DateTime(), nullable=True),
        sa.Column('reminder_sent_at', sa.DateTime(), nullable=True),
        sa.Column('overdue_notification_sent', sa.Boolean(), nullable=False, default=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['course_id'], ['training_courses.course_id']),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id']),
        sa.ForeignKeyConstraint(['assigned_by_id'], ['users.user_id']),
        sa.PrimaryKeyConstraint('enrollment_id')
    )
    op.create_index('ix_training_enrollments_course_id', 'training_enrollments', ['course_id'])
    op.create_index('ix_training_enrollments_user_id', 'training_enrollments', ['user_id'])
    op.create_index('ix_training_enrollments_status', 'training_enrollments', ['status'])
    
    # TrainingAssessment table
    op.create_table(
        'training_assessments',
        sa.Column('assessment_id', sa.Integer(), nullable=False),
        sa.Column('course_id', sa.Integer(), nullable=False),
        sa.Column('question_en', sa.Text(), nullable=False),
        sa.Column('question_ar', sa.Text(), nullable=False),
        sa.Column('question_type', sa.String(50), nullable=False),
        sa.Column('options_en', sa.JSON(), nullable=True),
        sa.Column('options_ar', sa.JSON(), nullable=True),
        sa.Column('correct_answer', sa.JSON(), nullable=False),
        sa.Column('explanation_en', sa.Text(), nullable=True),
        sa.Column('explanation_ar', sa.Text(), nullable=True),
        sa.Column('points', sa.Integer(), nullable=False, default=1),
        sa.Column('order_number', sa.Integer(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['course_id'], ['training_courses.course_id']),
        sa.PrimaryKeyConstraint('assessment_id')
    )
    op.create_index('ix_training_assessments_course_id', 'training_assessments', ['course_id'])
    
    # TrainingAttempt table
    op.create_table(
        'training_attempts',
        sa.Column('attempt_id', sa.Integer(), nullable=False),
        sa.Column('enrollment_id', sa.Integer(), nullable=False),
        sa.Column('attempt_number', sa.Integer(), nullable=False),
        sa.Column('started_at', sa.DateTime(), nullable=False),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('time_spent_minutes', sa.Integer(), nullable=True),
        sa.Column('responses_json', sa.JSON(), nullable=False),
        sa.Column('total_questions', sa.Integer(), nullable=False),
        sa.Column('correct_answers', sa.Integer(), nullable=False, default=0),
        sa.Column('score_percentage', sa.Integer(), nullable=False, default=0),
        sa.Column('points_earned', sa.Integer(), nullable=False, default=0),
        sa.Column('points_possible', sa.Integer(), nullable=False),
        sa.Column('passed', sa.Boolean(), nullable=False, default=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['enrollment_id'], ['training_enrollments.enrollment_id']),
        sa.PrimaryKeyConstraint('attempt_id')
    )
    op.create_index('ix_training_attempts_enrollment_id', 'training_attempts', ['enrollment_id'])
    
    # AwarenessCampaign table
    op.create_table(
        'awareness_campaigns',
        sa.Column('campaign_id', sa.Integer(), nullable=False),
        sa.Column('campaign_code', sa.String(50), nullable=False),
        sa.Column('title_en', sa.String(500), nullable=False),
        sa.Column('title_ar', sa.String(500), nullable=False),
        sa.Column('description_en', sa.Text(), nullable=False),
        sa.Column('description_ar', sa.Text(), nullable=False),
        sa.Column('message_en', sa.Text(), nullable=False),
        sa.Column('message_ar', sa.Text(), nullable=False),
        sa.Column('campaign_type', sa.String(100), nullable=False),
        sa.Column('category', sa.String(100), nullable=False),
        sa.Column('target_audience', sa.JSON(), nullable=False),
        sa.Column('target_user_ids', sa.JSON(), nullable=True),
        sa.Column('start_date', sa.DateTime(), nullable=False),
        sa.Column('end_date', sa.DateTime(), nullable=False),
        sa.Column('delivery_frequency', sa.String(50), nullable=True),
        sa.Column('content_url', sa.String(1000), nullable=True),
        sa.Column('attachments_json', sa.JSON(), nullable=True),
        sa.Column('total_sent', sa.Integer(), nullable=False, default=0),
        sa.Column('total_opened', sa.Integer(), nullable=False, default=0),
        sa.Column('total_clicked', sa.Integer(), nullable=False, default=0),
        sa.Column('total_completed_action', sa.Integer(), nullable=False, default=0),
        sa.Column('total_phishing_clicks', sa.Integer(), nullable=True),
        sa.Column('total_reported_phishing', sa.Integer(), nullable=True),
        sa.Column('created_by_id', UUID(as_uuid=True), nullable=False),
        sa.Column('status', sa.String(50), nullable=False, default='draft'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['created_by_id'], ['users.user_id']),
        sa.PrimaryKeyConstraint('campaign_id')
    )
    op.create_index('ix_awareness_campaigns_campaign_code', 'awareness_campaigns', ['campaign_code'], unique=True)
    op.create_index('ix_awareness_campaigns_status', 'awareness_campaigns', ['status'])
    
    # CompetencyMatrix table
    op.create_table(
        'competency_matrix',
        sa.Column('competency_id', sa.Integer(), nullable=False),
        sa.Column('role_name', sa.String(200), nullable=False),
        sa.Column('department', sa.String(200), nullable=True),
        sa.Column('required_courses', sa.JSON(), nullable=False),
        sa.Column('optional_courses', sa.JSON(), nullable=True),
        sa.Column('required_certifications', sa.JSON(), nullable=True),
        sa.Column('preferred_certifications', sa.JSON(), nullable=True),
        sa.Column('competency_description_en', sa.Text(), nullable=True),
        sa.Column('competency_description_ar', sa.Text(), nullable=True),
        sa.Column('minimum_training_hours_per_year', sa.Integer(), nullable=False, default=8),
        sa.Column('recertification_period_days', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('competency_id')
    )
    op.create_index('ix_competency_matrix_role_name', 'competency_matrix', ['role_name'])
    
    # ============================================================================
    # EXTERNAL AUDIT MANAGEMENT TABLES
    # ============================================================================
    
    # AuditProgram table
    op.create_table(
        'audit_programs',
        sa.Column('program_id', sa.Integer(), nullable=False),
        sa.Column('program_code', sa.String(50), nullable=False),
        sa.Column('title_en', sa.String(500), nullable=False),
        sa.Column('title_ar', sa.String(500), nullable=False),
        sa.Column('description_en', sa.Text(), nullable=True),
        sa.Column('description_ar', sa.Text(), nullable=True),
        sa.Column('audit_year', sa.Integer(), nullable=False),
        sa.Column('audit_type', sa.String(50), nullable=False),
        sa.Column('scope_description_en', sa.Text(), nullable=False),
        sa.Column('scope_description_ar', sa.Text(), nullable=False),
        sa.Column('iso27001_in_scope', sa.Boolean(), nullable=False, default=True),
        sa.Column('iso27017_in_scope', sa.Boolean(), nullable=False, default=False),
        sa.Column('iso27018_in_scope', sa.Boolean(), nullable=False, default=False),
        sa.Column('iso27701_in_scope', sa.Boolean(), nullable=False, default=False),
        sa.Column('nca_ecc_in_scope', sa.Boolean(), nullable=False, default=True),
        sa.Column('nca_ccc_in_scope', sa.Boolean(), nullable=False, default=True),
        sa.Column('pdpl_in_scope', sa.Boolean(), nullable=False, default=True),
        sa.Column('sdaia_ai_in_scope', sa.Boolean(), nullable=False, default=False),
        sa.Column('planned_start_date', sa.DateTime(), nullable=False),
        sa.Column('planned_end_date', sa.DateTime(), nullable=False),
        sa.Column('actual_start_date', sa.DateTime(), nullable=True),
        sa.Column('actual_end_date', sa.DateTime(), nullable=True),
        sa.Column('lead_auditor_id', UUID(as_uuid=True), nullable=True),
        sa.Column('audit_team_ids', sa.JSON(), nullable=True),
        sa.Column('external_auditor_firm', sa.String(500), nullable=True),
        sa.Column('external_auditor_contact', sa.JSON(), nullable=True),
        sa.Column('status', sa.String(50), nullable=False, default='planned'),
        sa.Column('total_findings', sa.Integer(), nullable=False, default=0),
        sa.Column('critical_findings', sa.Integer(), nullable=False, default=0),
        sa.Column('high_findings', sa.Integer(), nullable=False, default=0),
        sa.Column('medium_findings', sa.Integer(), nullable=False, default=0),
        sa.Column('low_findings', sa.Integer(), nullable=False, default=0),
        sa.Column('observations', sa.Integer(), nullable=False, default=0),
        sa.Column('certification_body', sa.String(500), nullable=True),
        sa.Column('certificate_number', sa.String(200), nullable=True),
        sa.Column('certificate_issue_date', sa.DateTime(), nullable=True),
        sa.Column('certificate_expiry_date', sa.DateTime(), nullable=True),
        sa.Column('certification_scope_en', sa.Text(), nullable=True),
        sa.Column('certification_scope_ar', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['lead_auditor_id'], ['users.user_id']),
        sa.PrimaryKeyConstraint('program_id')
    )
    op.create_index('ix_audit_programs_program_code', 'audit_programs', ['program_code'], unique=True)
    op.create_index('ix_audit_programs_status', 'audit_programs', ['status'])
    op.create_index('ix_audit_programs_audit_year', 'audit_programs', ['audit_year'])
    
    # AuditEngagement table
    op.create_table(
        'audit_engagements',
        sa.Column('engagement_id', sa.Integer(), nullable=False),
        sa.Column('program_id', sa.Integer(), nullable=False),
        sa.Column('engagement_code', sa.String(50), nullable=False),
        sa.Column('title_en', sa.String(500), nullable=False),
        sa.Column('title_ar', sa.String(500), nullable=False),
        sa.Column('objective_en', sa.Text(), nullable=False),
        sa.Column('objective_ar', sa.Text(), nullable=False),
        sa.Column('control_domain', sa.String(200), nullable=True),
        sa.Column('controls_in_scope', sa.JSON(), nullable=False),
        sa.Column('departments_in_scope', sa.JSON(), nullable=True),
        sa.Column('systems_in_scope', sa.JSON(), nullable=True),
        sa.Column('scheduled_date', sa.DateTime(), nullable=False),
        sa.Column('scheduled_duration_hours', sa.Integer(), nullable=False),
        sa.Column('actual_start_time', sa.DateTime(), nullable=True),
        sa.Column('actual_end_time', sa.DateTime(), nullable=True),
        sa.Column('auditor_ids', sa.JSON(), nullable=False),
        sa.Column('auditee_ids', sa.JSON(), nullable=False),
        sa.Column('agenda_en', sa.Text(), nullable=True),
        sa.Column('agenda_ar', sa.Text(), nullable=True),
        sa.Column('meeting_notes_en', sa.Text(), nullable=True),
        sa.Column('meeting_notes_ar', sa.Text(), nullable=True),
        sa.Column('status', sa.String(50), nullable=False, default='planned'),
        sa.Column('completion_percentage', sa.Integer(), nullable=False, default=0),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['program_id'], ['audit_programs.program_id']),
        sa.PrimaryKeyConstraint('engagement_id')
    )
    op.create_index('ix_audit_engagements_engagement_code', 'audit_engagements', ['engagement_code'], unique=True)
    op.create_index('ix_audit_engagements_program_id', 'audit_engagements', ['program_id'])
    op.create_index('ix_audit_engagements_status', 'audit_engagements', ['status'])
    
    # AuditEvidence table
    op.create_table(
        'audit_evidence',
        sa.Column('evidence_id', sa.Integer(), nullable=False),
        sa.Column('engagement_id', sa.Integer(), nullable=False),
        sa.Column('evidence_reference', sa.String(100), nullable=False),
        sa.Column('title_en', sa.String(500), nullable=False),
        sa.Column('title_ar', sa.String(500), nullable=False),
        sa.Column('description_en', sa.Text(), nullable=True),
        sa.Column('description_ar', sa.Text(), nullable=True),
        sa.Column('control_id', sa.String(50), nullable=False),
        sa.Column('control_requirement_en', sa.Text(), nullable=False),
        sa.Column('control_requirement_ar', sa.Text(), nullable=False),
        sa.Column('evidence_type', sa.String(100), nullable=False),
        sa.Column('evidence_category', sa.String(100), nullable=False),
        sa.Column('requested_by_id', UUID(as_uuid=True), nullable=False),
        sa.Column('provided_by_id', UUID(as_uuid=True), nullable=True),
        sa.Column('requested_date', sa.DateTime(), nullable=False),
        sa.Column('due_date', sa.DateTime(), nullable=False),
        sa.Column('submitted_date', sa.DateTime(), nullable=True),
        sa.Column('file_path', sa.String(1000), nullable=True),
        sa.Column('file_url', sa.String(1000), nullable=True),
        sa.Column('file_hash', sa.String(128), nullable=True),
        sa.Column('file_size_bytes', sa.Integer(), nullable=True),
        sa.Column('status', sa.String(50), nullable=False, default='pending'),
        sa.Column('reviewed_by_id', UUID(as_uuid=True), nullable=True),
        sa.Column('reviewed_date', sa.DateTime(), nullable=True),
        sa.Column('reviewer_notes_en', sa.Text(), nullable=True),
        sa.Column('reviewer_notes_ar', sa.Text(), nullable=True),
        sa.Column('adequacy_rating', sa.Integer(), nullable=True),
        sa.Column('completeness_score', sa.Integer(), nullable=True),
        sa.Column('tags', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['engagement_id'], ['audit_engagements.engagement_id']),
        sa.ForeignKeyConstraint(['requested_by_id'], ['users.user_id']),
        sa.ForeignKeyConstraint(['provided_by_id'], ['users.user_id']),
        sa.ForeignKeyConstraint(['reviewed_by_id'], ['users.user_id']),
        sa.PrimaryKeyConstraint('evidence_id')
    )
    op.create_index('ix_audit_evidence_evidence_reference', 'audit_evidence', ['evidence_reference'], unique=True)
    op.create_index('ix_audit_evidence_engagement_id', 'audit_evidence', ['engagement_id'])
    op.create_index('ix_audit_evidence_status', 'audit_evidence', ['status'])
    
    # AuditFinding table
    op.create_table(
        'audit_findings',
        sa.Column('finding_id', sa.Integer(), nullable=False),
        sa.Column('program_id', sa.Integer(), nullable=False),
        sa.Column('finding_number', sa.String(100), nullable=False),
        sa.Column('title_en', sa.String(500), nullable=False),
        sa.Column('title_ar', sa.String(500), nullable=False),
        sa.Column('description_en', sa.Text(), nullable=False),
        sa.Column('description_ar', sa.Text(), nullable=False),
        sa.Column('evidence_reference_en', sa.Text(), nullable=False),
        sa.Column('evidence_reference_ar', sa.Text(), nullable=False),
        sa.Column('severity', sa.String(50), nullable=False),
        sa.Column('finding_type', sa.String(100), nullable=False),
        sa.Column('control_reference', sa.String(50), nullable=False),
        sa.Column('control_requirement_en', sa.Text(), nullable=False),
        sa.Column('control_requirement_ar', sa.Text(), nullable=False),
        sa.Column('gap_identified_en', sa.Text(), nullable=False),
        sa.Column('gap_identified_ar', sa.Text(), nullable=False),
        sa.Column('iso27001_clause', sa.String(50), nullable=True),
        sa.Column('nca_ecc_control', sa.String(50), nullable=True),
        sa.Column('nca_ccc_control', sa.String(50), nullable=True),
        sa.Column('pdpl_article', sa.String(50), nullable=True),
        sa.Column('risk_rating', sa.String(50), nullable=False),
        sa.Column('impact_description_en', sa.Text(), nullable=True),
        sa.Column('impact_description_ar', sa.Text(), nullable=True),
        sa.Column('recommendation_en', sa.Text(), nullable=False),
        sa.Column('recommendation_ar', sa.Text(), nullable=False),
        sa.Column('owner_id', UUID(as_uuid=True), nullable=False),
        sa.Column('due_date', sa.DateTime(), nullable=False),
        sa.Column('corrective_action_plan_en', sa.Text(), nullable=True),
        sa.Column('corrective_action_plan_ar', sa.Text(), nullable=True),
        sa.Column('responsible_person_id', UUID(as_uuid=True), nullable=True),
        sa.Column('target_closure_date', sa.DateTime(), nullable=True),
        sa.Column('actual_closure_date', sa.DateTime(), nullable=True),
        sa.Column('status', sa.String(50), nullable=False, default='open'),
        sa.Column('progress_percentage', sa.Integer(), nullable=False, default=0),
        sa.Column('verification_evidence_en', sa.Text(), nullable=True),
        sa.Column('verification_evidence_ar', sa.Text(), nullable=True),
        sa.Column('verified_by_id', UUID(as_uuid=True), nullable=True),
        sa.Column('verification_date', sa.DateTime(), nullable=True),
        sa.Column('verification_notes_en', sa.Text(), nullable=True),
        sa.Column('verification_notes_ar', sa.Text(), nullable=True),
        sa.Column('escalated', sa.Boolean(), nullable=False, default=False),
        sa.Column('escalation_reason_en', sa.Text(), nullable=True),
        sa.Column('escalation_reason_ar', sa.Text(), nullable=True),
        sa.Column('escalated_to_id', UUID(as_uuid=True), nullable=True),
        sa.Column('escalation_date', sa.DateTime(), nullable=True),
        sa.Column('identified_date', sa.DateTime(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['program_id'], ['audit_programs.program_id']),
        sa.ForeignKeyConstraint(['owner_id'], ['users.user_id']),
        sa.ForeignKeyConstraint(['responsible_person_id'], ['users.user_id']),
        sa.ForeignKeyConstraint(['verified_by_id'], ['users.user_id']),
        sa.ForeignKeyConstraint(['escalated_to_id'], ['users.user_id']),
        sa.PrimaryKeyConstraint('finding_id')
    )
    op.create_index('ix_audit_findings_finding_number', 'audit_findings', ['finding_number'], unique=True)
    op.create_index('ix_audit_findings_program_id', 'audit_findings', ['program_id'])
    op.create_index('ix_audit_findings_status', 'audit_findings', ['status'])
    op.create_index('ix_audit_findings_severity', 'audit_findings', ['severity'])
    
    # CorrectiveAction table
    op.create_table(
        'corrective_actions',
        sa.Column('action_id', sa.Integer(), nullable=False),
        sa.Column('finding_id', sa.Integer(), nullable=False),
        sa.Column('action_number', sa.String(100), nullable=False),
        sa.Column('title_en', sa.String(500), nullable=False),
        sa.Column('title_ar', sa.String(500), nullable=False),
        sa.Column('description_en', sa.Text(), nullable=False),
        sa.Column('description_ar', sa.Text(), nullable=False),
        sa.Column('root_cause_en', sa.Text(), nullable=False),
        sa.Column('root_cause_ar', sa.Text(), nullable=False),
        sa.Column('root_cause_category', sa.String(100), nullable=True),
        sa.Column('action_steps_en', sa.JSON(), nullable=False),
        sa.Column('action_steps_ar', sa.JSON(), nullable=False),
        sa.Column('owner_id', UUID(as_uuid=True), nullable=False),
        sa.Column('assigned_to_ids', sa.JSON(), nullable=True),
        sa.Column('planned_start_date', sa.DateTime(), nullable=False),
        sa.Column('planned_completion_date', sa.DateTime(), nullable=False),
        sa.Column('actual_start_date', sa.DateTime(), nullable=True),
        sa.Column('actual_completion_date', sa.DateTime(), nullable=True),
        sa.Column('status', sa.String(50), nullable=False, default='planned'),
        sa.Column('progress_percentage', sa.Integer(), nullable=False, default=0),
        sa.Column('effectiveness_verified', sa.Boolean(), nullable=False, default=False),
        sa.Column('verification_method_en', sa.Text(), nullable=True),
        sa.Column('verification_method_ar', sa.Text(), nullable=True),
        sa.Column('verification_date', sa.DateTime(), nullable=True),
        sa.Column('verified_by_id', UUID(as_uuid=True), nullable=True),
        sa.Column('last_update_en', sa.Text(), nullable=True),
        sa.Column('last_update_ar', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['finding_id'], ['audit_findings.finding_id']),
        sa.ForeignKeyConstraint(['owner_id'], ['users.user_id']),
        sa.ForeignKeyConstraint(['verified_by_id'], ['users.user_id']),
        sa.PrimaryKeyConstraint('action_id')
    )
    op.create_index('ix_corrective_actions_action_number', 'corrective_actions', ['action_number'], unique=True)
    op.create_index('ix_corrective_actions_finding_id', 'corrective_actions', ['finding_id'])
    op.create_index('ix_corrective_actions_status', 'corrective_actions', ['status'])
    
    # CertificationRecord table
    op.create_table(
        'certification_records',
        sa.Column('certification_id', sa.Integer(), nullable=False),
        sa.Column('certificate_number', sa.String(200), nullable=False),
        sa.Column('certification_standard', sa.String(100), nullable=False),
        sa.Column('certification_body', sa.String(500), nullable=False),
        sa.Column('scope_en', sa.Text(), nullable=False),
        sa.Column('scope_ar', sa.Text(), nullable=False),
        sa.Column('scope_locations', sa.JSON(), nullable=True),
        sa.Column('scope_exclusions_en', sa.Text(), nullable=True),
        sa.Column('scope_exclusions_ar', sa.Text(), nullable=True),
        sa.Column('issue_date', sa.DateTime(), nullable=False),
        sa.Column('expiry_date', sa.DateTime(), nullable=False),
        sa.Column('surveillance_due_dates', sa.JSON(), nullable=True),
        sa.Column('status', sa.String(50), nullable=False, default='active'),
        sa.Column('certificate_file_path', sa.String(1000), nullable=True),
        sa.Column('certificate_url', sa.String(1000), nullable=True),
        sa.Column('audit_report_path', sa.String(1000), nullable=True),
        sa.Column('initial_audit_program_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['initial_audit_program_id'], ['audit_programs.program_id']),
        sa.PrimaryKeyConstraint('certification_id')
    )
    op.create_index('ix_certification_records_certificate_number', 'certification_records', ['certificate_number'], unique=True)
    op.create_index('ix_certification_records_status', 'certification_records', ['status'])


def downgrade():
    """Drop Phase 2.4 tables"""
    
    # Audit Management tables
    op.drop_index('ix_certification_records_status', table_name='certification_records')
    op.drop_index('ix_certification_records_certificate_number', table_name='certification_records')
    op.drop_table('certification_records')
    
    op.drop_index('ix_corrective_actions_status', table_name='corrective_actions')
    op.drop_index('ix_corrective_actions_finding_id', table_name='corrective_actions')
    op.drop_index('ix_corrective_actions_action_number', table_name='corrective_actions')
    op.drop_table('corrective_actions')
    
    op.drop_index('ix_audit_findings_severity', table_name='audit_findings')
    op.drop_index('ix_audit_findings_status', table_name='audit_findings')
    op.drop_index('ix_audit_findings_program_id', table_name='audit_findings')
    op.drop_index('ix_audit_findings_finding_number', table_name='audit_findings')
    op.drop_table('audit_findings')
    
    op.drop_index('ix_audit_evidence_status', table_name='audit_evidence')
    op.drop_index('ix_audit_evidence_engagement_id', table_name='audit_evidence')
    op.drop_index('ix_audit_evidence_evidence_reference', table_name='audit_evidence')
    op.drop_table('audit_evidence')
    
    op.drop_index('ix_audit_engagements_status', table_name='audit_engagements')
    op.drop_index('ix_audit_engagements_program_id', table_name='audit_engagements')
    op.drop_index('ix_audit_engagements_engagement_code', table_name='audit_engagements')
    op.drop_table('audit_engagements')
    
    op.drop_index('ix_audit_programs_audit_year', table_name='audit_programs')
    op.drop_index('ix_audit_programs_status', table_name='audit_programs')
    op.drop_index('ix_audit_programs_program_code', table_name='audit_programs')
    op.drop_table('audit_programs')
    
    # Training & Awareness tables
    op.drop_index('ix_competency_matrix_role_name', table_name='competency_matrix')
    op.drop_table('competency_matrix')
    
    op.drop_index('ix_awareness_campaigns_status', table_name='awareness_campaigns')
    op.drop_index('ix_awareness_campaigns_campaign_code', table_name='awareness_campaigns')
    op.drop_table('awareness_campaigns')
    
    op.drop_index('ix_training_attempts_enrollment_id', table_name='training_attempts')
    op.drop_table('training_attempts')
    
    op.drop_index('ix_training_assessments_course_id', table_name='training_assessments')
    op.drop_table('training_assessments')
    
    op.drop_index('ix_training_enrollments_status', table_name='training_enrollments')
    op.drop_index('ix_training_enrollments_user_id', table_name='training_enrollments')
    op.drop_index('ix_training_enrollments_course_id', table_name='training_enrollments')
    op.drop_table('training_enrollments')
    
    op.drop_index('ix_training_courses_category', table_name='training_courses')
    op.drop_index('ix_training_courses_status', table_name='training_courses')
    op.drop_index('ix_training_courses_course_code', table_name='training_courses')
    op.drop_table('training_courses')
    
    # ISMS Policy Management tables
    op.drop_index('ix_asset_inventory_classification', table_name='asset_inventory')
    op.drop_index('ix_asset_inventory_asset_type', table_name='asset_inventory')
    op.drop_index('ix_asset_inventory_asset_number', table_name='asset_inventory')
    op.drop_table('asset_inventory')
    
    op.drop_index('ix_doc_versions_policy_id', table_name='document_versions')
    op.drop_table('document_versions')
    
    op.drop_index('ix_policy_exceptions_status', table_name='policy_exceptions')
    op.drop_index('ix_policy_exceptions_exception_number', table_name='policy_exceptions')
    op.drop_table('policy_exceptions')
    
    op.drop_index('ix_policy_acks_user_id', table_name='policy_acknowledgements')
    op.drop_index('ix_policy_acks_policy_id', table_name='policy_acknowledgements')
    op.drop_table('policy_acknowledgements')
    
    op.drop_index('ix_isms_policies_policy_type', table_name='isms_policies')
    op.drop_index('ix_isms_policies_status', table_name='isms_policies')
    op.drop_index('ix_isms_policies_policy_number', table_name='isms_policies')
    op.drop_index('ix_isms_policies_policy_id', table_name='isms_policies')
    op.drop_table('isms_policies')
