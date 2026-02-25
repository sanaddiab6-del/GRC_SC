"""
Assessment Execution Migration: Complete Lifecycle Management

Creates tables for:
- Assessment Instances (Draft → Closed lifecycle)
- Assessment Responses (Control-level assessments)
- Assessment Status History (Audit trail)

Implements full NCA ECC/CCC/PDPL assessment execution workflow with:
- State machine enforcement
- RBAC authorization
- Scoring engine (compliance_score, weighted_score)
- Regulator submission tracking
- Remediation management

Revision ID: 008_assessment_execution
Revises: 007_lifecycle_tamper_versions
Create Date: 2026-02-16
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import uuid

# revision identifiers
revision = '008_assessment_execution'
down_revision = '007_lifecycle_tamper_versions'
branch_labels = None
depends_on = None


class GUID(sa.TypeDecorator):
    """Platform-independent GUID type (matches users.user_id)."""
    impl = sa.CHAR
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(postgresql.UUID())
        return dialect.type_descriptor(sa.CHAR(32))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        if dialect.name == 'postgresql':
            return str(value)
        if isinstance(value, uuid.UUID):
            return "%.32x" % value.int
        return "%.32x" % uuid.UUID(value).int

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        if not isinstance(value, uuid.UUID):
            value = uuid.UUID(value)
        return value


def upgrade():
    """Create assessment execution tables"""

    # ============================================================================
    # ASSESSMENT INSTANCES TABLE
    # ============================================================================
    op.create_table(
        'assessment_instances',

        # Primary key
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),

        # Identification
        sa.Column('assessment_id', sa.String(50), unique=True, nullable=False, index=True),
        sa.Column('name_en', sa.String(255), nullable=False),
        sa.Column('name_ar', sa.String(255), nullable=False),
        sa.Column('description_en', sa.Text, nullable=True),
        sa.Column('description_ar', sa.Text, nullable=True),

        # Assessment type and framework
        sa.Column('assessment_type', sa.String(50), nullable=False, index=True),
        sa.Column('framework', sa.String(50), nullable=False, index=True),

        # Scope definition
        sa.Column('control_scope', sa.JSON, nullable=True),  # List of control IDs
        sa.Column('domain_scope', sa.JSON, nullable=True),   # List of domain IDs

        # Ownership and assignment
        sa.Column('created_by_id', GUID(), sa.ForeignKey('users.user_id', ondelete='SET NULL'), nullable=True),
        sa.Column('assigned_assessor_id', GUID(), sa.ForeignKey('users.user_id', ondelete='SET NULL'), nullable=True, index=True),
        sa.Column('reviewer_id', GUID(), sa.ForeignKey('users.user_id', ondelete='SET NULL'), nullable=True),
        sa.Column('approver_id', GUID(), sa.ForeignKey('users.user_id', ondelete='SET NULL'), nullable=True),
        sa.Column('organization_id', sa.Integer, nullable=True),

        # Lifecycle status
        sa.Column('status', sa.String(20), nullable=False, default='DRAFT', index=True),

        # Lifecycle timestamps
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.text('CURRENT_TIMESTAMP'), onupdate=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('launched_at', sa.DateTime, nullable=True),
        sa.Column('due_date', sa.DateTime, nullable=True, index=True),
        sa.Column('submitted_at', sa.DateTime, nullable=True),
        sa.Column('reviewed_at', sa.DateTime, nullable=True),
        sa.Column('approved_at', sa.DateTime, nullable=True),
        sa.Column('closed_at', sa.DateTime, nullable=True),

        # Scope counts
        sa.Column('total_controls', sa.Integer, default=0),
        sa.Column('completed_controls', sa.Integer, default=0),
        sa.Column('progress_percentage', sa.Float, default=0.0),

        # Scoring
        sa.Column('compliance_score', sa.Float, nullable=True),
        sa.Column('weighted_score', sa.Float, nullable=True),
        sa.Column('compliant_count', sa.Integer, default=0),
        sa.Column('non_compliant_count', sa.Integer, default=0),
        sa.Column('partial_compliant_count', sa.Integer, default=0),
        sa.Column('not_applicable_count', sa.Integer, default=0),

        # Approval workflow
        sa.Column('approval_required', sa.Boolean, default=True),
        sa.Column('approval_comment', sa.Text, nullable=True),
        sa.Column('rejection_reason', sa.Text, nullable=True),

        # Regulator submission
        sa.Column('submitted_to_regulator', sa.Boolean, default=False),
        sa.Column('regulator_submission_date', sa.DateTime, nullable=True),
        sa.Column('regulator_reference_number', sa.String(100), nullable=True),
    )

    # Create composite index for common queries
    op.create_index(
        'ix_assessment_instances_status_framework',
        'assessment_instances',
        ['status', 'framework']
    )
    op.create_index(
        'ix_assessment_instances_assessor_status',
        'assessment_instances',
        ['assigned_assessor_id', 'status']
    )

    # ============================================================================
    # ASSESSMENT RESPONSES TABLE
    # ============================================================================
    op.create_table(
        'assessment_responses',

        # Primary key
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),

        # Foreign keys
        sa.Column('assessment_id', sa.Integer, sa.ForeignKey('assessment_instances.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('control_id', sa.String(50), nullable=False, index=True),

        # Compliance assessment
        sa.Column('compliance_status', sa.String(20), nullable=False),
        sa.Column('maturity_level', sa.Integer, nullable=True),  # 0-5 scale
        sa.Column('effectiveness_rating', sa.String(20), nullable=True),

        # Findings and gaps
        sa.Column('findings_en', sa.Text, nullable=True),
        sa.Column('findings_ar', sa.Text, nullable=True),
        sa.Column('gaps_identified_en', sa.Text, nullable=True),
        sa.Column('gaps_identified_ar', sa.Text, nullable=True),

        # Evidence
        sa.Column('evidence_provided', sa.Boolean, default=False),
        sa.Column('evidence_ids', sa.JSON, nullable=True),  # List of evidence IDs
        sa.Column('evidence_quality', sa.String(20), nullable=True),

        # Recommendations
        sa.Column('recommendation_en', sa.Text, nullable=True),
        sa.Column('recommendation_ar', sa.Text, nullable=True),
        sa.Column('risk_rating', sa.String(20), nullable=True),

        # Remediation tracking
        sa.Column('remediation_required', sa.Boolean, default=False),
        sa.Column('remediation_deadline', sa.DateTime, nullable=True),
        sa.Column('remediation_owner_id', GUID(), sa.ForeignKey('users.user_id', ondelete='SET NULL'), nullable=True),

        # Scoring
        sa.Column('control_weight', sa.Float, default=1.0),
        sa.Column('control_score', sa.Float, nullable=True),

        # Metadata
        sa.Column('assessed_by_id', GUID(), sa.ForeignKey('users.user_id', ondelete='SET NULL'), nullable=True),
        sa.Column('assessed_at', sa.DateTime, nullable=True),
        sa.Column('reviewer_comment', sa.Text, nullable=True),
        sa.Column('reviewed_at', sa.DateTime, nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.text('CURRENT_TIMESTAMP'), onupdate=sa.text('CURRENT_TIMESTAMP')),

        # Unique constraint: one response per control per assessment
        sa.UniqueConstraint('assessment_id', 'control_id', name='uq_assessment_control'),
    )

    # Create composite index for filtering
    op.create_index(
        'ix_assessment_responses_assessment_status',
        'assessment_responses',
        ['assessment_id', 'compliance_status']
    )

    # ============================================================================
    # ASSESSMENT STATUS HISTORY TABLE (Audit Trail)
    # ============================================================================
    op.create_table(
        'assessment_status_history',

        # Primary key
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),

        # Foreign keys
        sa.Column('assessment_id', sa.Integer, sa.ForeignKey('assessment_instances.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('from_status', sa.String(20), nullable=False),
        sa.Column('to_status', sa.String(20), nullable=False, index=True),
        sa.Column('changed_by_id', GUID(), sa.ForeignKey('users.user_id', ondelete='SET NULL'), nullable=True),

        # Audit trail
        sa.Column('changed_at', sa.DateTime, nullable=False, server_default=sa.text('CURRENT_TIMESTAMP'), index=True),
        sa.Column('comment', sa.Text, nullable=True),
        sa.Column('ip_address', sa.String(45), nullable=True),
        sa.Column('user_agent', sa.String(500), nullable=True),

        # Approval decisions
        sa.Column('approval_decision', sa.String(20), nullable=True),  # approved, rejected
        sa.Column('approval_comment', sa.Text, nullable=True),
    )

    # Create index for history queries
    op.create_index(
        'ix_assessment_status_history_assessment_timestamp',
        'assessment_status_history',
        ['assessment_id', 'changed_at']
    )


def downgrade():
    """Drop assessment execution tables"""

    # Drop in reverse order due to foreign key constraints
    op.drop_table('assessment_status_history')
    op.drop_table('assessment_responses')
    op.drop_table('assessment_instances')
