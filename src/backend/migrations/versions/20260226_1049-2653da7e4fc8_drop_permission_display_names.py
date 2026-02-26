"""drop_permission_display_names

Revision ID: 2653da7e4fc8
Revises: 44622c09d0cc
Create Date: 2026-02-26 10:49:18.473564+00:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2653da7e4fc8'
down_revision = '44622c09d0cc'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_column('permissions', 'display_name_ar')
    op.drop_column('permissions', 'display_name_en')


def downgrade() -> None:
    op.add_column(
        'permissions',
        sa.Column('display_name_en', sa.String(), nullable=False),
    )
    op.add_column(
        'permissions',
        sa.Column('display_name_ar', sa.String(), nullable=False),
    )
