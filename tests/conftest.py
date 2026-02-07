# Pytest configuration
import os
import sys
from pathlib import Path
import functools

import pytest
import httpx
from alembic import command
from alembic.config import Config

os.environ.setdefault("PYTEST_RUNNING", "1")

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src/backend")))


@pytest.fixture(scope="session", autouse=True)
def apply_migrations() -> None:
	"""Apply Alembic migrations before running API tests."""
	repo_root = Path(__file__).resolve().parents[1]
	backend_dir = repo_root / "src" / "backend"
	alembic_cfg = Config(str(backend_dir / "alembic.ini"))
	alembic_cfg.set_main_option("script_location", str(backend_dir / "migrations"))

	database_url = os.getenv("DATABASE_URL")
	if database_url:
		alembic_cfg.set_main_option("sqlalchemy.url", database_url)

	command.upgrade(alembic_cfg, "head")


@pytest.fixture(autouse=True)
def enable_asgi_lifespan(monkeypatch: pytest.MonkeyPatch) -> None:
	"""Ensure FastAPI startup/shutdown events run in tests."""
	monkeypatch.setattr(
		httpx,
		"ASGITransport",
		functools.partial(httpx.ASGITransport, lifespan="on"),
	)
