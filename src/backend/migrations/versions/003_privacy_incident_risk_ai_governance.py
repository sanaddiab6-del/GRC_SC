"""003_privacy_incident_risk_ai_governance

Revision ID: 003
Revises: 002
Create Date: 2024-01-15 00:00:00.000000

Description:
    Phase 2.2 & 2.3 - Full Compliance Implementation
    - Privacy & Data Protection (PDPL) - Phase 2.2
    - Incident Response (NCA ECC-IS-5) - Phase 2.3
    - Risk Management (NCA ECC-RM) - Phase 2.3
    - AI Governance (SDAIA AI Principles) - Phase 2.3

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = '003'
down_revision = '002_auth_system'
branch_labels = None
depends_on = None


def upgrade():
    """Create all Phase 2.2 & 2.3 tables"""
    
    # ==================== PRIVACY MANAGEMENT (Phase 2.2) ====================
    
    # Consent table
    op.create_table(
        'consents',
        sa.Column('consent_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('consent_type', sa.String(50), nullable=False),
        sa.Column('purpose_en', sa.Text(), nullable=False),
        sa.Column('purpose_ar', sa.Text(), nullable=False),
        sa.Column('data_categories', postgresql.JSONB(), nullable=False),
        sa.Column('status', sa.String(20), nullable=False),
        sa.Column('given_at', sa.DateTime(), nullable=False),
        sa.Column('expires_at', sa.DateTime()),
        sa.Column('withdrawn_at', sa.DateTime()),
        sa.Column('ip_address', sa.String(50)),
        sa.Column('user_agent', sa.Text()),
        sa.Column('version', sa.Integer(), default=1),
        sa.PrimaryKeyConstraint('consent_id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ondelete='CASCADE')
    )
    op.create_index('ix_consent_user', 'consents', ['user_id'])
    op.create_index('ix_consent_type', 'consents', ['consent_type'])
    op.create_index('ix_consent_status', 'consents', ['status'])
    
    # Data Subject Access Request (DSAR) table
    op.create_table(
        'data_subject_requests',
        sa.Column('request_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('request_number', sa.String(50), unique=True, nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('request_type', sa.String(50), nullable=False),
        sa.Column('status', sa.String(20), nullable=False),
        sa.Column('description_en', sa.Text(), nullable=False),
        sa.Column('description_ar', sa.Text(), nullable=False),
        sa.Column('requested_at', sa.DateTime(), nullable=False),
        sa.Column('deadline', sa.DateTime(), nullable=False),
        sa.Column('completed_at', sa.DateTime()),
        sa.Column('response_en', sa.Text()),
        sa.Column('response_ar', sa.Text()),
        sa.Column('data_provided', postgresql.JSONB()),
        sa.Column('assigned_to', postgresql.UUID(as_uuid=True)),
        sa.PrimaryKeyConstraint('request_id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['assigned_to'], ['users.user_id'])
    )
    op.create_index('ix_dsar_number', 'data_subject_requests', ['request_number'])
    op.create_index('ix_dsar_user', 'data_subject_requests', ['user_id'])
    op.create_index('ix_dsar_status', 'data_subject_requests', ['status'])
    
    # Data Classification table
    op.create_table(
        'data_classification_tags',
        sa.Column('tag_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('resource_type', sa.String(100), nullable=False),
        sa.Column('resource_id', sa.String(255), nullable=False),
        sa.Column('classification', sa.String(20), nullable=False),
        sa.Column('sensitivity_level', sa.Integer(), nullable=False),
        sa.Column('encryption_required', sa.Boolean(), default=True),
        sa.Column('retention_period_days', sa.Integer()),
        sa.Column('legal_basis_en', sa.Text()),
        sa.Column('legal_basis_ar', sa.Text()),
        sa.Column('tagged_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tagged_at', sa.DateTime(), nullable=False),
        sa.Column('reviewed_at', sa.DateTime()),
        sa.PrimaryKeyConstraint('tag_id'),
        sa.ForeignKeyConstraint(['tagged_by'], ['users.user_id'])
    )
    op.create_index('ix_classification_resource', 'data_classification_tags', ['resource_type', 'resource_id'])
    op.create_index('ix_classification_level', 'data_classification_tags', ['classification'])
    
    # Data Breach Incident table
    op.create_table(
        'data_breach_incidents',
        sa.Column('breach_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('incident_number', sa.String(50), unique=True, nullable=False),
        sa.Column('severity', sa.String(20), nullable=False),
        sa.Column('status', sa.String(20), nullable=False),
        sa.Column('title_en', sa.String(255), nullable=False),
        sa.Column('title_ar', sa.String(255), nullable=False),
        sa.Column('description_en', sa.Text(), nullable=False),
        sa.Column('description_ar', sa.Text(), nullable=False),
        sa.Column('discovered_at', sa.DateTime(), nullable=False),
        sa.Column('reported_at', sa.DateTime(), nullable=False),
        sa.Column('affected_records_count', sa.Integer(), default=0),
        sa.Column('data_types_affected', postgresql.JSONB()),
        sa.Column('affected_individuals', postgresql.JSONB()),
        sa.Column('containment_actions_en', sa.Text()),
        sa.Column('containment_actions_ar', sa.Text()),
        sa.Column('remediation_plan_en', sa.Text()),
        sa.Column('remediation_plan_ar', sa.Text()),
        sa.Column('sdaia_notified', sa.Boolean(), default=False),
        sa.Column('sdaia_notified_at', sa.DateTime()),
        sa.Column('individuals_notified', sa.Boolean(), default=False),
        sa.Column('individuals_notified_at', sa.DateTime()),
        sa.Column('reported_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('assigned_to', postgresql.UUID(as_uuid=True)),
        sa.Column('contained_at', sa.DateTime()),
        sa.Column('resolved_at', sa.DateTime()),
        sa.PrimaryKeyConstraint('breach_id'),
        sa.ForeignKeyConstraint(['reported_by'], ['users.user_id']),
        sa.ForeignKeyConstraint(['assigned_to'], ['users.user_id'])
    )
    op.create_index('ix_breach_number', 'data_breach_incidents', ['incident_number'])
    op.create_index('ix_breach_severity', 'data_breach_incidents', ['severity'])
    op.create_index('ix_breach_status', 'data_breach_incidents', ['status'])
    
    # Data Retention Policy table
    op.create_table(
        'data_retention_policies',
        sa.Column('policy_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('data_category', sa.String(100), nullable=False),
        sa.Column('retention_period_days', sa.Integer(), nullable=False),
        sa.Column('legal_basis_en', sa.Text(), nullable=False),
        sa.Column('legal_basis_ar', sa.Text(), nullable=False),
        sa.Column('description_en', sa.Text()),
        sa.Column('description_ar', sa.Text()),
        sa.Column('auto_delete', sa.Boolean(), default=False),
        sa.Column('archive_before_delete', sa.Boolean(), default=True),
        sa.Column('applies_to', postgresql.JSONB()),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime()),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.PrimaryKeyConstraint('policy_id'),
        sa.ForeignKeyConstraint(['created_by'], ['users.user_id'])
    )
    op.create_index('ix_retention_category', 'data_retention_policies', ['data_category'])
    
    # Privacy Impact Assessment (PIA) table
    op.create_table(
        'privacy_impact_assessments',
        sa.Column('pia_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('project_name', sa.String(255), nullable=False),
        sa.Column('project_description_en', sa.Text(), nullable=False),
        sa.Column('project_description_ar', sa.Text(), nullable=False),
        sa.Column('status', sa.String(20), nullable=False),
        sa.Column('data_types_processed', postgresql.JSONB()),
        sa.Column('processing_purpose_en', sa.Text(), nullable=False),
        sa.Column('processing_purpose_ar', sa.Text(), nullable=False),
        sa.Column('legal_basis_en', sa.Text()),
        sa.Column('legal_basis_ar', sa.Text()),
        sa.Column('risk_level', sa.String(20)),
        sa.Column('privacy_risks_identified', postgresql.JSONB()),
        sa.Column('mitigation_measures_en', sa.Text()),
        sa.Column('mitigation_measures_ar', sa.Text()),
        sa.Column('dpo_consulted', sa.Boolean(), default=False),
        sa.Column('sdaia_consultation_required', sa.Boolean(), default=False),
        sa.Column('conducted_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('reviewed_by', postgresql.UUID(as_uuid=True)),
        sa.Column('conducted_at', sa.DateTime(), nullable=False),
        sa.Column('next_review_date', sa.DateTime()),
        sa.PrimaryKeyConstraint('pia_id'),
        sa.ForeignKeyConstraint(['conducted_by'], ['users.user_id']),
        sa.ForeignKeyConstraint(['reviewed_by'], ['users.user_id'])
    )
    op.create_index('ix_pia_status', 'privacy_impact_assessments', ['status'])
    
    # ==================== INCIDENT RESPONSE (Phase 2.3) ====================
    
    # Security Incident table
    op.create_table(
        'security_incidents',
        sa.Column('incident_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('incident_number', sa.String(50), unique=True, nullable=False),
        sa.Column('category', sa.String(50), nullable=False),
        sa.Column('severity', sa.String(20), nullable=False),
        sa.Column('status', sa.String(20), nullable=False),
        sa.Column('title_en', sa.String(255), nullable=False),
        sa.Column('title_ar', sa.String(255), nullable=False),
        sa.Column('description_en', sa.Text(), nullable=False),
        sa.Column('description_ar', sa.Text(), nullable=False),
        sa.Column('detected_at', sa.DateTime(), nullable=False),
        sa.Column('reported_at', sa.DateTime(), nullable=False),
        sa.Column('contained_at', sa.DateTime()),
        sa.Column('resolved_at', sa.DateTime()),
        sa.Column('closed_at', sa.DateTime()),
        sa.Column('affected_systems', postgresql.JSONB()),
        sa.Column('affected_users_count', sa.Integer(), default=0),
        sa.Column('business_impact_en', sa.Text()),
        sa.Column('business_impact_ar', sa.Text()),
        sa.Column('financial_impact', sa.Integer()),
        sa.Column('immediate_actions_en', sa.Text()),
        sa.Column('immediate_actions_ar', sa.Text()),
        sa.Column('containment_actions_en', sa.Text()),
        sa.Column('containment_actions_ar', sa.Text()),
        sa.Column('eradication_actions_en', sa.Text()),
        sa.Column('eradication_actions_ar', sa.Text()),
        sa.Column('recovery_actions_en', sa.Text()),
        sa.Column('recovery_actions_ar', sa.Text()),
        sa.Column('root_cause_en', sa.Text()),
        sa.Column('root_cause_ar', sa.Text()),
        sa.Column('lessons_learned_en', sa.Text()),
        sa.Column('lessons_learned_ar', sa.Text()),
        sa.Column('nca_reported', sa.Boolean(), default=False),
        sa.Column('nca_reported_at', sa.DateTime()),
        sa.Column('sdaia_reported', sa.Boolean(), default=False),
        sa.Column('sdaia_reported_at', sa.DateTime()),
        sa.Column('reported_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('assigned_to', postgresql.UUID(as_uuid=True)),
        sa.Column('incident_commander', postgresql.UUID(as_uuid=True)),
        sa.PrimaryKeyConstraint('incident_id'),
        sa.ForeignKeyConstraint(['reported_by'], ['users.user_id']),
        sa.ForeignKeyConstraint(['assigned_to'], ['users.user_id']),
        sa.ForeignKeyConstraint(['incident_commander'], ['users.user_id'])
    )
    op.create_index('ix_incident_number', 'security_incidents', ['incident_number'])
    op.create_index('ix_incident_severity', 'security_incidents', ['severity'])
    op.create_index('ix_incident_status', 'security_incidents', ['status'])
    
    # Incident Playbook table
    op.create_table(
        'incident_playbooks',
        sa.Column('playbook_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name_en', sa.String(255), nullable=False),
        sa.Column('name_ar', sa.String(255), nullable=False),
        sa.Column('category', sa.String(50), nullable=False),
        sa.Column('description_en', sa.Text(), nullable=False),
        sa.Column('description_ar', sa.Text(), nullable=False),
        sa.Column('detection_steps', postgresql.JSONB(), nullable=False),
        sa.Column('containment_steps', postgresql.JSONB(), nullable=False),
        sa.Column('eradication_steps', postgresql.JSONB(), nullable=False),
        sa.Column('recovery_steps', postgresql.JSONB(), nullable=False),
        sa.Column('escalation_criteria_en', sa.Text()),
        sa.Column('escalation_criteria_ar', sa.Text()),
        sa.Column('escalation_contacts', postgresql.JSONB()),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime()),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.PrimaryKeyConstraint('playbook_id'),
        sa.ForeignKeyConstraint(['created_by'], ['users.user_id'])
    )
    
    # ==================== RISK MANAGEMENT (Phase 2.3) ====================
    
    # Risk table
    op.create_table(
        'risks',
        sa.Column('risk_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('risk_number', sa.String(50), unique=True, nullable=False),
        sa.Column('category', sa.String(50), nullable=False),
        sa.Column('status', sa.String(20), nullable=False),
        sa.Column('title_en', sa.String(255), nullable=False),
        sa.Column('title_ar', sa.String(255), nullable=False),
        sa.Column('description_en', sa.Text(), nullable=False),
        sa.Column('description_ar', sa.Text(), nullable=False),
        sa.Column('likelihood', sa.Integer(), nullable=False),
        sa.Column('impact', sa.Integer(), nullable=False),
        sa.Column('inherent_risk_score', sa.Integer()),
        sa.Column('inherent_risk_level', sa.String(20)),
        sa.Column('existing_controls_en', sa.Text()),
        sa.Column('existing_controls_ar', sa.Text()),
        sa.Column('control_effectiveness', sa.Integer()),
        sa.Column('residual_likelihood', sa.Integer()),
        sa.Column('residual_impact', sa.Integer()),
        sa.Column('residual_risk_score', sa.Integer()),
        sa.Column('residual_risk_level', sa.String(20)),
        sa.Column('risk_appetite', sa.String(20)),
        sa.Column('risk_tolerance_exceeded', sa.Boolean(), default=False),
        sa.Column('treatment_strategy', sa.String(50)),
        sa.Column('treatment_plan_en', sa.Text()),
        sa.Column('treatment_plan_ar', sa.Text()),
        sa.Column('treatment_deadline', sa.DateTime()),
        sa.Column('treatment_status', sa.String(20)),
        sa.Column('treatment_cost', sa.Integer()),
        sa.Column('risk_owner', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('identified_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('identified_at', sa.DateTime(), nullable=False),
        sa.Column('last_assessed_at', sa.DateTime()),
        sa.Column('next_review_date', sa.DateTime()),
        sa.Column('closed_at', sa.DateTime()),
        sa.Column('related_controls', postgresql.JSONB()),
        sa.Column('related_incidents', postgresql.JSONB()),
        sa.PrimaryKeyConstraint('risk_id'),
        sa.ForeignKeyConstraint(['risk_owner'], ['users.user_id']),
        sa.ForeignKeyConstraint(['identified_by'], ['users.user_id'])
    )
    op.create_index('ix_risk_number', 'risks', ['risk_number'])
    op.create_index('ix_risk_category', 'risks', ['category'])
    op.create_index('ix_risk_status', 'risks', ['status'])
    
    # Risk Assessment table
    op.create_table(
        'risk_assessments',
        sa.Column('assessment_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('risk_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('assessed_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('assessed_at', sa.DateTime(), nullable=False),
        sa.Column('likelihood', sa.Integer(), nullable=False),
        sa.Column('impact', sa.Integer(), nullable=False),
        sa.Column('risk_score', sa.Integer(), nullable=False),
        sa.Column('risk_level', sa.String(20), nullable=False),
        sa.Column('notes_en', sa.Text()),
        sa.Column('notes_ar', sa.Text()),
        sa.Column('changes_since_last_en', sa.Text()),
        sa.Column('changes_since_last_ar', sa.Text()),
        sa.PrimaryKeyConstraint('assessment_id'),
        sa.ForeignKeyConstraint(['risk_id'], ['risks.risk_id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['assessed_by'], ['users.user_id'])
    )
    op.create_index('ix_assessment_risk', 'risk_assessments', ['risk_id'])
    
    # Third-party Risk table
    op.create_table(
        'third_party_risks',
        sa.Column('vendor_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('vendor_name', sa.String(255), nullable=False),
        sa.Column('vendor_type', sa.String(100), nullable=False),
        sa.Column('contact_name', sa.String(255)),
        sa.Column('contact_email', sa.String(255)),
        sa.Column('contact_phone', sa.String(50)),
        sa.Column('risk_rating', sa.String(20), nullable=False),
        sa.Column('data_access_level', sa.String(50)),
        sa.Column('services_provided_en', sa.Text(), nullable=False),
        sa.Column('services_provided_ar', sa.Text(), nullable=False),
        sa.Column('has_nca_compliance', sa.Boolean(), default=False),
        sa.Column('has_iso27001', sa.Boolean(), default=False),
        sa.Column('has_soc2', sa.Boolean(), default=False),
        sa.Column('compliance_certificates', postgresql.JSONB()),
        sa.Column('contract_start_date', sa.DateTime()),
        sa.Column('contract_end_date', sa.DateTime()),
        sa.Column('contract_value', sa.Integer()),
        sa.Column('data_processing_agreement', sa.Boolean(), default=False),
        sa.Column('last_review_date', sa.DateTime()),
        sa.Column('next_review_date', sa.DateTime()),
        sa.Column('review_frequency_days', sa.Integer(), default=365),
        sa.Column('vendor_manager', postgresql.UUID(as_uuid=True)),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('vendor_id'),
        sa.ForeignKeyConstraint(['vendor_manager'], ['users.user_id'])
    )
    op.create_index('ix_vendor_rating', 'third_party_risks', ['risk_rating'])
    
    # ==================== AI GOVERNANCE (Phase 2.3) ====================
    
    # AI Model table
    op.create_table(
        'ai_models',
        sa.Column('model_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('model_name', sa.String(255), nullable=False, unique=True),
        sa.Column('model_version', sa.String(50), nullable=False),
        sa.Column('model_type', sa.String(50), nullable=False),
        sa.Column('status', sa.String(20), nullable=False),
        sa.Column('description_en', sa.Text(), nullable=False),
        sa.Column('description_ar', sa.Text(), nullable=False),
        sa.Column('use_case_en', sa.Text(), nullable=False),
        sa.Column('use_case_ar', sa.Text(), nullable=False),
        sa.Column('framework', sa.String(100)),
        sa.Column('algorithm', sa.String(255)),
        sa.Column('input_features', postgresql.JSONB()),
        sa.Column('output_format', postgresql.JSONB()),
        sa.Column('training_data_source', sa.String(255)),
        sa.Column('training_data_size', sa.Integer()),
        sa.Column('training_data_period_start', sa.DateTime()),
        sa.Column('training_data_period_end', sa.DateTime()),
        sa.Column('data_labeling_method_en', sa.Text()),
        sa.Column('data_labeling_method_ar', sa.Text()),
        sa.Column('accuracy', sa.Float()),
        sa.Column('precision', sa.Float()),
        sa.Column('recall', sa.Float()),
        sa.Column('f1_score', sa.Float()),
        sa.Column('other_metrics', postgresql.JSONB()),
        sa.Column('bias_assessment_completed', sa.Boolean(), default=False),
        sa.Column('bias_assessment_date', sa.DateTime()),
        sa.Column('fairness_metrics', postgresql.JSONB()),
        sa.Column('known_biases_en', sa.Text()),
        sa.Column('known_biases_ar', sa.Text()),
        sa.Column('mitigation_strategies_en', sa.Text()),
        sa.Column('mitigation_strategies_ar', sa.Text()),
        sa.Column('is_explainable', sa.Boolean(), default=False),
        sa.Column('explainability_method', sa.String(255)),
        sa.Column('explanation_available', sa.Boolean(), default=False),
        sa.Column('processes_personal_data', sa.Boolean(), default=False),
        sa.Column('privacy_enhancing_techniques', postgresql.JSONB()),
        sa.Column('data_minimization_applied', sa.Boolean(), default=False),
        sa.Column('deployment_environment', sa.String(100)),
        sa.Column('api_endpoint', sa.String(500)),
        sa.Column('model_file_path', sa.String(500)),
        sa.Column('deployed_at', sa.DateTime()),
        sa.Column('last_updated_at', sa.DateTime()),
        sa.Column('performance_monitoring_enabled', sa.Boolean(), default=False),
        sa.Column('drift_detection_enabled', sa.Boolean(), default=False),
        sa.Column('last_monitored_at', sa.DateTime()),
        sa.Column('model_owner', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('model_id'),
        sa.ForeignKeyConstraint(['model_owner'], ['users.user_id']),
        sa.ForeignKeyConstraint(['created_by'], ['users.user_id'])
    )
    op.create_index('ix_model_name', 'ai_models', ['model_name'])
    op.create_index('ix_model_status', 'ai_models', ['status'])
    
    # Bias Test Result table
    op.create_table(
        'bias_test_results',
        sa.Column('test_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('model_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('test_name', sa.String(255), nullable=False),
        sa.Column('test_type', sa.String(100), nullable=False),
        sa.Column('tested_at', sa.DateTime(), nullable=False),
        sa.Column('tested_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('protected_attribute', sa.String(100), nullable=False),
        sa.Column('attribute_values', postgresql.JSONB()),
        sa.Column('bias_detected', sa.Boolean(), nullable=False),
        sa.Column('severity', sa.String(20)),
        sa.Column('bias_score', sa.Float()),
        sa.Column('fairness_metrics', postgresql.JSONB()),
        sa.Column('test_dataset_size', sa.Integer()),
        sa.Column('findings_en', sa.Text()),
        sa.Column('findings_ar', sa.Text()),
        sa.Column('recommendations_en', sa.Text()),
        sa.Column('recommendations_ar', sa.Text()),
        sa.Column('requires_action', sa.Boolean(), default=False),
        sa.Column('action_taken_en', sa.Text()),
        sa.Column('action_taken_ar', sa.Text()),
        sa.Column('retested', sa.Boolean(), default=False),
        sa.Column('retest_date', sa.DateTime()),
        sa.PrimaryKeyConstraint('test_id'),
        sa.ForeignKeyConstraint(['model_id'], ['ai_models.model_id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['tested_by'], ['users.user_id'])
    )
    op.create_index('ix_bias_test_model', 'bias_test_results', ['model_id'])
    
    # Model Audit table
    op.create_table(
        'model_audits',
        sa.Column('audit_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('model_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('event_type', sa.String(100), nullable=False),
        sa.Column('event_timestamp', sa.DateTime(), nullable=False),
        sa.Column('performed_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('changes', postgresql.JSONB()),
        sa.Column('reason_en', sa.Text()),
        sa.Column('reason_ar', sa.Text()),
        sa.Column('impact_assessment_en', sa.Text()),
        sa.Column('impact_assessment_ar', sa.Text()),
        sa.Column('requires_retraining', sa.Boolean(), default=False),
        sa.Column('requires_retesting', sa.Boolean(), default=False),
        sa.PrimaryKeyConstraint('audit_id'),
        sa.ForeignKeyConstraint(['model_id'], ['ai_models.model_id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['performed_by'], ['users.user_id'])
    )
    op.create_index('ix_model_audit_model', 'model_audits', ['model_id'])
    
    # AI Ethics Review table
    op.create_table(
        'ai_ethics_reviews',
        sa.Column('review_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('model_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('review_date', sa.DateTime(), nullable=False),
        sa.Column('reviewer', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('review_type', sa.String(50)),
        sa.Column('principle_human_centric', sa.Boolean()),
        sa.Column('principle_transparent', sa.Boolean()),
        sa.Column('principle_fair', sa.Boolean()),
        sa.Column('principle_accountable', sa.Boolean()),
        sa.Column('principle_privacy', sa.Boolean()),
        sa.Column('principle_secure', sa.Boolean()),
        sa.Column('ethical_concerns_en', sa.Text()),
        sa.Column('ethical_concerns_ar', sa.Text()),
        sa.Column('recommendations_en', sa.Text()),
        sa.Column('recommendations_ar', sa.Text()),
        sa.Column('approved', sa.Boolean(), nullable=False),
        sa.Column('approval_conditions_en', sa.Text()),
        sa.Column('approval_conditions_ar', sa.Text()),
        sa.Column('next_review_date', sa.DateTime()),
        sa.PrimaryKeyConstraint('review_id'),
        sa.ForeignKeyConstraint(['model_id'], ['ai_models.model_id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['reviewer'], ['users.user_id'])
    )
    op.create_index('ix_ethics_review_model', 'ai_ethics_reviews', ['model_id'])


def downgrade():
    """Drop all Phase 2.2 & 2.3 tables"""
    
    # AI Governance
    op.drop_table('ai_ethics_reviews')
    op.drop_table('model_audits')
    op.drop_table('bias_test_results')
    op.drop_table('ai_models')
    
    # Risk Management
    op.drop_table('third_party_risks')
    op.drop_table('risk_assessments')
    op.drop_table('risks')
    
    # Incident Response
    op.drop_table('incident_playbooks')
    op.drop_table('security_incidents')
    
    # Privacy Management
    op.drop_table('privacy_impact_assessments')
    op.drop_table('data_retention_policies')
    op.drop_table('data_breach_incidents')
    op.drop_table('data_classification_tags')
    op.drop_table('data_subject_requests')
    op.drop_table('consents')
