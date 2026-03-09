"""
Password hashing utilities.

Pre-hashes passwords with SHA-256 + base64 before bcrypt so that bcrypt never
receives raw input longer than 72 bytes.  The base64-encoded SHA-256 digest is
always 44 characters (43 significant + 1 padding), well within the limit.

No plain-text password is ever logged or stored.
"""
import base64
import hashlib
from passlib.context import CryptContext

# Plain bcrypt – we own the pre-hashing step ourselves.
_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def _prehash_password(password: str) -> str:
    """Return base64(sha256(password)) — always 44 ASCII characters."""
    digest = hashlib.sha256(password.encode("utf-8")).digest()
    return base64.b64encode(digest).decode("ascii")


# Keep the old name as an alias so any callers that used _pre_hash still work.
_pre_hash = _prehash_password


def get_password_hash(password: str) -> str:
    """Hash *password* using SHA-256 + base64 pre-hashing, then bcrypt."""
    return _pwd_context.hash(_prehash_password(password))


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Return ``True`` if *plain_password* matches *hashed_password*."""
    try:
        return _pwd_context.verify(_prehash_password(plain_password), hashed_password)
    except Exception:
        return False

