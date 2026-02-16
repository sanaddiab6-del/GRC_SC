"""
Phase 2.3 Migration: AI Governance & Operations
Creates tables for AI model registry, bias testing, SIEM integration, and vulnerability management

Revision ID: 003_ai_governance_siem
Revises: 002_auth_tables
Create Date: 2026-02-09
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from uuid import uuid4
from datetime import datetime
import uuid

# revision identifiers
revision = '003_ai_governance_siem'
down_revision = '002_auth_tables'
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
    """Apply AI Governance & SIEM tables"""
    
    # AI Models Registry
    op.create_table(
        'ai_models',
        sa.Column('model_id', GUID(), primary_key=True, default=uuid4),
        sa.Column('model_name', sa.String(255), nullable=False, unique=True),
        sa.Column('model_version', sa.String(50), nullable=False),
        sa.Column('model_type', sa.String(50), nullable=False),
        sa.Column('status', sa.String(50), nullable=False, default='development'),
        sa.Column('description_en', sa.Text, nullable=False),
        sa.Column('description_ar', sa.Text, nullable=False),
        sa.Column('use_case_en', sa.Text, nullable=False),
        sa.Column('use_case_ar', sa.Text, nullable=False),
        sa.Column('framework', sa.String(100)),
        sa.Column('algorithm', sa.String(255)),
        sa.Column('input_features', sa.JSON),
        sa.Column('output_format', sa.JSON),
        sa.Column('training_data_source', sa.String(255)),
        sa.Column('training_data_size', sa.Integer),
        sa.Column('training_data_period_start', sa.DateTime),
        sa.Column('training_data_period_end', sa.DateTime),
        sa.Column('data_labeling_method_en', sa.Text),
        sa.Column('data_labeling_method_ar', sa.Text),
        sa.Column('accuracy', sa.Float),
        sa.Column('precision', sa.Float),
        sa.Column('recall', sa.Float),
        sa.Column('f1_score', sa.Float),
        sa.Column('other_metrics', sa.JSON),
        sa.Column('bias_assessment_completed', sa.Boolean, default=False),
        sa.Column('bias_assessment_date', sa.DateTime),
        sa.Column('fairness_metrics', sa.JSON),
        sa.Column('known_biases_en', sa.Text),
        sa.Column('known_biases_ar', sa.Text),
        sa.Column('mitigation_strategies_en', sa.Text),
        sa.Column('mitigation_strategies_ar', sa.Text),
        sa.Column('is_explainable', sa.Boolean, default=False),
        sa.Column('explainability_method', sa.String(255)),
        sa.Column('explanation_available', sa.Boolean, default=False),
        sa.Column('processes_personal_data', sa.Boolean, default=False),
        sa.Column('privacy_enhancing_techniques', sa.JSON),
        sa.Column('data_minimization_applied', sa.Boolean, default=False),
        sa.Column('deployment_environment', sa.String(100)),
        sa.Column('api_endpoint', sa.String(500)),
        sa.Column('model_file_path', sa.String(500)),
        sa.Column('deployed_at', sa.DateTime),
        sa.Column('last_updated_at', sa.DateTime),
        sa.Column('performance_monitoring_enabled', sa.Boolean, default=False),
        sa.Column('drift_detection_enabled', sa.Boolean, default=False),
        sa.Column('last_monitored_at', sa.DateTime),
        sa.Column('model_owner', GUID(), sa.ForeignKey('users.user_id'), nullable=False),
        sa.Column('created_by', GUID(), sa.ForeignKey('users.user_id'), nullable=False),
        sa.Column('created_at', sa.DateTime, default=datetime.utcnow, nullable=False),
        sa.PrimaryKeyConstraint('model_id')
    )
    op.create_index('ix_ai_models_status', 'ai_models', ['status'])
    op.create_index('ix_ai_models_model_type', 'ai_models', ['model_type'])
    
    # Bias Test Results
    op.create_table(
        'bias_test_results',
        sa.Column('test_id', GUID(), primary_key=True, default=uuid4),
        sa.Column('model_id', GUID(), sa.ForeignKey('ai_models.model_id', ondelete='CASCADE'), nullable=False),
        sa.Column('test_name', sa.String(255), nullable=False),
        sa.Column('test_type', sa.String(100), nullable=False),
        sa.Column('tested_at', sa.DateTime, default=datetime.utcnow, nullable=False),
        sa.Column('tested_by', GUID(), sa.ForeignKey('users.user_id'), nullable=False),
        sa.Column('protected_attribute', sa.String(100), nullable=False),
        sa.Column('attribute_values', sa.JSON),
        sa.Column('bias_detected', sa.Boolean, nullable=False),
        sa.Column('severity', sa.String(20)),
        sa.Column('bias_score', sa.Float),
        sa.Column('fairness_metrics', sa.JSON),
        sa.Column('test_dataset_size', sa.Integer),
        sa.Column('findings_en', sa.Text),
        sa.Column('findings_ar', sa.Text),
        sa.Column('recommendations_en', sa.Text),
        sa.Column('recommendations_ar', sa.Text),
        sa.Column('requires_action', sa.Boolean, default=False),
        sa.Column('action_taken_en', sa.Text),
        sa.Column('action_taken_ar', sa.Text),
        sa.Column('retested', sa.Boolean, default=False),
        sa.Column('retest_date', sa.DateTime),
        sa.PrimaryKeyConstraint('test_id')
    )
    op.create_index('ix_bias_tests_model_id', 'bias_test_results', ['model_id'])
    op.create_index('ix_bias_tests_severity', 'bias_test_results', ['severity'])
    
    # Model Audit Trail
    op.create_table(
        'model_audits',
        sa.Column('audit_id', GUID(), primary_key=True, default=uuid4),
        sa.Column('model_id', GUID(), sa.ForeignKey('ai_models.model_id', ondelete='CASCADE'), nullable=False),
        sa.Column('event_type', sa.String(100), nullable=False),
        sa.Column('event_timestamp', sa.DateTime, default=datetime.utcnow, nullable=False),
        sa.Column('performed_by', GUID(), sa.ForeignKey('users.user_id'), nullable=False),
        sa.Column('changes', sa.JSON),
        sa.Column('reason_en', sa.Text),
        sa.Column('reason_ar', sa.Text),
        sa.Column('impact_assessment_en', sa.Text),
        sa.Column('impact_assessment_ar', sa.Text),
        sa.Column('requires_retraining', sa.Boolean, default=False),
        sa.Column('requires_retesting', sa.Boolean, default=False),
        sa.PrimaryKeyConstraint('audit_id')
    )
    op.create_index('ix_model_audits_model_id', 'model_audits', ['model_id'])
    
    # AI Ethics Reviews
    op.create_table(
        'ai_ethics_reviews',
        sa.Column('review_id', GUID(), primary_key=True, default=uuid4),
        sa.Column('model_id', GUID(), sa.ForeignKey('ai_models.model_id', ondelete='CASCADE'), nullable=False),
        sa.Column('review_date', sa.DateTime, default=datetime.utcnow, nullable=False),
        sa.Column('reviewer', GUID(), sa.ForeignKey('users.user_id'), nullable=False),
        sa.Column('review_type', sa.String(50)),
        sa.Column('principle_human_centric', sa.Boolean),
        sa.Column('principle_transparent', sa.Boolean),
        sa.Column('principle_fair', sa.Boolean),
        sa.Column('principle_accountable', sa.Boolean),
        sa.Column('principle_privacy', sa.Boolean),
        sa.Column('principle_secure', sa.Boolean),
        sa.Column('ethical_concerns_en', sa.Text),
        sa.Column('ethical_concerns_ar', sa.Text),
        sa.Column('recommendations_en', sa.Text),
        sa.Column('recommendations_ar', sa.Text),
        sa.Column('approved', sa.Boolean, nullable=False),
        sa.Column('approval_conditions_en', sa.Text),
        sa.Column('approval_conditions_ar', sa.Text),
        sa.Column('next_review_date', sa.DateTime),
        sa.PrimaryKeyConstraint('review_id')
    )
    
    # Security Events (SIEM)
    op.create_table(
        'security_events',
        sa.Column('event_id', GUID(), primary_key=True, default=uuid4),
        sa.Column('event_type', sa.String(100), nullable=False),
        sa.Column('severity', sa.String(50), nullable=False),
        sa.Column('event_timestamp', sa.DateTime, default=datetime.utcnow, nullable=False),
        sa.Column('source_system', sa.String(255)),
        sa.Column('source_ip', sa.String(45)),
        sa.Column('source_hostname', sa.String(255)),
        sa.Column('source_user_id', GUID(), sa.ForeignKey('users.user_id')),
        sa.Column('event_name', sa.String(255), nullable=False),
        sa.Column('event_description', sa.Text),
        sa.Column('event_data', sa.JSON),
        sa.Column('detection_rule', sa.String(255)),
        sa.Column('confidence_score', sa.Float),
        sa.Column('false_positive_likelihood', sa.Float),
        sa.Column('affected_controls', sa.JSON),
        sa.Column('compliance_impact', sa.JSON),
        sa.Column('risk_score', sa.Float),
        sa.Column('auto_response_taken', sa.Boolean, default=False),
        sa.Column('auto_response_action', sa.String(255)),
        sa.Column('requires_investigation', sa.Boolean, default=False),
        sa.Column('incident_created', sa.Boolean, default=False),
        sa.Column('incident_id', GUID()),
        sa.Column('threat_intelligence', sa.JSON),
        sa.Column('user_risk_level', sa.String(50)),
        sa.Column('asset_criticality', sa.String(50)),
        sa.Column('created_at', sa.DateTime, default=datetime.utcnow, nullable=False),
        sa.Column('processed_at', sa.DateTime),
        sa.PrimaryKeyConstraint('event_id')
    )
    op.create_index('ix_security_events_timestamp', 'security_events', ['event_timestamp'])
    op.create_index('ix_security_events_severity', 'security_events', ['severity'])
    op.create_index('ix_security_events_type', 'security_events', ['event_type'])
    
    # Security Incidents
    op.create_table(
        'security_incidents',
        sa.Column('incident_id', GUID(), primary_key=True, default=uuid4),
        sa.Column('incident_number', sa.String(50), unique=True, nullable=False),
        sa.Column('title_en', sa.String(255), nullable=False),
        sa.Column('title_ar', sa.String(255), nullable=False),
        sa.Column('description_en', sa.Text, nullable=False),
        sa.Column('description_ar', sa.Text, nullable=False),
        sa.Column('incident_type', sa.String(100), nullable=False),
        sa.Column('severity', sa.String(50), nullable=False),
        sa.Column('status', sa.String(50), nullable=False, default='new'),
        sa.Column('detected_at', sa.DateTime, default=datetime.utcnow, nullable=False),
        sa.Column('reported_at', sa.DateTime, default=datetime.utcnow, nullable=False),
        sa.Column('containment_at', sa.DateTime),
        sa.Column('eradication_at', sa.DateTime),
        sa.Column('recovery_at', sa.DateTime),
        sa.Column('closed_at', sa.DateTime),
        sa.Column('affected_systems', sa.JSON),
        sa.Column('affected_users_count', sa.Integer, default=0),
        sa.Column('data_compromised', sa.Boolean, default=False),
        sa.Column('data_types_compromised', sa.JSON),
        sa.Column('estimated_impact_usd', sa.Float),
        sa.Column('violated_controls', sa.JSON),
        sa.Column('compliance_violations', sa.JSON),
        sa.Column('regulatory_notification_required', sa.Boolean, default=False),
        sa.Column('regulatory_notification_deadline', sa.DateTime),
        sa.Column('assigned_to', GUID(), sa.ForeignKey('users.user_id')),
        sa.Column('investigation_notes', sa.Text),
        sa.Column('root_cause_en', sa.Text),
        sa.Column('root_cause_ar', sa.Text),
        sa.Column('attack_vector_en', sa.Text),
        sa.Column('attack_vector_ar', sa.Text),
        sa.Column('containment_actions', sa.JSON),
        sa.Column('eradication_actions', sa.JSON),
        sa.Column('recovery_actions', sa.JSON),
        sa.Column('lessons_learned_en', sa.Text),
        sa.Column('lessons_learned_ar', sa.Text),
        sa.Column('created_at', sa.DateTime, default=datetime.utcnow, nullable=False),
        sa.Column('updated_at', sa.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow),
        sa.PrimaryKeyConstraint('incident_id')
    )
    op.create_index('ix_security_incidents_number', 'security_incidents', ['incident_number'])
    op.create_index('ix_security_incidents_status', 'security_incidents', ['status'])
    op.create_index('ix_security_incidents_severity', 'security_incidents', ['severity'])

def downgrade():
    """Drop Phase 2.3 tables"""
    op.drop_table('security_incidents')
    op.drop_table('security_events')
    op.drop_table('ai_ethics_reviews')
    op.drop_table('model_audits')
    op.drop_table('bias_test_results')
    op.drop_table('ai_models')
