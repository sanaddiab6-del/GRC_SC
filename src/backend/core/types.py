"""
Cross-database type definitions
PostgreSQL database types and compatibility layer
"""

from sqlalchemy import JSON
from sqlalchemy.dialects.postgresql import JSONB as PG_JSONB
from typing import Any

# Use JSONB type for PostgreSQL (native JSON with indexing support)
JSONType = JSON().with_variant(PG_JSONB(), 'postgresql')
