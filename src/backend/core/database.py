"""
Database connection and session management
Uses SQLAlchemy 2.0 async pattern
"""

import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import NullPool
from core.config import settings

# Convert postgresql:// to postgresql+asyncpg://
DATABASE_URL = settings.DATABASE_URL.replace(
    "postgresql://", "postgresql+asyncpg://"
)

# Create async engine
use_null_pool = bool(os.getenv("PYTEST_RUNNING")) or bool(os.getenv("PYTEST_CURRENT_TEST"))
engine_kwargs = {
    "echo": settings.DATABASE_ECHO,
    "future": True,
    "pool_pre_ping": True,
    "pool_size": 10,
    "max_overflow": 20,
}

if use_null_pool:
    engine_kwargs["poolclass"] = NullPool

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


async def init_db():
    """
    Initialize database - create tables
    Handles connection errors gracefully for development
    """
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    except Exception as e:
        # Re-raise to let caller handle
        raise Exception(f"Database initialization failed: {str(e)}") from e


async def get_db():
    """Dependency for FastAPI routes"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
