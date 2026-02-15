"""
Input validation and sanitization utilities for SICO GRC Platform.
Implements security best practices to prevent injection attacks (NCA ECC-IS-3).
"""
import re
import html
from typing import Any, Dict, List
from fastapi import HTTPException, status


# Dangerous SQL keywords (basic protection, parameterized queries are still primary defense)
SQL_INJECTION_PATTERNS = [
    r"(\bunion\b.*\bselect\b)",
    r"(\bdrop\b.*\btable\b)",
    r"(\binsert\b.*\binto\b)",
    r"(\bdelete\b.*\bfrom\b)",
    r"(\bupdate\b.*\bset\b)",
    r"(--)",
    r"(;.*\b(drop|union|select|insert|update|delete)\b)",
    r"(\bexec\b.*\()",
    r"(\bexecute\b.*\()",
]

# XSS patterns
XSS_PATTERNS = [
    r"<script[^>]*>.*?</script>",
    r"javascript:",
    r"on\w+\s*=",  # onclick, onload, etc.
    r"<iframe",
    r"<object",
    r"<embed",
]


def sanitize_string(value: str, max_length: int = 1000) -> str:
    """
    Sanitize string input to prevent XSS attacks.
    
    Args:
        value: Input string
        max_length: Maximum allowed length
        
    Returns:
        Sanitized string
        
    Raises:
        HTTPException: If malicious content detected
    """
    if not isinstance(value, str):
        return value
    
    # Length check
    if len(value) > max_length:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Input too long. Maximum {max_length} characters allowed."
        )
    
    # Check for XSS patterns
    for pattern in XSS_PATTERNS:
        if re.search(pattern, value, re.IGNORECASE):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Potentially malicious content detected"
            )
    
    # HTML escape
    sanitized = html.escape(value)
    
    return sanitized


def validate_no_sql_injection(value: str) -> str:
    """
    Validate string for SQL injection patterns.
    Note: This is defense-in-depth. Always use parameterized queries as primary defense.
    
    Args:
        value: Input string
        
    Returns:
        Original value if safe
        
    Raises:
        HTTPException: If SQL injection pattern detected
    """
    if not isinstance(value, str):
        return value
    
    # Check for SQL injection patterns
    for pattern in SQL_INJECTION_PATTERNS:
        if re.search(pattern, value, re.IGNORECASE):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid input format"
            )
    
    return value


def sanitize_dict(data: Dict[str, Any], max_length: int = 1000) -> Dict[str, Any]:
    """
    Recursively sanitize dictionary values.
    
    Args:
        data: Input dictionary
        max_length: Maximum string length
        
    Returns:
        Sanitized dictionary
    """
    sanitized = {}
    
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
    """
    Validate UUID format.
    
    Args:
        value: UUID string
        
    Returns:
        True if valid UUID
    """
    uuid_pattern = r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
    return bool(re.match(uuid_pattern, value, re.IGNORECASE))


def validate_email(email: str) -> bool:
    """
    Validate email format (basic check, use EmailStr for comprehensive validation).
    
    Args:
        email: Email address
        
    Returns:
        True if valid format
    """
    email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(email_pattern, email))


def validate_saudi_mobile(phone: str) -> bool:
    """
    Validate Saudi mobile number format.
    Formats: +966XXXXXXXXX or 05XXXXXXXX or 9665XXXXXXXX
    
    Args:
        phone: Phone number
        
    Returns:
        True if valid Saudi mobile
    """
    # Remove spaces and dashes
    phone = phone.replace(" ", "").replace("-", "")
    
    patterns = [
        r"^\+9665\d{8}$",  # +966 5XX XXX XXX
        r"^9665\d{8}$",    # 966 5XX XXX XXX
        r"^05\d{8}$",      # 05X XXX XXXX
    ]
    
    return any(re.match(pattern, phone) for pattern in patterns)


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename to prevent directory traversal attacks.
    
    Args:
        filename: File name
        
    Returns:
        Sanitized filename
        
    Raises:
        HTTPException: If malicious patterns detected
    """
    # Check for directory traversal
    if ".." in filename or "/" in filename or "\\" in filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid filename format"
        )
    
    # Allow only alphanumeric, dots, dashes, underscores
    safe_filename = re.sub(r'[^a-zA-Z0-9._-]', '_', filename)
    
    # Limit length
    if len(safe_filename) > 255:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Filename too long"
        )
    
    return safe_filename


def validate_json_size(data: Any, max_size_kb: int = 500) -> bool:
    """
    Validate JSON payload size to prevent memory exhaustion attacks.
    
    Args:
        data: JSON data
        max_size_kb: Maximum size in KB
        
    Returns:
        True if within limits
        
    Raises:
        HTTPException: If payload too large
    """
    import json
    
    size_bytes = len(json.dumps(data).encode('utf-8'))
    size_kb = size_bytes / 1024
    
    if size_kb > max_size_kb:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Payload too large. Maximum {max_size_kb} KB allowed."
        )
    
    return True


# IP address validation for Saudi IP ranges (optional, for geo-restrictions)
def is_saudi_ip(ip: str) -> bool:
    """
    Check if IP address is from Saudi Arabia (basic check).
    For production, use GeoIP database like MaxMind.
    
    Args:
        ip: IP address
        
    Returns:
        True if Saudi IP (simplified check)
    """
    # TODO: Implement proper GeoIP lookup with MaxMind or similar
    # This is a placeholder - in production, use a proper GeoIP database
    # Saudi Arabia IP ranges (partial list for demonstration)
    saudi_ip_prefixes = [
        "213.130.",  # STC
        "212.26.",   # Mobily
        "212.72.",   # Zain
        # Add more ranges as needed
    ]
    
    return any(ip.startswith(prefix) for prefix in saudi_ip_prefixes)
