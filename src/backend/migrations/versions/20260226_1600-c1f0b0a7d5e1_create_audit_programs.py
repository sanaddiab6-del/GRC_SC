"""
Create audit_programs table

Revision ID: c1f0b0a7d5e1
Revises: 003_ai_governance_siem
Create Date: 2026-02-26 16:00:00.000000
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import uuid


# revision identifiers, used by Alembic.
revision = "c1f0b0a7d5e1"
down_revision = "003_ai_governance_siem"
branch_labels = None
depends_on = None


class GUID(sa.TypeDecorator):
    """Platform-independent GUID type (matches users.user_id)."""
    impl = sa.CHAR
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(postgresql.UUID())
        return dialect.type_descriptor(sa.CHAR(32))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        if dialect.name == "postgresql":
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


def upgrade() -> None:
    op.create_table(
        "audit_programs",
        sa.Column("program_id", sa.Integer(), nullable=False),
        sa.Column("program_code", sa.String(50), nullable=False),
        sa.Column("title_en", sa.String(500), nullable=False),
        sa.Column("title_ar", sa.String(500), nullable=False),
        sa.Column("description_en", sa.Text(), nullable=True),
        sa.Column("description_ar", sa.Text(), nullable=True),
        sa.Column("audit_year", sa.Integer(), nullable=False),
        sa.Column(
            "audit_type",
            sa.Enum(
                "internal",
                "external_certification",
                "external_surveillance",
                "external_recertification",
                "regulatory",
                "third_party",
                "soc2_type1",
                "soc2_type2",
                name="audittype",
                native_enum=False,
            ),
            nullable=False,
        ),
        sa.Column("scope_description_en", sa.Text(), nullable=False),
        sa.Column("scope_description_ar", sa.Text(), nullable=False),
        sa.Column("iso27001_in_scope", sa.Boolean(), nullable=False, default=True),
        sa.Column("iso27017_in_scope", sa.Boolean(), nullable=False, default=False),
        sa.Column("iso27018_in_scope", sa.Boolean(), nullable=False, default=False),
        sa.Column("iso27701_in_scope", sa.Boolean(), nullable=False, default=False),
        sa.Column("nca_ecc_in_scope", sa.Boolean(), nullable=False, default=True),
        sa.Column("nca_ccc_in_scope", sa.Boolean(), nullable=False, default=True),
        sa.Column("pdpl_in_scope", sa.Boolean(), nullable=False, default=True),
        sa.Column("sdaia_ai_in_scope", sa.Boolean(), nullable=False, default=False),
        sa.Column("planned_start_date", sa.DateTime(), nullable=False),
        sa.Column("planned_end_date", sa.DateTime(), nullable=False),
        sa.Column("actual_start_date", sa.DateTime(), nullable=True),
        sa.Column("actual_end_date", sa.DateTime(), nullable=True),
        sa.Column("lead_auditor_id", GUID(), nullable=True),
        sa.Column("audit_team_ids", sa.JSON(), nullable=True),
        sa.Column("external_auditor_firm", sa.String(500), nullable=True),
        sa.Column("external_auditor_contact", sa.JSON(), nullable=True),
        sa.Column(
            "status",
            sa.Enum(
                "planned",
                "in_preparation",
                "in_progress",
                "pending_response",
                "under_review",
                "completed",
                "cancelled",
                name="auditstatus",
                native_enum=False,
            ),
            nullable=False,
            default="planned",
        ),
        sa.Column("total_findings", sa.Integer(), nullable=False, default=0),
        sa.Column("critical_findings", sa.Integer(), nullable=False, default=0),
        sa.Column("high_findings", sa.Integer(), nullable=False, default=0),
        sa.Column("medium_findings", sa.Integer(), nullable=False, default=0),
        sa.Column("low_findings", sa.Integer(), nullable=False, default=0),
        sa.Column("observations", sa.Integer(), nullable=False, default=0),
        sa.Column("certification_body", sa.String(500), nullable=True),
        sa.Column("certificate_number", sa.String(200), nullable=True),
        sa.Column("certificate_issue_date", sa.DateTime(), nullable=True),
        sa.Column("certificate_expiry_date", sa.DateTime(), nullable=True),
        sa.Column("certification_scope_en", sa.Text(), nullable=True),
        sa.Column("certification_scope_ar", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["lead_auditor_id"], ["users.user_id"]),
        sa.PrimaryKeyConstraint("program_id"),
    )
    op.create_index("ix_audit_programs_program_id", "audit_programs", ["program_id"])
    op.create_index(
        "ix_audit_programs_program_code",
        "audit_programs",
        ["program_code"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index("ix_audit_programs_program_code", table_name="audit_programs")
    op.drop_index("ix_audit_programs_program_id", table_name="audit_programs")
    op.drop_table("audit_programs")
