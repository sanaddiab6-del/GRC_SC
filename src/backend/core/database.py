"""
Database connection and session management
Uses SQLAlchemy 2.0 async pattern
"""

import os
from typing import Any, AsyncGenerator, Dict

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import NullPool
from core.config import settings

# Convert postgresql:// to postgresql+asyncpg:// if needed
if settings.DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = settings.DATABASE_URL.replace(
        "postgresql://", "postgresql+asyncpg://"
    )
else:
    DATABASE_URL = settings.DATABASE_URL

# Create async engine
use_null_pool = bool(os.getenv("PYTEST_RUNNING")) or bool(os.getenv("PYTEST_CURRENT_TEST"))
is_sqlite = "sqlite" in DATABASE_URL

engine_kwargs: Dict[str, Any] = {
    "echo": settings.DATABASE_ECHO,
    "future": True,
}

if use_null_pool or is_sqlite:
    engine_kwargs["poolclass"] = NullPool
else:
    engine_kwargs["pool_pre_ping"] = True
    engine_kwargs["pool_size"] = 10
    engine_kwargs["max_overflow"] = 20

engine = create_async_engine(DATABASE_URL, **engine_kwargs)

# Session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)

# Base class for models
Base = declarative_base()


def _load_models() -> None:
    """Import models to register tables with SQLAlchemy metadata."""
    # Local imports to avoid circular dependencies at module import time.
    from controls import models as _controls_models  # noqa: F401
    from evidence import models as _evidence_models  # noqa: F401
    from reporting import models as _reporting_models  # noqa: F401
    from auth import models as _auth_models  # noqa: F401
    from privacy import models as _privacy_models  # noqa: F401
    from incident import models as _incident_models  # noqa: F401
    from risk import models as _risk_models  # noqa: F401
    from ai_governance import models as _ai_governance_models  # noqa: F401
    from siem import models as _siem_models  # noqa: F401
    from isms import models as _isms_models  # noqa: F401
    from training import models as _training_models  # noqa: F401
    from audit import models as _audit_models  # noqa: F401
    # Disabled to avoid duplicate table definitions (models already in module-specific files)
    # import enterprise_models as _enterprise_models  # noqa: F401 - Enterprise GRC


async def init_db():
    """
    Initialize database - create tables
    Handles connection errors gracefully for development
    """
    try:
        _load_models()
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    except Exception as e:
        # Re-raise to let caller handle
        raise Exception(f"Database initialization failed: {str(e)}") from e


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for FastAPI routes

    Usage:
        @router.get("/items")
        async def get_items(db: AsyncSession = Depends(get_db)):
            ...
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()