"""add_permission_descriptions

Revision ID: 44622c09d0cc
Revises: 009_backup_dr
Create Date: 2026-02-26 10:35:17.695775+00:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '44622c09d0cc'
down_revision = '009_backup_dr'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        'permissions',
        sa.Column('description_en', sa.String(), nullable=True),
    )
    op.add_column(
        'permissions',
        sa.Column('description_ar', sa.String(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column('permissions', 'description_ar')
    op.drop_column('permissions', 'description_en')
