"""Input validation and sanitization utilities for SICO GRC Platform."""

import html
import importlib
import json
import logging
import os
import re
from typing import Any, Dict

from fastapi import HTTPException, status

logger = logging.getLogger(__name__)

XSS_PATTERNS = [
    r"<\s*script[^>]*>",
    r"javascript:\s*",
    r"on\w+\s*=",
    r"<\s*iframe[^>]*>",
]

SQL_INJECTION_PATTERNS = [
    r"\bunion\b\s+\bselect\b",
    r"\bdrop\b\s+\btable\b",
    r"\binsert\b\s+\binto\b",
    r"\bdelete\b\s+\bfrom\b",
    r"\bupdate\b\s+\w+\s+\bset\b",
    r"(--|;)",
]

GEOIP_AVAILABLE = False
geoip2_reader = None

try:
    geoip2_database = importlib.import_module("geoip2.database")
    GEOIP_DB_PATH = os.getenv("GEOIP_DB_PATH", "/usr/share/GeoIP/GeoLite2-Country.mmdb")
    if os.path.exists(GEOIP_DB_PATH):
        geoip2_reader = geoip2_database.Reader(GEOIP_DB_PATH)
        GEOIP_AVAILABLE = True
except ImportError:
    logger.warning("geoip2 library not installed; using fallback IP ranges")
except Exception as exc:
    logger.error(f"Error loading GeoIP2 database: {exc}")


def sanitize_string(value: str, max_length: int = 1000) -> str:
    """Validate and sanitize string input."""
    if not isinstance(value, str):
        return value

    if len(value) > max_length:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Input too long. Maximum {max_length} characters allowed.",
        )

    for pattern in XSS_PATTERNS:
        if re.search(pattern, value, re.IGNORECASE):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Potentially malicious content detected",
            )

    return html.escape(value)


def validate_no_sql_injection(value: str) -> str:
    """Validate input against common SQL injection patterns."""
    if not isinstance(value, str):
        return value

    for pattern in SQL_INJECTION_PATTERNS:
        if re.search(pattern, value, re.IGNORECASE):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid input format",
            )

    return value


def sanitize_dict(data: Dict[str, Any], max_length: int = 1000) -> Dict[str, Any]:
    """Recursively sanitize dictionary values."""
    sanitized: Dict[str, Any] = {}

    for key, value in data.items():
        if isinstance(value, str):
            sanitized[key] = sanitize_string(value, max_length)
        elif isinstance(value, dict):
            sanitized[key] = sanitize_dict(value, max_length)
        elif isinstance(value, list):
            sanitized[key] = [
                sanitize_string(item, max_length) if isinstance(item, str) else item
                for item in value
            ]
        else:
            sanitized[key] = value

    return sanitized


def validate_uuid(value: str) -> bool:
    """Validate UUID string format."""
    uuid_pattern = r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
    return bool(re.match(uuid_pattern, value, re.IGNORECASE))


def validate_email(email: str) -> bool:
    """Validate basic email format."""
    email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(email_pattern, email))


def validate_saudi_mobile(phone: str) -> bool:
    """Validate Saudi mobile number format."""
    normalized = phone.replace(" ", "").replace("-", "")
    patterns = [
        r"^\+9665\d{8}$",
        r"^9665\d{8}$",
        r"^05\d{8}$",
    ]
    return any(re.match(pattern, normalized) for pattern in patterns)


def sanitize_filename(filename: str) -> str:
    """Sanitize filename and block traversal patterns."""
    if ".." in filename or "/" in filename or "\\" in filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid filename format",
        )

    safe_filename = re.sub(r"[^a-zA-Z0-9._-]", "_", filename)

    if len(safe_filename) > 255:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Filename too long",
        )

    return safe_filename


def validate_json_size(data: Any, max_size_kb: int = 500) -> bool:
    """Validate JSON payload size in KB."""
    size_bytes = len(json.dumps(data).encode("utf-8"))
    size_kb = size_bytes / 1024

    if size_kb > max_size_kb:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Payload too large. Maximum {max_size_kb} KB allowed.",
        )

    return True


def is_saudi_ip(ip: str) -> bool:
    """Check whether an IP is geolocated to Saudi Arabia."""
    if GEOIP_AVAILABLE and geoip2_reader:
        try:
            response = geoip2_reader.country(ip)
            return response.country.iso_code == "SA"
        except Exception:
            pass

    saudi_ip_prefixes = [
        "213.130.",
        "213.131.",
        "212.26.",
        "212.27.",
        "212.72.",
        "212.73.",
        "195.229.",
        "46.242.",
        "31.9.",
        "31.13.",
    ]
    return any(ip.startswith(prefix) for prefix in saudi_ip_prefixes)
