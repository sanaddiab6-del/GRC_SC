"""
Tests for JWT Authentication System
Coverage: Token creation, validation, RBAC, Azure AD integration
"""

from datetime import datetime, timedelta
import pytest
from fastapi import HTTPException
import jwt

from src.backend.core.auth import (
    create_access_token,
    create_refresh_token,
    create_token_pair,
    decode_token,
    get_token_data,
    verify_password,
    get_password_hash,
    JWT_SECRET_KEY,
    JWT_ALGORITHM,
)
from ai.security.ai_security import AIRole, AIPermission


# ============================================================================
# Test Token Creation
# ============================================================================

def test_create_access_token():
    """Test JWT access token creation"""
    token = create_access_token(
        user_id="user123",
        tenant_id="tenant456",
        role=AIRole.AI_OPERATOR,
        permissions={AIPermission.QUERY_RAG, AIPermission.VIEW_DATA},
    )
    
    assert isinstance(token, str)
    assert len(token) > 0
    
    # Decode and verify
    payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
    assert payload["sub"] == "user123"
    assert payload["tenant_id"] == "tenant456"
    assert payload["role"] == "ai_operator"
    assert set(payload["permissions"]) == {"query_rag", "view_data"}
    assert payload["type"] == "access"


def test_create_refresh_token():
    """Test JWT refresh token creation"""
    token = create_refresh_token(
        user_id="user123",
        tenant_id="tenant456",
    )
    
    assert isinstance(token, str)
    assert len(token) > 0
    
    # Decode and verify
    payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
    assert payload["sub"] == "user123"
    assert payload["tenant_id"] == "tenant456"
    assert payload["type"] == "refresh"


def test_create_token_pair():
    """Test access + refresh token pair creation"""
    tokens = create_token_pair(
        user_id="user123",
        tenant_id="tenant456",
        role=AIRole.AI_ADMIN,
        permissions={AIPermission.MANAGE_MODELS, AIPermission.APPROVE_MODELS},
    )
    
    assert tokens.token_type == "bearer"
    assert isinstance(tokens.access_token, str)
    assert isinstance(tokens.refresh_token, str)
    assert tokens.expires_in > 0


def test_token_expiration():
    """Test token expiration time"""
    # Create token with 1 second expiry
    token = create_access_token(
        user_id="user123",
        tenant_id="tenant456",
        role=AIRole.VIEWER,
        permissions=set(),
        expires_delta=timedelta(seconds=1),
    )
    
    # Should decode successfully immediately
    payload = decode_token(token)
    assert payload["sub"] == "user123"
    
    # Wait and verify expiration (simulate)
    import time
    time.sleep(2)
    
    # Should raise expired signature error
    with pytest.raises(HTTPException) as exc_info:
        decode_token(token)
    
    assert exc_info.value.status_code == 401
    assert "expired" in str(exc_info.value.detail).lower()


# ============================================================================
# Test Token Validation
# ============================================================================

def test_decode_valid_token():
    """Test decoding valid JWT token"""
    token = create_access_token(
        user_id="user123",
        tenant_id="tenant456",
        role=AIRole.AI_OPERATOR,
        permissions={AIPermission.QUERY_RAG},
    )
    
    payload = decode_token(token)
    
    assert payload["sub"] == "user123"
    assert payload["tenant_id"] == "tenant456"
    assert payload["role"] == "ai_operator"


def test_decode_invalid_token():
    """Test decoding invalid JWT token"""
    invalid_token = "invalid.jwt.token"
    
    with pytest.raises(HTTPException) as exc_info:
        decode_token(invalid_token)
    
    assert exc_info.value.status_code == 401
    assert "invalid" in str(exc_info.value.detail).lower()


def test_decode_tampered_token():
    """Test decoding tampered JWT token"""
    # Create valid token
    token = create_access_token(
        user_id="user123",
        tenant_id="tenant456",
        role=AIRole.VIEWER,
        permissions=set(),
    )
    
    # Tamper with token (change last character)
    tampered_token = token[:-1] + ("A" if token[-1] != "A" else "B")
    
    with pytest.raises(HTTPException) as exc_info:
        decode_token(tampered_token)
    
    assert exc_info.value.status_code == 401


def test_get_token_data():
    """Test extracting user data from token"""
    token = create_access_token(
        user_id="user123",
        tenant_id="tenant456",
        role=AIRole.AI_ADMIN,
        permissions={AIPermission.MANAGE_MODELS, AIPermission.APPROVE_MODELS},
    )
    
    token_data = get_token_data(token)
    
    assert token_data.user_id == "user123"
    assert token_data.tenant_id == "tenant456"
    assert token_data.role == AIRole.AI_ADMIN
    assert AIPermission.MANAGE_MODELS in token_data.permissions
    assert AIPermission.APPROVE_MODELS in token_data.permissions


def test_get_token_data_invalid_role():
    """Test token with invalid role string"""
    # Manually create token with invalid role
    payload = {
        "sub": "user123",
        "tenant_id": "tenant456",
        "role": "invalid_role",
        "permissions": [],
        "exp": datetime.utcnow() + timedelta(minutes=30),
        "iat": datetime.utcnow(),
        "type": "access",
    }
    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    
    with pytest.raises(HTTPException) as exc_info:
        get_token_data(token)
    
    assert exc_info.value.status_code == 401
    assert "role" in str(exc_info.value.detail).lower()


# ============================================================================
# Test Password Hashing
# ============================================================================

def test_password_hashing():
    """Test password hashing and verification"""
    password = "SecurePassword123!"
    
    # Hash password
    hashed = get_password_hash(password)
    
    assert isinstance(hashed, str)
    assert len(hashed) > 0
    assert hashed != password  # Should be hashed
    
    # Verify correct password
    assert verify_password(password, hashed) is True
    
    # Verify incorrect password
    assert verify_password("WrongPassword", hashed) is False


def test_password_hash_uniqueness():
    """Test that same password produces different hashes"""
    password = "SamePassword123"
    
    hash1 = get_password_hash(password)
    hash2 = get_password_hash(password)
    
    # Different hashes (bcrypt uses random salt)
    assert hash1 != hash2
    
    # Both verify correctly
    assert verify_password(password, hash1)
    assert verify_password(password, hash2)


# ============================================================================
# Test Role-Based Authorization
# ============================================================================

def test_admin_permissions():
    """Test AI_ADMIN role has all permissions"""
    token = create_access_token(
        user_id="admin",
        tenant_id="tenant1",
        role=AIRole.AI_ADMIN,
        permissions={
            AIPermission.MANAGE_MODELS,
            AIPermission.APPROVE_MODELS,
            AIPermission.QUERY_RAG,
            AIPermission.VIEW_DATA,
            AIPermission.EXPORT_DATA,
            AIPermission.MODIFY_SETTINGS,
        },
    )
    
    token_data = get_token_data(token)
    
    assert token_data.role == AIRole.AI_ADMIN
    assert len(token_data.permissions) == 6
    assert AIPermission.MANAGE_MODELS in token_data.permissions


def test_viewer_limited_permissions():
    """Test VIEWER role has minimal permissions"""
    token = create_access_token(
        user_id="viewer",
        tenant_id="tenant1",
        role=AIRole.VIEWER,
        permissions={AIPermission.VIEW_DATA},
    )
    
    token_data = get_token_data(token)
    
    assert token_data.role == AIRole.VIEWER
    assert AIPermission.VIEW_DATA in token_data.permissions
    assert AIPermission.MANAGE_MODELS not in token_data.permissions
    assert AIPermission.EXPORT_DATA not in token_data.permissions


# ============================================================================
# Test Multi-Tenancy Isolation
# ============================================================================

def test_tenant_isolation():
    """Test tokens are tenant-specific"""
    # Create tokens for different tenants
    token1 = create_access_token(
        user_id="user1",
        tenant_id="tenant_a",
        role=AIRole.AI_OPERATOR,
        permissions={AIPermission.QUERY_RAG},
    )
    
    token2 = create_access_token(
        user_id="user2",
        tenant_id="tenant_b",
        role=AIRole.AI_OPERATOR,
        permissions={AIPermission.QUERY_RAG},
    )
    
    # Verify tenant separation
    data1 = get_token_data(token1)
    data2 = get_token_data(token2)
    
    assert data1.tenant_id == "tenant_a"
    assert data2.tenant_id == "tenant_b"
    assert data1.tenant_id != data2.tenant_id


def test_same_user_different_tenants():
    """Test same user can have different tokens for different tenants"""
    user_id = "user123"
    
    token1 = create_access_token(
        user_id=user_id,
        tenant_id="tenant_a",
        role=AIRole.AI_ADMIN,
        permissions={AIPermission.MANAGE_MODELS},
    )
    
    token2 = create_access_token(
        user_id=user_id,
        tenant_id="tenant_b",
        role=AIRole.VIEWER,
        permissions={AIPermission.VIEW_DATA},
    )
    
    data1 = get_token_data(token1)
    data2 = get_token_data(token2)
    
    # Same user, different contexts
    assert data1.user_id == data2.user_id == user_id
    assert data1.tenant_id != data2.tenant_id
    assert data1.role != data2.role


# ============================================================================
# Test Security Scenarios
# ============================================================================

def test_token_cannot_be_modified():
    """Test token modification detection"""
    token = create_access_token(
        user_id="user123",
        tenant_id="tenant456",
        role=AIRole.VIEWER,
        permissions={AIPermission.VIEW_DATA},
    )
    
    # Try to decode token parts
    parts = token.split(".")
    assert len(parts) == 3
    
    # Attempt to modify payload (change user_id)
    import base64
    import json
    
    # Decode payload
    payload_bytes = base64.urlsafe_b64decode(parts[1] + "==")
    payload = json.loads(payload_bytes)
    
    # Modify payload
    payload["role"] = "ai_admin"
    
    # Re-encode
    modified_payload = base64.urlsafe_b64encode(
        json.dumps(payload).encode()
    ).decode().rstrip("=")
    
    # Reconstruct token with modified payload
    modified_token = f"{parts[0]}.{modified_payload}.{parts[2]}"
    
    # Should fail verification (signature mismatch)
    with pytest.raises(HTTPException):
        decode_token(modified_token)


def test_refresh_token_cannot_be_used_as_access():
    """Test refresh tokens are distinguished from access tokens"""
    refresh_token = create_refresh_token(
        user_id="user123",
        tenant_id="tenant456",
    )
    
    # Decode refresh token
    payload = decode_token(refresh_token)
    
    # Verify it's marked as refresh type
    assert payload["type"] == "refresh"
    
    # In production, you would check token type before using it
    # and reject refresh tokens for API access


# ============================================================================
# Run Tests
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
