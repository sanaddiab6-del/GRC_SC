from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context
import sys
from pathlib import Path

# Add src/backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.database import Base
from core.config import settings
import os

# Import ALL models to ensure they're registered with Base.metadata
try:
    from controls.models import Control
    from evidence.models import Evidence
    from reporting.models import Report
    from auth.models import User, Role, Permission
    from privacy.models import ProcessingActivity, DataSubjectRequest, DataBreach
    from incident.models import Incident, IncidentWorkflowLog
    from risk.models import Risk, RiskAssessment
    from ai_governance.models import AIModel, BiasTestResult, AIPerformanceMetric, EthicalReview
    from siem.models import SecurityEvent, ThreatIntelligence, SecurityAlert
    from isms.models import Asset, Vendor
    from training.models import TrainingModule, TrainingCompletion
    from audit.models import AuditFinding, AuditWorkflow
    import enterprise_models  # Import all enterprise models
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
# Convert async URLs to sync for Alembic
database_url = os.getenv("DATABASE_URL", settings.DATABASE_URL)
if "postgresql+asyncpg://" in database_url:
    database_url = database_url.replace("postgresql+asyncpg://", "postgresql://")
elif "sqlite+aiosqlite://" in database_url:
    database_url = database_url.replace("sqlite+aiosqlite://", "sqlite://")
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


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

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

