"""
Database connection and session management
Supports both SQLite (aiosqlite) and PostgreSQL (asyncpg) via DATABASE_URL.

URL normalisation rules
-----------------------
  sqlite:///…                  → sqlite+aiosqlite:///…
  sqlite+aiosqlite:///…        → unchanged
  postgresql://…               → postgresql+asyncpg://…
  postgresql+asyncpg://…       → unchanged
  postgresql+psycopg2://…      → postgresql+asyncpg://…
  postgres://…  (shorthand)    → postgresql+asyncpg://…
"""

import os
from typing import Any, AsyncGenerator, Dict

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import NullPool
from core.config import settings


# ---------------------------------------------------------------------------
# URL helpers (importable by migrations/env.py and scripts)
# ---------------------------------------------------------------------------

def resolve_async_url(raw_url: str) -> str:
    """
    Normalise *raw_url* so it always uses the correct async driver scheme.

    Recognised schemes and their resolutions:

      sqlite:///…              → sqlite+aiosqlite:///…
      sqlite+aiosqlite:///…    → unchanged
      postgresql://…           → postgresql+asyncpg://…
      postgresql+asyncpg://…   → unchanged
      postgresql+psycopg2://…  → postgresql+asyncpg://…
      postgres://…             → postgresql+asyncpg://…
    """
    url = raw_url.strip()

    # --- SQLite ---
    if url.startswith("sqlite"):
        if "+aiosqlite" not in url:
            url = url.replace("sqlite://", "sqlite+aiosqlite://", 1)
        return url

    # --- PostgreSQL (including the heroku-style "postgres://" shorthand) ---
    if url.startswith("postgres"):
        # Normalise the postgres:// shorthand first
        url = url.replace("postgres://", "postgresql://", 1)
        if "+asyncpg" in url:
            return url
        # Strip any other driver specifier (e.g. +psycopg2) and inject asyncpg
        if "+" in url:
            scheme_part, rest = url.split("://", 1)
            base_scheme = scheme_part.split("+")[0]      # e.g. "postgresql"
            url = f"{base_scheme}+asyncpg://{rest}"
        else:
            url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
        return url

    # Unknown scheme — pass through unchanged so the error surfaces in SQLAlchemy
    return url


def resolve_sync_url(async_url: str) -> str:
    """
    Convert an async-driver URL to its synchronous equivalent.

    Used by Alembic migrations and direct-SQL helper scripts that cannot
    accept an async driver specifier.

      sqlite+aiosqlite:///…    → sqlite:///…
      postgresql+asyncpg://…   → postgresql://…
    """
    url = async_url.strip()
    url = url.replace("sqlite+aiosqlite://", "sqlite://")
    url = url.replace("postgresql+asyncpg://", "postgresql://")
    return url


# ---------------------------------------------------------------------------
# Engine setup
# ---------------------------------------------------------------------------

DATABASE_URL: str = resolve_async_url(settings.DATABASE_URL)
is_postgresql: bool = True   # SQLite is not supported; PostgreSQL only

use_null_pool: bool = (
    bool(os.getenv("PYTEST_RUNNING"))
    or bool(os.getenv("PYTEST_CURRENT_TEST"))
)

engine_kwargs: Dict[str, Any] = {
    "echo": settings.DATABASE_ECHO,
    "future": True,
}

if use_null_pool:
    # Tests use NullPool to avoid connection-pool interference.
    engine_kwargs["poolclass"] = NullPool
else:
    # PostgreSQL connection pool defaults.
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
    try:
        import regulatory_versions as _reg_versions  # noqa: F401
    except Exception:
        pass
    # Enterprise models are required for organization and enterprise-user FKs
    import enterprise_models as _enterprise_models  # noqa: F401


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


async def validate_db_startup() -> bool:
    """
    Perform lightweight startup validation against the configured database.

    Checks
    ------
    1. **Connectivity** – runs ``SELECT 1`` to confirm the engine can reach
       the database server or file.
    2. **Migration state** – reads ``alembic_version`` to verify that at
       least one migration has been applied.  A missing or empty table emits
       a WARNING rather than raising an exception so that a fresh development
       environment (before the first ``alembic upgrade head``) is never
       blocked from starting.

    Returns
    -------
    bool
        ``True``  – connection succeeded (migration warnings do not affect
                    this value).
        ``False`` – connection itself failed; app will run in API-only mode.
    """
    import logging
    from sqlalchemy import text
    from urllib.parse import urlparse

    _log = logging.getLogger(__name__)

    # Mask any password embedded in the URL before logging.
    try:
        parsed = urlparse(DATABASE_URL)
        if parsed.password:
            safe_url = DATABASE_URL.replace(parsed.password, "***")
        else:
            safe_url = DATABASE_URL
    except Exception:
        safe_url = DATABASE_URL

    _log.info("  DB backend : postgresql")
    _log.info("  DB URL     : %s", safe_url)

    # ── 1. Connectivity ──────────────────────────────────────────────────
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        _log.info("\u2713 Database connection OK")
    except Exception as exc:
        _log.error(
            "\u2717 Database connection FAILED – the application will run in "
            "API-only mode until the database is reachable.\n"
            "  Backend : postgresql\n"
            "  URL     : %s\n"
            "  Error   : %s",
            safe_url,
            exc,
        )
        return False

    # ── 2. Migration state ───────────────────────────────────────────────
    try:
        async with engine.connect() as conn:
            result = await conn.execute(
                text("SELECT version_num FROM alembic_version")
            )
            rows = result.fetchall()

        if not rows:
            _log.warning(
                "\u26a0\ufe0f  alembic_version table is empty – no migrations have been "
                "applied yet.  Run: alembic upgrade head"
            )
        else:
            applied = ", ".join(r[0] for r in rows)
            _log.info("\u2713 Migrations applied: %s", applied)

    except Exception as exc:
        err_lower = str(exc).lower()
        if (
            "does not exist" in err_lower       # PostgreSQL
            or "alembic_version" in err_lower
        ):
            _log.warning(
                "\u26a0\ufe0f  alembic_version table not found – migrations may not have "
                "been run yet.  Run: alembic upgrade head"
            )
        else:
            _log.warning("\u26a0\ufe0f  Could not read migration state: %s", exc)

    return True


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