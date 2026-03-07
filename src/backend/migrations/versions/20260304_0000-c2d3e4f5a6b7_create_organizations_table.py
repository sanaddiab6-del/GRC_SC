"""Create organizations table for multi-tenancy

Revision ID: c2d3e4f5a6b7
Revises: b7c8d9e0f1a2
Create Date: 2026-03-04 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy import text


# revision identifiers, used by Alembic.
revision = "c2d3e4f5a6b7"
down_revision = "b7c8d9e0f1a2"
branch_labels = None
depends_on = None


def _table_exists(table_name: str) -> bool:
    """Check if a table exists in the database."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    return table_name in inspector.get_table_names()


def upgrade() -> None:
    """Create organizations table if it doesn't exist (idempotent)."""
    
    # Only create table if it doesn't exist
    if not _table_exists("organizations"):
        op.create_table(
            "organizations",
            sa.Column("id", sa.Integer(), primary_key=True, index=True),
            sa.Column("name_en", sa.String(255), nullable=False),
            sa.Column("name_ar", sa.String(255), nullable=False),
            sa.Column("org_type", sa.String(50), nullable=True),
            sa.Column("parent_org_id", sa.Integer(), nullable=True),
            sa.Column("license_type", sa.String(50), nullable=True),
            sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
            sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        )
        
        # Add foreign key constraint for self-referencing parent_org_id
        op.create_foreign_key(
            "fk_organizations_parent_org_id",
            "organizations",
            "organizations",
            ["parent_org_id"],
            ["id"],
            ondelete="SET NULL"
        )
        
        # Create indexes
        op.create_index(
            "ix_organizations_parent_org_id",
            "organizations",
            ["parent_org_id"],
            unique=False
        )
        
        print("✓ Created organizations table")
    else:
        print("⊗ organizations table already exists, skipping creation")


def downgrade() -> None:
    """Drop organizations table if it exists (idempotent)."""
    
    if _table_exists("organizations"):
        # Drop the table (foreign keys will be dropped automatically due to CASCADE)
        op.drop_table("organizations")
        print("✓ Dropped organizations table")
    else:
        print("⊗ organizations table doesn't exist, skipping drop")
