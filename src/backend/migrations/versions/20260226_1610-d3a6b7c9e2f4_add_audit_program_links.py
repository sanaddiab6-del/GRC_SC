"""
Add audit program foreign keys to audit_engagements and audit_findings

Revision ID: d3a6b7c9e2f4
Revises: 004_isms_training_audit
Create Date: 2026-02-26 16:10:00.000000
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "d3a6b7c9e2f4"
down_revision = "004_isms_training_audit"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "audit_findings",
        sa.Column("program_id", sa.Integer(), nullable=False),
    )
    op.create_foreign_key(
        "fk_audit_engagements_program_id",
        "audit_engagements",
        "audit_programs",
        ["program_id"],
        ["program_id"],
    )
    op.create_foreign_key(
        "fk_audit_findings_program_id",
        "audit_findings",
        "audit_programs",
        ["program_id"],
        ["program_id"],
    )


def downgrade() -> None:
    op.drop_constraint(
        "fk_audit_findings_program_id",
        "audit_findings",
        type_="foreignkey",
    )
    op.drop_constraint(
        "fk_audit_engagements_program_id",
        "audit_engagements",
        type_="foreignkey",
    )
    op.drop_column("audit_findings", "program_id")
