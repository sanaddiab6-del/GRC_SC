"""
Tests for core/database.py — URL resolution helpers and settings.
"""
import pytest


# ─── resolve_async_url ────────────────────────────────────────────────────────

def test_resolve_async_url_already_async():
    from core.database import resolve_async_url

    url = "postgresql+asyncpg://user:pass@localhost:5432/db"
    assert resolve_async_url(url) == url


def test_resolve_async_url_plain_postgresql():
    from core.database import resolve_async_url

    url = "postgresql://user:pass@localhost:5432/db"
    result = resolve_async_url(url)
    assert "+asyncpg" in result
    assert result == "postgresql+asyncpg://user:pass@localhost:5432/db"


def test_resolve_async_url_postgres_shorthand():
    from core.database import resolve_async_url

    url = "postgres://user:pass@host:5432/db"
    result = resolve_async_url(url)
    assert "postgresql+asyncpg://" in result


def test_resolve_async_url_psycopg2():
    from core.database import resolve_async_url

    url = "postgresql+psycopg2://user:pass@localhost:5432/db"
    result = resolve_async_url(url)
    assert "+asyncpg" in result
    assert "+psycopg2" not in result


def test_resolve_async_url_unknown_scheme():
    from core.database import resolve_async_url

    url = "sqlite:///test.db"
    # Unknown scheme passes through unchanged
    assert resolve_async_url(url) == url


def test_resolve_async_url_whitespace():
    from core.database import resolve_async_url

    url = "  postgresql://u:p@h:5432/db  "
    result = resolve_async_url(url)
    assert not result.startswith(" ")
    assert "+asyncpg" in result


# ─── resolve_sync_url ────────────────────────────────────────────────────────

def test_resolve_sync_url():
    from core.database import resolve_sync_url

    url = "postgresql+asyncpg://user:pass@localhost:5432/db"
    result = resolve_sync_url(url)
    assert result == "postgresql://user:pass@localhost:5432/db"
    assert "+asyncpg" not in result


def test_resolve_sync_url_already_sync():
    from core.database import resolve_sync_url

    url = "postgresql://user:pass@localhost:5432/db"
    assert resolve_sync_url(url) == url


# ─── Settings ────────────────────────────────────────────────────────────────

def test_settings_db_backend():
    from core.config import settings

    assert settings.db_backend == "postgresql"


def test_settings_supported_frameworks():
    from core.config import settings

    assert "ECC" in settings.SUPPORTED_FRAMEWORKS
    assert "CCC" in settings.SUPPORTED_FRAMEWORKS
    assert "PDPL" in settings.SUPPORTED_FRAMEWORKS


def test_settings_not_production_in_tests():
    from core.config import settings

    assert not settings.is_production


def test_settings_defaults():
    from core.config import settings

    assert settings.APP_NAME == "SICO GRC Platform"
    assert settings.API_V1_PREFIX == "/api/v1"
    assert settings.DEFAULT_LANGUAGE == "ar"
    assert settings.AUDIT_LOG_RETENTION_YEARS == 7
    assert settings.RATE_LIMIT_ENABLED is False
