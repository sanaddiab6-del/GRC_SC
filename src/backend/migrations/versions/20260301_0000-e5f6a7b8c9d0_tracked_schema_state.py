"""Placeholder for database state at e5f6a7b8c9d0
(schema was previously applied outside migration tracking)

Revision ID: e5f6a7b8c9d0
Revises: 4ecec7f4ec4f
Create Date: 2026-03-01 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = 'e5f6a7b8c9d0'
down_revision = '4ecec7f4ec4f'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """No-op – database was already in this state."""
    pass


def downgrade() -> None:
    """No-op."""
    pass
