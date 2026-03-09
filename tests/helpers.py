"""
Shared test helpers & fixtures for mocking DB sessions and auth dependencies.
Import these in individual test modules to avoid duplication.
"""

import sys, os, uuid
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime, timedelta

# Ensure backend on path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src/backend")))

os.environ.setdefault("PYTEST_RUNNING", "1")
os.environ.setdefault("SECRET_KEY", "test-secret-key-for-ci-32-chars-minimum-secure-key-12345")
os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost:5432/sico_grc_test")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379")


def make_fake_user(**overrides):
    """Build a mock User ORM object suitable for dependency injection."""
    user = MagicMock()
    user.user_id = overrides.get("user_id", uuid.uuid4())
    user.email = overrides.get("email", "testuser@example.com")
    user.full_name_en = overrides.get("full_name_en", "Test User")
    user.full_name_ar = overrides.get("full_name_ar", "مستخدم تجريبي")
    user.organization_name = overrides.get("organization_name", "Test Org")
    user.password_hash = overrides.get("password_hash", "$2b$12$FAKEHASH")
    user.is_active = overrides.get("is_active", True)
    user.is_verified = overrides.get("is_verified", True)
    user.last_login_at = overrides.get("last_login_at", datetime.utcnow())
    user.created_at = overrides.get("created_at", datetime.utcnow())
    user.failed_login_attempts = overrides.get("failed_login_attempts", 0)
    user.locked_until = overrides.get("locked_until", None)

    # Roles (list of mock Role objects)
    if "roles" in overrides:
        user.roles = overrides["roles"]
    else:
        role = MagicMock()
        role.role_name = "Admin"
        role.role_id = uuid.uuid4()
        role.created_at = datetime.utcnow()
        user.roles = [role]

    return user


def make_admin_role():
    role = MagicMock()
    role.role_name = "Admin"
    role.role_id = uuid.uuid4()
    role.created_at = datetime.utcnow()
    return role


def make_mock_db(**kwargs):
    """Create an AsyncSession mock with configurable execute results."""
    session = AsyncMock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    session.add = MagicMock()
    session.delete = AsyncMock()

    if "execute_returns" in kwargs:
        returns = kwargs["execute_returns"]
        if isinstance(returns, list):
            session.execute = AsyncMock(side_effect=returns)
        else:
            session.execute = AsyncMock(return_value=returns)
    else:
        session.execute = AsyncMock()

    if "scalar_return" in kwargs:
        session.scalar = AsyncMock(return_value=kwargs["scalar_return"])
    else:
        session.scalar = AsyncMock(return_value=0)

    return session


def make_scalar_result(value):
    """Wrap a value so that result.scalar() returns it."""
    m = MagicMock()
    m.scalar.return_value = value
    m.scalar_one_or_none.return_value = value
    return m


def make_scalars_result(items):
    """Wrap a list so that result.scalars().all() returns it."""
    m = MagicMock()
    m.scalars.return_value.all.return_value = items
    return m


def override_auth(app, fake_user=None):
    """Override auth dependencies to return *fake_user* (bypasses DB)."""
    from auth.security import get_current_user, get_current_active_user

    fu = fake_user or make_fake_user()

    async def _get_user():
        return fu

    app.dependency_overrides[get_current_user] = _get_user
    app.dependency_overrides[get_current_active_user] = _get_user
    return fu


def override_db(app, session):
    """Override get_db dependency to yield *session*."""
    from core.database import get_db

    async def _get_db():
        yield session

    app.dependency_overrides[get_db] = _get_db


def override_permission(app, permission_string: str):
    """Override require_permission dependency for a given permission."""
    from auth.security import require_permission

    dep_fn = require_permission(permission_string)

    async def _noop():
        return make_fake_user()

    app.dependency_overrides[dep_fn] = _noop


def clear_overrides(app):
    """Remove all dependency overrides."""
    app.dependency_overrides.clear()
