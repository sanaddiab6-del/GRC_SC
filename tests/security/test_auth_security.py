"""
Tests for auth/security.py — password hashing, token creation, role/permission checks.
"""
import pytest
import uuid
import os
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta


# ─── Password hashing ────────────────────────────────────────────────────────

def test_password_hash_and_verify():
    from auth.security import get_password_hash, verify_password

    raw = "TestPassword123!@#"
    hashed = get_password_hash(raw)
    assert hashed != raw
    assert verify_password(raw, hashed)


def test_password_verify_wrong():
    from auth.security import get_password_hash, verify_password

    hashed = get_password_hash("Correct123!@#$")
    assert not verify_password("Wrong123!@#$", hashed)


def test_password_hash_unique():
    from auth.security import get_password_hash

    h1 = get_password_hash("Same123!@#")
    h2 = get_password_hash("Same123!@#")
    # bcrypt salts → different hashes each time
    assert h1 != h2


# ─── Token creation ──────────────────────────────────────────────────────────

def test_create_access_token():
    from auth.security import create_access_token

    token = create_access_token(data={"sub": "user123", "email": "a@b.com"})
    assert isinstance(token, str)
    assert len(token) > 20


def test_create_refresh_token():
    from auth.security import create_refresh_token

    token = create_refresh_token("user123")
    assert isinstance(token, str)
    assert len(token) > 20


def test_access_token_decode():
    from auth.security import create_access_token, SECRET_KEY, ALGORITHM
    from jose import jwt

    user_id = str(uuid.uuid4())
    token = create_access_token(data={"sub": user_id, "email": "test@x.com"})
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    assert payload["sub"] == user_id
    assert payload["email"] == "test@x.com"
    assert "exp" in payload


def test_refresh_token_decode():
    from auth.security import create_refresh_token, SECRET_KEY, ALGORITHM
    from jose import jwt

    user_id = str(uuid.uuid4())
    token = create_refresh_token(user_id)
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    assert payload["sub"] == user_id
    assert payload["type"] == "refresh"


# ─── hash_token ───────────────────────────────────────────────────────────────

def test_hash_token_deterministic():
    from auth.security import hash_token

    h1 = hash_token("mytoken")
    h2 = hash_token("mytoken")
    assert h1 == h2
    assert len(h1) == 64  # SHA-256 hex digest


def test_hash_token_different():
    from auth.security import hash_token

    assert hash_token("a") != hash_token("b")


# ─── require_role ─────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_require_role_unauthorized():
    """require_role should raise 403 for non-matching role."""
    from auth.security import require_role
    from fastapi import HTTPException

    # Create the dependency
    dep = require_role("Admin")

    # Mock user without Admin role
    user = MagicMock()
    role = MagicMock()
    role.role_name = "Viewer"
    user.roles = [role]

    # The dependency generator needs a user; we simulate by calling it
    # require_role returns an async function that takes current_user
    # but it's a Depends wrapper — we test the logic
    with pytest.raises(HTTPException) as exc_info:
        await dep(current_user=user)
    assert exc_info.value.status_code == 403


# ─── log_audit_event ─────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_log_audit_event():
    from auth.security import log_audit_event

    session = AsyncMock()
    session.add = MagicMock()
    session.commit = AsyncMock()

    await log_audit_event(
        db=session,
        user_id="user-123",
        action="test_action",
        resource="test",
        resource_id="res-1",
        status="success",
        ip_address="127.0.0.1",
        user_agent="pytest",
    )
    session.add.assert_called_once()
    session.commit.assert_awaited_once()
