"""
Database Configuration
SQLAlchemy async session management
"""

import os
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Get database URL from environment (fallback for development)
try:
    from src.backend.core.secrets import get_secret
    DATABASE_URL = get_secret("DATABASE-URL")
except (ImportError, ValueError):
    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://user:pass@localhost:5432/sanadcom"
    )

# Create async engine
engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

# Create async session factory
async_session_maker = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Base class for models
Base = declarative_base()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for getting async database session
    
    Usage:
        @router.get("/items")
        async def get_items(db: AsyncSession = Depends(get_db)):
            ...
    """
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
