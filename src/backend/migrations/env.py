from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context
import sys
from pathlib import Path

# Add src/backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.database import Base, resolve_sync_url
from core.config import settings
import os

# Import ALL models to ensure they're registered with Base.metadata
try:
    from controls.models import Control
    from evidence.models import Evidence
    from reporting.models import Report
    from auth.models import User, Role, Permission
    from privacy.models import Consent, DataSubjectRequest, DataBreachIncident
    from incident.models import SecurityIncident, IncidentPlaybook
    from risk.models import Risk, RiskAssessment
    from ai_governance.models import AIModel, BiasTestResult, ModelAudit, AIEthicsReview
    from siem.models import SecurityEvent, ThreatIntelligence, VulnerabilityScan
    from isms.models import ISMSPolicy, AssetInventory
    from training.models import TrainingCourse, TrainingEnrollment
    from audit.models import AuditFinding, AuditEngagement
    from dynamic_config import models as _dynamic_config_models  # noqa: F401
    import enterprise_models  # Import all enterprise models
    try:
        from regulatory_versions import FrameworkVersion  # noqa: F401
    except ImportError:
        pass
except ImportError as e:
    print(f"Warning: Could not import some models: {e}")
    print("Database metadata may be incomplete")

# Alembic Config object
config = context.config

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set target metadata
target_metadata = Base.metadata

# Override sqlalchemy.url from environment
# Prefer DATABASE_URL_SYNC (already a sync URL), then fall back to
# DATABASE_URL after stripping the asyncpg driver prefix.
database_url = os.getenv("DATABASE_URL_SYNC") or resolve_sync_url(
    os.getenv("DATABASE_URL", settings.DATABASE_URL)
)
config.set_main_option("sqlalchemy.url", database_url)


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


import asyncio

def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    asyncpg is an async-only driver that Alembic cannot use directly.
    We therefore derive the equivalent synchronous URL and build a
    regular (sync) engine for migration execution.
    """
    url = config.get_main_option("sqlalchemy.url")

    from sqlalchemy import create_engine
    connectable = create_engine(url, poolclass=pool.NullPool)

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

