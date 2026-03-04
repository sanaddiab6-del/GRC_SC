"""Restore audit_log columns required by auth audit events (idempotent)

Revision ID: b7c8d9e0f1a2
Revises: a1b2c3d4e5f6
Create Date: 2026-03-02 15:10:00.000000
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy import text


# revision identifiers, used by Alembic.
revision = "b7c8d9e0f1a2"
down_revision = "a1b2c3d4e5f6"
branch_labels = None
depends_on = None


def _column_exists(table_name: str, column_name: str) -> bool:
    conn = op.get_bind()
    result = conn.execute(
        text(
            "SELECT 1 FROM information_schema.columns "
            "WHERE table_name = :table_name AND column_name = :column_name"
        ),
        {"table_name": table_name, "column_name": column_name},
    )
    return result.scalar_one_or_none() is not None


def _index_exists(index_name: str) -> bool:
    conn = op.get_bind()
    result = conn.execute(
        text("SELECT 1 FROM pg_indexes WHERE indexname = :index_name"),
        {"index_name": index_name},
    )
    return result.scalar_one_or_none() is not None


def upgrade() -> None:
    if not _column_exists("audit_logs", "resource_id"):
        op.add_column("audit_logs", sa.Column("resource_id", sa.String(length=100), nullable=True))
    if not _column_exists("audit_logs", "ip_address"):
        op.add_column("audit_logs", sa.Column("ip_address", sa.String(length=50), nullable=True))
    if not _column_exists("audit_logs", "user_agent"):
        op.add_column("audit_logs", sa.Column("user_agent", sa.String(length=500), nullable=True))
    if not _column_exists("audit_logs", "status"):
        op.add_column("audit_logs", sa.Column("status", sa.String(length=20), nullable=True))
    if not _column_exists("audit_logs", "timestamp"):
        op.add_column("audit_logs", sa.Column("timestamp", sa.DateTime(), nullable=True))

    if not _index_exists("ix_audit_logs_resource_id"):
        op.create_index("ix_audit_logs_resource_id", "audit_logs", ["resource_id"], unique=False)
    if not _index_exists("ix_audit_logs_timestamp"):
        op.create_index("ix_audit_logs_timestamp", "audit_logs", ["timestamp"], unique=False)


def downgrade() -> None:
    if _index_exists("ix_audit_logs_timestamp"):
        op.drop_index("ix_audit_logs_timestamp", table_name="audit_logs")
    if _index_exists("ix_audit_logs_resource_id"):
        op.drop_index("ix_audit_logs_resource_id", table_name="audit_logs")

    if _column_exists("audit_logs", "timestamp"):
        op.drop_column("audit_logs", "timestamp")
    if _column_exists("audit_logs", "status"):
        op.drop_column("audit_logs", "status")
    if _column_exists("audit_logs", "user_agent"):
        op.drop_column("audit_logs", "user_agent")
    if _column_exists("audit_logs", "ip_address"):
        op.drop_column("audit_logs", "ip_address")
    if _column_exists("audit_logs", "resource_id"):
        op.drop_column("audit_logs", "resource_id")
