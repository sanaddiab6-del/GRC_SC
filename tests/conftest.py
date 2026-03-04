# Pytest configuration
import asyncio
import os
import sys
from pathlib import Path
import pytest_asyncio

import pytest
from httpx import ASGITransport, AsyncClient
from alembic import command
from alembic.config import Config

# Set test environment variables before any imports
os.environ.setdefault("PYTEST_RUNNING", "1")
os.environ.setdefault("SECRET_KEY", "test-secret-key-for-ci-32-chars-minimum-secure-key-12345")
os.environ.setdefault("DATABASE_URL", "postgresql://sico:test_password@localhost:5432/sico_test")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379")

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src/backend")))

@pytest_asyncio.fixture
async def test_client():
	"""Provide an async HTTP client bound to the FastAPI app."""
	from main import app
	async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
		yield client

@pytest.fixture(scope="session", autouse=True)
def apply_migrations() -> None:
	"""Apply Alembic migrations before running API tests.

	Falls back to creating tables via SQLAlchemy metadata for SQLite
	(which does not support all PostgreSQL migration operations).
	"""
	try:
		repo_root = Path(__file__).resolve().parents[1]
		backend_dir = repo_root / "src" / "backend"
		alembic_cfg = Config(str(backend_dir / "alembic.ini"))
		alembic_cfg.set_main_option("script_location", str(backend_dir / "migrations"))

		database_url = os.getenv("DATABASE_URL")
		if database_url:
			alembic_cfg.set_main_option("sqlalchemy.url", database_url)

		command.upgrade(alembic_cfg, "head")
		print("✓ Database migrations applied successfully")
	except Exception as e:
		print(f"⚠️  Database migration failed: {e}")
		print("   Falling back to SQLAlchemy create_all for test schema")
		# Fallback: drop and recreate all tables from current models (safe for test env)
		try:
			async def _recreate_db():
				from sqlalchemy.ext.asyncio import create_async_engine
				from core.config import settings
				from core.database import Base
				from core.database import _load_models
				_load_models()
				try:
					import regulatory_versions  # noqa: F401
				except Exception:
					pass
				engine = create_async_engine(settings.DATABASE_URL)
				async with engine.begin() as conn:
					await conn.run_sync(Base.metadata.drop_all)
					await conn.run_sync(Base.metadata.create_all)
				await engine.dispose()

			asyncio.run(_recreate_db())
			print("✓ Database schema created via SQLAlchemy models")
		except Exception as e2:
			print(f"⚠️  Fallback schema creation also failed: {e2}")
			print("   Tests will run with limited functionality")
