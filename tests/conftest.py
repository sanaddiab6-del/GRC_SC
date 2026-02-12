# Pytest configuration
import os
import sys
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config

# Set test environment variables before any imports
os.environ.setdefault("PYTEST_RUNNING", "1")
os.environ.setdefault("SECRET_KEY", "test-secret-key-for-ci-32-chars-minimum-secure-key-12345")
os.environ.setdefault("DATABASE_URL", "postgresql://sico:test_password@localhost:5432/sico_test")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379")

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src/backend")))


@pytest.fixture(scope="session", autouse=True)
def apply_migrations() -> None:
	"""Apply Alembic migrations before running API tests.
	
	Database schema is created via migrations, not FastAPI lifespan.
	httpx 0.27+ ASGITransport handles lifespan events automatically.
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
		print("   Tests will run with limited functionality")
		# Don't fail - allow tests to run even if DB is not available
