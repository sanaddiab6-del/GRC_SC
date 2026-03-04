"""Add organization_name to users table (idempotent)

Revision ID: a1b2c3d4e5f6
Revises: 4ecec7f4ec4f
Create Date: 2026-03-02 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import text

# revision identifiers
revision = 'a1b2c3d4e5f6'
down_revision = 'e5f6a7b8c9d0'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Add organization_name column to users table.
    Idempotent – skips if the column already exists.
    """
    conn = op.get_bind()
    result = conn.execute(
        text(
            "SELECT column_name FROM information_schema.columns "
            "WHERE table_name = 'users' AND column_name = 'organization_name'"
        )
    )
    if result.fetchone() is None:
        op.add_column(
            'users',
            sa.Column('organization_name', sa.String(255), nullable=True),
        )


def downgrade() -> None:
    """Remove organization_name from users (only if it exists)."""
    conn = op.get_bind()
    result = conn.execute(
        text(
            "SELECT column_name FROM information_schema.columns "
            "WHERE table_name = 'users' AND column_name = 'organization_name'"
        )
    )
    if result.fetchone() is not None:
        op.drop_column('users', 'organization_name')
