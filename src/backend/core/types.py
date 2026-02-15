"""
Cross-database type definitions
Provides compatibility between PostgreSQL and SQLite
"""

from sqlalchemy import JSON
from sqlalchemy.dialects.postgresql import JSONB as PG_JSONB
from typing import Any

# Use JSON type which works with both PostgreSQL and SQLite
# SQLAlchemy automatically uses JSONB on PostgreSQL and TEXT on SQLite
JSONType = JSON().with_variant(PG_JSONB(), 'postgresql')
