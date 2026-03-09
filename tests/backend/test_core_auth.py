"""
Tests for core/auth.py — SHA-256 pre-hash + bcrypt password utilities and
JWT token creation/validation.
"""
import pytest
import os


# ─── Password hashing (core/auth.py) ─────────────────────────────────────────

def test_prehash_password_is_base64():
    from core.auth import _prehash_password
    import base64

    h = _prehash_password("TestPassword123!")
    # Must be valid base64
    base64.b64decode(h)
    assert len(h) == 44  # SHA-256 digest is 32 bytes → base64 is 44 chars


def test_prehash_is_deterministic():
    from core.auth import _prehash_password

    assert _prehash_password("same") == _prehash_password("same")


def test_prehash_different_inputs():
    from core.auth import _prehash_password

    assert _prehash_password("a") != _prehash_password("b")


def test_prehash_long_password():
    """Password > 72 bytes must still hash correctly via the pre-hash."""
    from core.auth import _prehash_password

    long_pw = "A" * 100
    h = _prehash_password(long_pw)
    assert len(h) == 44  # Always 44 chars


def test_get_password_hash():
    from core.auth import get_password_hash

    h = get_password_hash("StrongPass123!")
    assert h.startswith("$2b$")


def test_verify_password_correct():
    from core.auth import get_password_hash, verify_password

    pw = "StrongPass123!@#"
    h = get_password_hash(pw)
    assert verify_password(pw, h)


def test_verify_password_wrong():
    from core.auth import get_password_hash, verify_password

    h = get_password_hash("Correct123!@#")
    assert not verify_password("Wrong123!@#", h)


def test_verify_password_long():
    """Passwords > 72 bytes should hash and verify without error."""
    from core.auth import get_password_hash, verify_password

    pw = "VeryLongPassword123!@#" * 5  # 110 chars
    h = get_password_hash(pw)
    assert verify_password(pw, h)


def test_hash_unique_salts():
    from core.auth import get_password_hash

    h1 = get_password_hash("Same123!@#")
    h2 = get_password_hash("Same123!@#")
    assert h1 != h2  # bcrypt uses random salt


# ─── JWT token creation (core/auth.py) ───────────────────────────────────────

@pytest.mark.skipif(
    not True,  # always run
    reason="AI security module may not be available",
)
def test_decode_token_valid():
    """create_access_token + decode_token round-trip (uses AI module if available)."""
    pytest.importorskip("ai.security.ai_security")

    from core.auth import create_access_token, decode_token
    from ai.security.ai_security import AIRole, AIPermission

    token = create_access_token(
        user_id="user-1",
        tenant_id="tenant-1",
        role=AIRole.ANALYST,
        permissions={AIPermission.QUERY_RAG},
    )

    payload = decode_token(token)
    assert payload["sub"] == "user-1"
    assert payload["tenant_id"] == "tenant-1"
    assert payload["type"] == "access"


def test_decode_token_invalid():
    from core.auth import decode_token
    from fastapi import HTTPException

    with pytest.raises(HTTPException) as exc_info:
        decode_token("not.a.valid.token")
    assert exc_info.value.status_code == 401


def test_decode_token_expired():
    from core.auth import JWT_SECRET_KEY, JWT_ALGORITHM
    from fastapi import HTTPException
    import jwt
    from datetime import datetime, timedelta

    payload = {
        "sub": "user",
        "tenant_id": "t",
        "role": "analyst",
        "permissions": [],
        "exp": datetime.utcnow() - timedelta(hours=1),
        "iat": datetime.utcnow() - timedelta(hours=2),
        "type": "access",
    }
    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

    from core.auth import decode_token
    with pytest.raises(HTTPException) as exc_info:
        decode_token(token)
    assert exc_info.value.status_code == 401
