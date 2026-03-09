"""
Auth router tests — register, login, logout, refresh, profile, admin endpoints.
All DB and password-hashing operations are mocked.
"""
import pytest
import uuid
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta
from httpx import AsyncClient, ASGITransport


def _fake_user(**kw):
    u = MagicMock()
    u.user_id = kw.get("user_id", uuid.uuid4())
    u.email = kw.get("email", "user@example.com")
    u.full_name_en = kw.get("full_name_en", "Test")
    u.full_name_ar = kw.get("full_name_ar", "تجريبي")
    u.organization_name = kw.get("organization_name", "Org")
    u.password_hash = kw.get("password_hash", "$2b$12$HASH")
    u.is_active = kw.get("is_active", True)
    u.is_verified = kw.get("is_verified", True)
    u.last_login_at = kw.get("last_login_at", datetime.utcnow())
    u.created_at = kw.get("created_at", datetime.utcnow())
    u.failed_login_attempts = kw.get("failed_login_attempts", 0)
    u.locked_until = kw.get("locked_until", None)
    role = MagicMock()
    role.role_name = kw.get("role", "Admin")
    role.role_id = uuid.uuid4()
    role.created_at = datetime.utcnow()
    u.roles = kw.get("roles", [role])
    return u


def _setup(app, session, user=None):
    from core.database import get_db

    async def _db():
        yield session

    app.dependency_overrides[get_db] = _db

    if user:
        from auth.security import get_current_user, get_current_active_user

        async def _u():
            return user

        app.dependency_overrides[get_current_user] = _u
        app.dependency_overrides[get_current_active_user] = _u


def _teardown(app):
    app.dependency_overrides.clear()


# ─── Register ────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_register_success():
    from main import app

    session = AsyncMock()
    # First execute: check existing user (None)
    exists_result = MagicMock()
    exists_result.scalar_one_or_none.return_value = None
    # Second execute: re-fetch after commit (selectinload)
    new_user = _fake_user(is_active=False, is_verified=False, roles=[])
    refetch_result = MagicMock()
    refetch_result.scalar_one.return_value = new_user
    session.execute = AsyncMock(side_effect=[exists_result, refetch_result])
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    session.add = MagicMock()

    _setup(app, session)
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
            r = await c.post("/api/v1/auth/register", json={
                "email": "new@example.com",
                "password": "StrongPass123!@#",
                "full_name_en": "New User",
                "full_name_ar": "مستخدم جديد",
            })
        assert r.status_code == 201
    finally:
        _teardown(app)


@pytest.mark.asyncio
async def test_register_duplicate_email():
    from main import app

    session = AsyncMock()
    existing = _fake_user()
    result = MagicMock()
    result.scalar_one_or_none.return_value = existing
    session.execute = AsyncMock(return_value=result)

    _setup(app, session)
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
            r = await c.post("/api/v1/auth/register", json={
                "email": "user@example.com",
                "password": "StrongPass123!@#",
                "full_name_en": "Dup",
                "full_name_ar": "مكرر",
            })
        assert r.status_code == 409
    finally:
        _teardown(app)


@pytest.mark.asyncio
async def test_register_weak_password():
    from main import app

    session = AsyncMock()
    _setup(app, session)
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
            r = await c.post("/api/v1/auth/register", json={
                "email": "weak@example.com",
                "password": "short",
                "full_name_en": "W",
                "full_name_ar": "ض",
            })
        assert r.status_code == 422  # validation error
    finally:
        _teardown(app)


# ─── Login ───────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
@patch("auth.router.verify_password", return_value=True)
@patch("auth.router.create_access_token", return_value="fake-access")
@patch("auth.router.create_refresh_token", return_value="fake-refresh")
@patch("auth.router.hash_token", return_value="hashed")
@patch("auth.router.log_audit_event", new_callable=AsyncMock)
async def test_login_success(mock_audit, mock_hash, mock_rt, mock_at, mock_verify):
    from main import app

    user = _fake_user(is_active=True)
    session = AsyncMock()
    result = MagicMock()
    result.scalar_one_or_none.return_value = user
    session.execute = AsyncMock(return_value=result)
    session.commit = AsyncMock()
    session.add = MagicMock()

    _setup(app, session)
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
            r = await c.post("/api/v1/auth/login", data={
                "username": "user@example.com",
                "password": "StrongPass123!@#",
            })
        assert r.status_code == 200
        data = r.json()
        assert data["access_token"] == "fake-access"
        assert data["token_type"] == "bearer"
    finally:
        _teardown(app)


@pytest.mark.asyncio
async def test_login_unknown_user():
    from main import app

    session = AsyncMock()
    result = MagicMock()
    result.scalar_one_or_none.return_value = None
    session.execute = AsyncMock(return_value=result)

    _setup(app, session)
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
            r = await c.post("/api/v1/auth/login", data={
                "username": "nobody@example.com",
                "password": "StrongPass123!@#",
            })
        assert r.status_code == 401
    finally:
        _teardown(app)


@pytest.mark.asyncio
@patch("auth.router.verify_password", return_value=False)
@patch("auth.router.log_audit_event", new_callable=AsyncMock)
async def test_login_wrong_password(mock_audit, mock_verify):
    from main import app

    user = _fake_user()
    session = AsyncMock()
    result = MagicMock()
    result.scalar_one_or_none.return_value = user
    session.execute = AsyncMock(return_value=result)
    session.commit = AsyncMock()

    _setup(app, session)
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
            r = await c.post("/api/v1/auth/login", data={
                "username": "user@example.com",
                "password": "WrongPassword123!@",
            })
        assert r.status_code == 401
    finally:
        _teardown(app)


@pytest.mark.asyncio
async def test_login_locked_account():
    from main import app

    user = _fake_user(locked_until=datetime.utcnow() + timedelta(minutes=15))
    session = AsyncMock()
    result = MagicMock()
    result.scalar_one_or_none.return_value = user
    session.execute = AsyncMock(return_value=result)

    _setup(app, session)
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
            r = await c.post("/api/v1/auth/login", data={
                "username": "user@example.com",
                "password": "Whatever123!@#",
            })
        assert r.status_code == 403
    finally:
        _teardown(app)


@pytest.mark.asyncio
@patch("auth.router.verify_password", return_value=True)
@patch("auth.router.log_audit_event", new_callable=AsyncMock)
async def test_login_inactive_account(mock_audit, mock_verify):
    from main import app

    user = _fake_user(is_active=False)
    session = AsyncMock()
    result = MagicMock()
    result.scalar_one_or_none.return_value = user
    session.execute = AsyncMock(return_value=result)
    session.commit = AsyncMock()

    _setup(app, session)
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
            r = await c.post("/api/v1/auth/login", data={
                "username": "user@example.com",
                "password": "StrongPass123!@#",
            })
        assert r.status_code == 403
    finally:
        _teardown(app)


# ─── Logout ──────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
@patch("auth.router.log_audit_event", new_callable=AsyncMock)
async def test_logout_success(mock_audit):
    from main import app

    user = _fake_user()
    session = AsyncMock()
    # Fetch refresh tokens
    tokens_result = MagicMock()
    tokens_result.scalars.return_value.all.return_value = []
    session.execute = AsyncMock(return_value=tokens_result)
    session.commit = AsyncMock()

    _setup(app, session, user=user)
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
            r = await c.post("/api/v1/auth/logout")
        assert r.status_code == 200
        assert "logged out" in r.json()["message"].lower()
    finally:
        _teardown(app)


# ─── Profile ─────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_get_profile():
    from main import app

    user = _fake_user()
    session = AsyncMock()
    result = MagicMock()
    result.scalar_one_or_none.return_value = user
    session.execute = AsyncMock(return_value=result)

    _setup(app, session, user=user)
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
            r = await c.get("/api/v1/auth/me")
        assert r.status_code == 200
        data = r.json()
        assert data["email"] == "user@example.com"
    finally:
        _teardown(app)


# ─── Change password ─────────────────────────────────────────────────────────

@pytest.mark.asyncio
@patch("auth.router.verify_password", return_value=True)
@patch("auth.router.get_password_hash", return_value="newhash")
@patch("auth.router.log_audit_event", new_callable=AsyncMock)
async def test_change_password_success(mock_audit, mock_hash, mock_verify):
    from main import app

    user = _fake_user()
    session = AsyncMock()
    session.commit = AsyncMock()

    _setup(app, session, user=user)
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
            r = await c.post("/api/v1/auth/change-password", json={
                "old_password": "OldPass123!@#",
                "new_password": "NewSecure123!@#",
            })
        assert r.status_code == 200
    finally:
        _teardown(app)


@pytest.mark.asyncio
@patch("auth.router.verify_password", return_value=False)
async def test_change_password_wrong_old(mock_verify):
    from main import app

    user = _fake_user()
    session = AsyncMock()

    _setup(app, session, user=user)
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
            r = await c.post("/api/v1/auth/change-password", json={
                "old_password": "WrongOld123!@#",
                "new_password": "NewSecure123!@#",
            })
        assert r.status_code == 400
    finally:
        _teardown(app)


# ─── Admin: list users ───────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_list_users_as_admin():
    from main import app

    admin = _fake_user(role="Admin")
    session = AsyncMock()
    result = MagicMock()
    result.scalars.return_value.all.return_value = [admin]
    session.execute = AsyncMock(return_value=result)

    _setup(app, session, user=admin)
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
            r = await c.get("/api/v1/auth/users")
        assert r.status_code == 200
        assert isinstance(r.json(), list)
    finally:
        _teardown(app)


@pytest.mark.asyncio
async def test_list_users_forbidden():
    from main import app

    viewer = _fake_user(role="Viewer")
    # Give the viewer role without Admin
    role = MagicMock()
    role.role_name = "Viewer"
    viewer.roles = [role]
    session = AsyncMock()

    _setup(app, session, user=viewer)
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
            r = await c.get("/api/v1/auth/users")
        assert r.status_code == 403
    finally:
        _teardown(app)


# ─── Admin: list roles ───────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_list_roles():
    from main import app

    admin = _fake_user(role="Admin")
    session = AsyncMock()
    role_mock = MagicMock()
    role_mock.role_id = uuid.uuid4()
    role_mock.role_name = "Analyst"
    role_mock.description_en = "Analyst"
    role_mock.description_ar = "محلل"
    role_mock.created_at = datetime.utcnow()
    result = MagicMock()
    result.scalars.return_value.all.return_value = [role_mock]
    session.execute = AsyncMock(return_value=result)

    _setup(app, session, user=admin)
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
            r = await c.get("/api/v1/auth/roles")
        assert r.status_code == 200
    finally:
        _teardown(app)


# ─── Admin: admin stats ──────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_admin_stats():
    from main import app

    admin = _fake_user(role="Admin")
    session = AsyncMock()
    session.scalar = AsyncMock(side_effect=[10, 8, 50, 30, 5])

    _setup(app, session, user=admin)
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
            r = await c.get("/api/v1/auth/admin/stats")
        assert r.status_code == 200
        data = r.json()
        assert data["total_users"] == 10
        assert data["active_users"] == 8
    finally:
        _teardown(app)


# ─── Admin: system status ────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_system_status():
    from main import app

    admin = _fake_user(role="Admin")
    session = AsyncMock()
    # text("SELECT 1")
    select1 = MagicMock()
    # pg_database_size
    size_result = MagicMock()
    size_result.scalar.return_value = 1024 * 1024
    # audit log count
    audit_result = MagicMock()
    session.execute = AsyncMock(side_effect=[select1, size_result, audit_result])

    _setup(app, session, user=admin)
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
            r = await c.get("/api/v1/auth/admin/system-status")
        assert r.status_code == 200
        data = r.json()
        assert data["backend_ok"] is True
    finally:
        _teardown(app)


# ─── Pending registrations ───────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_list_pending_registrations():
    from main import app

    admin = _fake_user(role="Admin")
    session = AsyncMock()
    pending = _fake_user(is_active=False, is_verified=False, roles=[])
    result = MagicMock()
    result.scalars.return_value.all.return_value = [pending]
    session.execute = AsyncMock(return_value=result)

    _setup(app, session, user=admin)
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
            r = await c.get("/api/v1/auth/pending-registrations")
        assert r.status_code == 200
        assert isinstance(r.json(), list)
    finally:
        _teardown(app)


# ─── Approve / deny registration ─────────────────────────────────────────────

@pytest.mark.asyncio
@patch("auth.router.send_account_approved_email")
@patch("auth.router.log_audit_event", new_callable=AsyncMock)
async def test_approve_registration(mock_audit, mock_email):
    from main import app

    admin = _fake_user(role="Admin")
    pending = _fake_user(is_active=False, is_verified=False, roles=[])
    session = AsyncMock()

    # First execute: fetch user
    fetch_result = MagicMock()
    fetch_result.scalar_one_or_none.return_value = pending
    # Second execute: fetch Analyst role
    analyst_role = MagicMock()
    analyst_role.role_name = "Analyst"
    role_result = MagicMock()
    role_result.scalar_one_or_none.return_value = analyst_role
    session.execute = AsyncMock(side_effect=[fetch_result, role_result])
    session.commit = AsyncMock()

    _setup(app, session, user=admin)
    try:
        uid = str(pending.user_id)
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
            r = await c.post(f"/api/v1/auth/users/{uid}/approve")
        assert r.status_code == 200
    finally:
        _teardown(app)


@pytest.mark.asyncio
@patch("auth.router.send_account_denied_email")
@patch("auth.router.log_audit_event", new_callable=AsyncMock)
async def test_deny_registration(mock_audit, mock_email):
    from main import app

    admin = _fake_user(role="Admin")
    pending = _fake_user(is_active=False)
    session = AsyncMock()
    result = MagicMock()
    result.scalar_one_or_none.return_value = pending
    session.execute = AsyncMock(return_value=result)
    session.delete = AsyncMock()
    session.commit = AsyncMock()

    _setup(app, session, user=admin)
    try:
        uid = str(pending.user_id)
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
            r = await c.post(f"/api/v1/auth/users/{uid}/deny")
        assert r.status_code == 200
    finally:
        _teardown(app)


# ─── Deactivate user ─────────────────────────────────────────────────────────

@pytest.mark.asyncio
@patch("auth.router.log_audit_event", new_callable=AsyncMock)
async def test_deactivate_user(mock_audit):
    from main import app

    admin = _fake_user(role="Admin")
    target = _fake_user(is_active=True)
    session = AsyncMock()
    result = MagicMock()
    result.scalar_one_or_none.return_value = target
    session.execute = AsyncMock(return_value=result)
    session.commit = AsyncMock()

    _setup(app, session, user=admin)
    try:
        uid = str(target.user_id)
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
            r = await c.patch(f"/api/v1/auth/users/{uid}/deactivate")
        assert r.status_code == 200
    finally:
        _teardown(app)
