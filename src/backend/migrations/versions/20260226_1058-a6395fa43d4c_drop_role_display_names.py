"""drop_role_display_names

Revision ID: a6395fa43d4c
Revises: 2653da7e4fc8
Create Date: 2026-02-26 10:58:45.267499+00:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a6395fa43d4c'
down_revision = '2653da7e4fc8'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_column('roles', 'display_name_ar')
    op.drop_column('roles', 'display_name_en')


def downgrade() -> None:
    op.add_column(
        'roles',
        sa.Column('display_name_en', sa.String(), nullable=False),
    )
    op.add_column(
        'roles',
        sa.Column('display_name_ar', sa.String(), nullable=False),
    )
