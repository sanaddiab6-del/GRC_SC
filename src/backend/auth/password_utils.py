"""
Password hashing utilities.

Uses explicit SHA-256 pre-hashing before bcrypt so that passwords longer than
72 bytes (bcrypt's hard limit) are handled correctly.  The SHA-256 hex digest
is always 64 ASCII characters, safely within that limit.

No plain-text password is ever logged or stored.
"""
import hashlib
from passlib.context import CryptContext

# Plain bcrypt – we own the pre-hashing step ourselves.
_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def _pre_hash(password: str) -> str:
    """Return the SHA-256 hex digest of *password* (always 64 bytes)."""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def get_password_hash(password: str) -> str:
    """Hash *password* using SHA-256 pre-hashing + bcrypt."""
    return _pwd_context.hash(_pre_hash(password))


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Return ``True`` if *plain_password* matches *hashed_password*."""
    try:
        return _pwd_context.verify(_pre_hash(plain_password), hashed_password)
    except Exception:
        return False
