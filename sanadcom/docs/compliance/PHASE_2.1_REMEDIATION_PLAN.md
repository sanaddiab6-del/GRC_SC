# Phase 2.1: Critical Security Controls - Implementation Plan

## Overview
This phase addresses P0 (CRITICAL) security gaps identified in the compliance validation. These controls are **mandatory** before production deployment and are blocking requirements for NCA ECC, CCC, and PDPL compliance.

**Timeline**: 2 weeks  
**Target Compliance Improvement**: 35% (from 17% to 52%)

---

## 1. Authentication & Authorization System

### 1.1 Technical Design

**Stack**:
- FastAPI Security utilities (OAuth2, JWT)
- python-jose for JWT handling
- passlib + bcrypt for password hashing
- Azure AD integration for enterprise SSO

**Architecture**:
```
User Request → API Gateway → JWT Validation → RBAC Check → Route Handler
                                ↓                    ↓
                          Token Blacklist       Role-Permission Matrix
```

### 1.2 Database Schema

```sql
-- Users table
CREATE TABLE users (
    user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name_en VARCHAR(255),
    full_name_ar VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    last_login_at TIMESTAMP,
    failed_login_attempts INT DEFAULT 0,
    locked_until TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Roles table
CREATE TABLE roles (
    role_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    role_name VARCHAR(50) UNIQUE NOT NULL,
    description_en TEXT,
    description_ar TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Permissions table
CREATE TABLE permissions (
    permission_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    permission_name VARCHAR(100) UNIQUE NOT NULL,
    resource VARCHAR(50) NOT NULL, -- controls, evidence, reports
    action VARCHAR(20) NOT NULL, -- create, read, update, delete
    description_en TEXT,
    description_ar TEXT
);

-- Role-Permission mapping
CREATE TABLE role_permissions (
    role_id UUID REFERENCES roles(role_id) ON DELETE CASCADE,
    permission_id UUID REFERENCES permissions(permission_id) ON DELETE CASCADE,
    PRIMARY KEY (role_id, permission_id)
);

-- User-Role mapping
CREATE TABLE user_roles (
    user_id UUID REFERENCES users(user_id) ON DELETE CASCADE,
    role_id UUID REFERENCES roles(role_id) ON DELETE CASCADE,
    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    assigned_by UUID REFERENCES users(user_id),
    PRIMARY KEY (user_id, role_id)
);

-- Refresh tokens table
CREATE TABLE refresh_tokens (
    token_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(user_id) ON DELETE CASCADE,
    token_hash VARCHAR(255) NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    revoked_at TIMESTAMP
);

-- API keys for service-to-service
CREATE TABLE api_keys (
    api_key_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    key_hash VARCHAR(255) NOT NULL,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    scopes JSONB, -- ["controls:read", "evidence:write"]
    expires_at TIMESTAMP,
    last_used_at TIMESTAMP,
    created_by UUID REFERENCES users(user_id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    revoked_at TIMESTAMP
);
```

### 1.3 Default Roles & Permissions

| Role | Permissions | Use Case |
|------|------------|----------|
| **Admin** | All permissions | System administrators |
| **Compliance Officer** | controls:*, evidence:*, reports:read | Manage compliance controls |
| **Auditor** | All read permissions, evidence:create/update | Audit activities |
| **Analyst** | controls:read, evidence:read, reports:read | Reporting and analysis |
| **Viewer** | controls:read (public), reports:read | Read-only access |

### 1.4 Implementation Files

**File**: `src/backend/auth/models.py`
```python
from sqlalchemy import Column, String, Boolean, DateTime, Integer, ForeignKey, Table
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from core.database import Base
import uuid
from datetime import datetime

class User(Base):
    __tablename__ = "users"
    
    user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name_en = Column(String(255))
    full_name_ar = Column(String(255))
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    last_login_at = Column(DateTime)
    failed_login_attempts = Column(Integer, default=0)
    locked_until = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    roles = relationship("Role", secondary="user_roles", back_populates="users")
    refresh_tokens = relationship("RefreshToken", back_populates="user", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="user")

class Role(Base):
    __tablename__ = "roles"
    
    role_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    role_name = Column(String(50), unique=True, nullable=False)
    description_en = Column(String)
    description_ar = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    users = relationship("User", secondary="user_roles", back_populates="roles")
    permissions = relationship("Permission", secondary="role_permissions", back_populates="roles")

class Permission(Base):
    __tablename__ = "permissions"
    
    permission_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    permission_name = Column(String(100), unique=True, nullable=False)
    resource = Column(String(50), nullable=False)
    action = Column(String(20), nullable=False)
    description_en = Column(String)
    description_ar = Column(String)
    
    roles = relationship("Role", secondary="role_permissions", back_populates="permissions")

# Association tables
user_roles = Table(
    'user_roles',
    Base.metadata,
    Column('user_id', UUID(as_uuid=True), ForeignKey('users.user_id', ondelete='CASCADE'), primary_key=True),
    Column('role_id', UUID(as_uuid=True), ForeignKey('roles.role_id', ondelete='CASCADE'), primary_key=True),
    Column('assigned_at', DateTime, default=datetime.utcnow),
    Column('assigned_by', UUID(as_uuid=True), ForeignKey('users.user_id'))
)

role_permissions = Table(
    'role_permissions',
    Base.metadata,
    Column('role_id', UUID(as_uuid=True), ForeignKey('roles.role_id', ondelete='CASCADE'), primary_key=True),
    Column('permission_id', UUID(as_uuid=True), ForeignKey('permissions.permission_id', ondelete='CASCADE'), primary_key=True)
)

class RefreshToken(Base):
    __tablename__ = "refresh_tokens"
    
    token_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)
    token_hash = Column(String(255), nullable=False)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    revoked_at = Column(DateTime)
    
    user = relationship("User", back_populates="refresh_tokens")

class APIKey(Base):
    __tablename__ = "api_keys"
    
    api_key_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    key_hash = Column(String(255), nullable=False, unique=True)
    name = Column(String(100), nullable=False)
    description = Column(String)
    scopes = Column(JSONB)
    expires_at = Column(DateTime)
    last_used_at = Column(DateTime)
    created_by = Column(UUID(as_uuid=True), ForeignKey('users.user_id'))
    created_at = Column(DateTime, default=datetime.utcnow)
    revoked_at = Column(DateTime)
```

**File**: `src/backend/auth/security.py`
```python
from datetime import datetime, timedelta
from typing import Optional, List
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import get_db
from core.config import settings
from auth.models import User, RefreshToken
import hashlib

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")
http_bearer = HTTPBearer()

# JWT settings
SECRET_KEY = settings.SECRET_KEY  # From Azure Key Vault in production
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash password using bcrypt."""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "access"
    })
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(user_id: str) -> str:
    """Create refresh token."""
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode = {
        "sub": str(user_id),
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "refresh"
    }
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    """Get current authenticated user."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        token_type: str = payload.get("type")
        
        if user_id is None or token_type != "access":
            raise credentials_exception
            
    except JWTError:
        raise credentials_exception
    
    # Get user from database
    from sqlalchemy import select
    result = await db.execute(select(User).where(User.user_id == user_id))
    user = result.scalar_one_or_none()
    
    if user is None:
        raise credentials_exception
    
    if not user.is_active:
        raise HTTPException(status_code=403, detail="User account is inactive")
    
    return user

async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get current active user."""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

def require_permission(resource: str, action: str):
    """Dependency to check if user has required permission."""
    async def permission_checker(
        current_user: User = Depends(get_current_active_user)
    ):
        # Check if user has permission through roles
        for role in current_user.roles:
            for permission in role.permissions:
                if permission.resource == resource and permission.action == action:
                    return current_user
                # Check for wildcard permissions
                if permission.resource == resource and permission.action == "*":
                    return current_user
                if permission.resource == "*" and permission.action == "*":
                    return current_user
        
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Permission denied: {resource}:{action}"
        )
    
    return permission_checker

def require_role(role_name: str):
    """Dependency to check if user has required role."""
    async def role_checker(
        current_user: User = Depends(get_current_active_user)
    ):
        user_roles = [role.role_name for role in current_user.roles]
        if role_name not in user_roles and "Admin" not in user_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role required: {role_name}"
            )
        return current_user
    
    return role_checker
```

### 1.5 Integration Steps

1. Add dependencies to `src/backend/requirements.txt`:
```
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
```

2. Create Alembic migration:
```bash
alembic revision -m "add_authentication_system"
```

3. Update existing routers to require authentication:
```python
from auth.security import get_current_active_user, require_permission

@router.get("/controls", dependencies=[Depends(require_permission("controls", "read"))])
async def list_controls(...):
    ...
```

4. Add authentication router to `main.py`:
```python
from auth.router import router as auth_router
app.include_router(auth_router, prefix="/api/v1/auth", tags=["authentication"])
```

---

## 2. Data Encryption

### 2.1 Transport Layer Security (TLS/HTTPS)

**Implementation**:
```python
# src/backend/core/config.py
class Settings(BaseSettings):
    # Force HTTPS in production
    FORCE_HTTPS: bool = True
    
    # TLS settings
    TLS_CERT_FILE: str = "/etc/ssl/certs/server.crt"
    TLS_KEY_FILE: str = "/etc/ssl/private/server.key"
    TLS_MIN_VERSION: str = "TLSv1.2"  # NCA requirement
```

**Nginx configuration** (deployment/nginx.conf):
```nginx
server {
    listen 443 ssl http2;
    server_name sico.example.sa;
    
    # TLS 1.2+ only (NCA requirement)
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers 'ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384';
    ssl_prefer_server_ciphers on;
    
    ssl_certificate /etc/ssl/certs/server.crt;
    ssl_certificate_key /etc/ssl/private/server.key;
    
    # HSTS (NCA requirement)
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    
    location / {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 2.2 Database Encryption at Rest

**PostgreSQL TLS Configuration**:
```yaml
# deployment/docker-compose.yml
services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: sico_grc
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      # Enable SSL
      POSTGRES_INITDB_ARGS: "--data-checksums"
    volumes:
      - ./deployment/postgres/ssl:/var/lib/postgresql/ssl:ro
      - ./deployment/postgres/postgresql.conf:/etc/postgresql/postgresql.conf
    command: >
      postgres
      -c ssl=on
      -c ssl_cert_file=/var/lib/postgresql/ssl/server.crt
      -c ssl_key_file=/var/lib/postgresql/ssl/server.key
      -c ssl_ca_file=/var/lib/postgresql/ssl/ca.crt
```

**Connection string update**:
```python
# src/backend/core/database.py
DATABASE_URL = f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{database}?ssl=require"
```

### 2.3 Field-Level Encryption for PII

**Implementation using cryptography**:

```python
# src/backend/core/encryption.py
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
from cryptography.hazmat.backends import default_backend
from base64 import urlsafe_b64encode, urlsafe_b64decode
from core.config import settings
import os

class FieldEncryption:
    """Field-level encryption for PII using Fernet (AES-256)."""
    
    def __init__(self):
        # Get encryption key from Azure Key Vault
        self.key = self._get_encryption_key()
        self.cipher = Fernet(self.key)
    
    def _get_encryption_key(self) -> bytes:
        """Get encryption key from secure storage."""
        # In production, fetch from Azure Key Vault
        if settings.ENVIRONMENT == "production":
            from azure.keyvault.secrets import SecretClient
            from azure.identity import DefaultAzureCredential
            
            client = SecretClient(
                vault_url=settings.AZURE_KEY_VAULT_URL,
                credential=DefaultAzureCredential()
            )
            key = client.get_secret("sico-encryption-key").value
            return key.encode()
        else:
            # Development: use key from environment
            return settings.ENCRYPTION_KEY.encode()
    
    def encrypt(self, plaintext: str) -> str:
        """Encrypt plaintext string."""
        if not plaintext:
            return plaintext
        encrypted = self.cipher.encrypt(plaintext.encode())
        return urlsafe_b64encode(encrypted).decode()
    
    def decrypt(self, ciphertext: str) -> str:
        """Decrypt ciphertext string."""
        if not ciphertext:
            return ciphertext
        decoded = urlsafe_b64decode(ciphertext.encode())
        decrypted = self.cipher.decrypt(decoded)
        return decrypted.decode()

# Global instance
field_encryption = FieldEncryption()

# SQLAlchemy custom type for encrypted fields
from sqlalchemy.types import TypeDecorator, String

class EncryptedString(TypeDecorator):
    """SQLAlchemy type for encrypted string fields."""
    
    impl = String
    cache_ok = True
    
    def process_bind_param(self, value, dialect):
        """Encrypt before storing."""
        if value is not None:
            return field_encryption.encrypt(value)
        return value
    
    def process_result_value(self, value, dialect):
        """Decrypt after retrieving."""
        if value is not None:
            return field_encryption.decrypt(value)
        return value
```

**Usage in models**:
```python
from core.encryption import EncryptedString

class User(Base):
    __tablename__ = "users"
    
    email = Column(EncryptedString(255), unique=True, nullable=False)  # Encrypted
    full_name_en = Column(EncryptedString(255))  # Encrypted if PII
```

### 2.4 Azure Key Vault Integration

**Setup script** (`scripts/setup_key_vault.sh`):
```bash
#!/bin/bash
# Setup Azure Key Vault for SICO GRC

RESOURCE_GROUP="sico-grc-rg"
KEY_VAULT_NAME="sico-grc-kv"
LOCATION="saudiarabia-central"

# Create Key Vault
az keyvault create \
  --name $KEY_VAULT_NAME \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION \
  --enable-rbac-authorization true

# Generate encryption key
ENCRYPTION_KEY=$(python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")

# Store secrets
az keyvault secret set --vault-name $KEY_VAULT_NAME --name "sico-encryption-key" --value "$ENCRYPTION_KEY"
az keyvault secret set --vault-name $KEY_VAULT_NAME --name "sico-jwt-secret" --value "$(openssl rand -base64 32)"
az keyvault secret set --vault-name $KEY_VAULT_NAME --name "sico-db-password" --value "$DB_PASSWORD"
```

---

## 3. Audit Logging System

### 3.1 Audit Log Schema

```sql
CREATE TABLE audit_logs (
    log_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    user_id UUID REFERENCES users(user_id),
    user_email VARCHAR(255),
    action VARCHAR(50) NOT NULL, -- CREATE, READ, UPDATE, DELETE, LOGIN, LOGOUT
    resource_type VARCHAR(50) NOT NULL, -- control, evidence, report, user
    resource_id VARCHAR(255),
    endpoint VARCHAR(255),
    http_method VARCHAR(10),
    status_code INT,
    ip_address INET,
    user_agent TEXT,
    request_body JSONB,
    response_body JSONB,
    changes JSONB, -- Before/after for updates
    session_id UUID,
    severity VARCHAR(20), -- INFO, WARNING, ERROR, CRITICAL
    compliance_event BOOLEAN DEFAULT FALSE, -- Flag for compliance-relevant events
    retention_until DATE, -- 7 years per NCA
    INDEX idx_audit_user_id (user_id),
    INDEX idx_audit_timestamp (timestamp),
    INDEX idx_audit_resource (resource_type, resource_id),
    INDEX idx_audit_action (action),
    INDEX idx_audit_compliance (compliance_event) WHERE compliance_event = TRUE
);

-- Audit log is append-only (no updates/deletes)
CREATE POLICY audit_log_append_only ON audit_logs
    USING (false)
    WITH CHECK (true);
```

### 3.2 Audit Logging Middleware

**File**: `src/backend/middleware/audit_logger.py`
```python
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import async_session
from auth.models import User
import uuid
import json
from datetime import datetime, timedelta

class AuditLogMiddleware(BaseHTTPMiddleware):
    """Middleware to log all API requests for audit trail."""
    
    async def dispatch(self, request: Request, call_next):
        # Generate request ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        # Extract user info (if authenticated)
        user_id = None
        user_email = None
        if hasattr(request.state, "user"):
            user_id = request.state.user.user_id
            user_email = request.state.user.email
        
        # Capture request body (if applicable)
        request_body = None
        if request.method in ["POST", "PUT", "PATCH"]:
            try:
                body = await request.body()
                if body:
                    request_body = json.loads(body)
                    # Mask sensitive fields
                    if isinstance(request_body, dict):
                        for sensitive_field in ["password", "token", "secret"]:
                            if sensitive_field in request_body:
                                request_body[sensitive_field] = "***REDACTED***"
            except:
                request_body = None
        
        # Process request
        start_time = datetime.utcnow()
        response = await call_next(request)
        duration = (datetime.utcnow() - start_time).total_seconds()
        
        # Log to database (async)
        await self._log_to_database(
            user_id=user_id,
            user_email=user_email,
            action=self._extract_action(request.method),
            resource_type=self._extract_resource_type(request.url.path),
            endpoint=request.url.path,
            http_method=request.method,
            status_code=response.status_code,
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent"),
            request_body=request_body,
            session_id=request.state.request_id,
            compliance_event=self._is_compliance_event(request.url.path, request.method)
        )
        
        return response
    
    async def _log_to_database(self, **log_data):
        """Async database logging."""
        async with async_session() as db:
            from audit.models import AuditLog
            
            # Calculate retention date (7 years per NCA)
            retention_until = datetime.utcnow().date() + timedelta(days=365 * 7)
            
            audit_log = AuditLog(
                **log_data,
                timestamp=datetime.utcnow(),
                retention_until=retention_until
            )
            db.add(audit_log)
            await db.commit()
    
    def _extract_action(self, http_method: str) -> str:
        """Map HTTP method to action."""
        mapping = {
            "GET": "READ",
            "POST": "CREATE",
            "PUT": "UPDATE",
            "PATCH": "UPDATE",
            "DELETE": "DELETE"
        }
        return mapping.get(http_method, "UNKNOWN")
    
    def _extract_resource_type(self, path: str) -> str:
        """Extract resource type from path."""
        parts = path.split("/")
        if len(parts) >= 4:
            return parts[3]  # /api/v1/{resource}
        return "unknown"
    
    def _is_compliance_event(self, path: str, method: str) -> bool:
        """Check if event is compliance-relevant."""
        compliance_endpoints = [
            "/controls",
            "/evidence",
            "/reports",
            "/auth/login",
            "/auth/logout",
            "/users"
        ]
        return any(endpoint in path for endpoint in compliance_endpoints)
```

### 3.3 Audit Log Query Interface

**File**: `src/backend/audit/router.py`
```python
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from core.database import get_db
from auth.security import require_role
from audit.models import AuditLog
from audit.schemas import AuditLogResponse, AuditLogFilter
from typing import List
from datetime import datetime, timedelta

router = APIRouter()

@router.get(
    "/audit-logs",
    response_model=List[AuditLogResponse],
    dependencies=[Depends(require_role("Auditor"))]
)
async def query_audit_logs(
    user_id: Optional[str] = None,
    resource_type: Optional[str] = None,
    action: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    compliance_only: bool = False,
    offset: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """Query audit logs with filters (Auditor role required)."""
    
    query = select(AuditLog)
    
    # Apply filters
    if user_id:
        query = query.where(AuditLog.user_id == user_id)
    if resource_type:
        query = query.where(AuditLog.resource_type == resource_type)
    if action:
        query = query.where(AuditLog.action == action)
    if start_date:
        query = query.where(AuditLog.timestamp >= start_date)
    if end_date:
        query = query.where(AuditLog.timestamp <= end_date)
    if compliance_only:
        query = query.where(AuditLog.compliance_event == True)
    
    # Order and paginate
    query = query.order_by(AuditLog.timestamp.desc()).offset(offset).limit(limit)
    
    result = await db.execute(query)
    return result.scalars().all()

@router.get(
    "/audit-logs/summary",
    dependencies=[Depends(require_role("Auditor"))]
)
async def get_audit_summary(
    days: int = 30,
    db: AsyncSession = Depends(get_db)
):
    """Get audit log summary statistics."""
    
    since = datetime.utcnow() - timedelta(days=days)
    
    # Total events
    total_query = select(func.count(AuditLog.log_id)).where(AuditLog.timestamp >= since)
    total_result = await db.execute(total_query)
    total_events = total_result.scalar()
    
    # By action
    by_action_query = select(
        AuditLog.action,
        func.count(AuditLog.log_id)
    ).where(AuditLog.timestamp >= since).group_by(AuditLog.action)
    by_action_result = await db.execute(by_action_query)
    
    # By user (top 10)
    by_user_query = select(
        AuditLog.user_email,
        func.count(AuditLog.log_id)
    ).where(AuditLog.timestamp >= since).group_by(AuditLog.user_email).order_by(func.count(AuditLog.log_id).desc()).limit(10)
    by_user_result = await db.execute(by_user_query)
    
    return {
        "period_days": days,
        "total_events": total_events,
        "by_action": dict(by_action_result.all()),
        "top_users": dict(by_user_result.all()),
        "compliance_events": total_events  # Filter for compliance_event=True
    }
```

---

## 4. Input Validation & Security Headers

### 4.1 Enhanced Pydantic Validation

**File**: `src/backend/core/validators.py`
```python
from pydantic import validator, Field
from typing import Optional
import re

class SecurityValidators:
    """Common security validators for Pydantic models."""
    
    @staticmethod
    def validate_no_sql_injection(value: str) -> str:
        """Check for SQL injection patterns."""
        sql_patterns = [
            r"(\bunion\b.*\bselect\b)",
            r"(\bselect\b.*\bfrom\b)",
            r"(\binsert\b.*\binto\b)",
            r"(\bdelete\b.*\bfrom\b)",
            r"(\bdrop\b.*\btable\b)",
            r"(--)",
            r"(;.*--)"
        ]
        for pattern in sql_patterns:
            if re.search(pattern, value.lower()):
                raise ValueError("Potential SQL injection detected")
        return value
    
    @staticmethod
    def validate_no_xss(value: str) -> str:
        """Check for XSS patterns."""
        xss_patterns = [
            r"<script",
            r"javascript:",
            r"onerror=",
            r"onload=",
            r"<iframe"
        ]
        for pattern in xss_patterns:
            if re.search(pattern, value.lower()):
                raise ValueError("Potential XSS detected")
        return value
    
    @staticmethod
    def validate_arabic_or_english(value: str) -> str:
        """Validate string contains only Arabic or English characters."""
        if not re.match(r'^[\u0600-\u06FFa-zA-Z0-9\s\-.,!?()]+$', value):
            raise ValueError("Only Arabic, English, and common punctuation allowed")
        return value
```

### 4.2 Security Headers Middleware

**File**: `src/backend/middleware/security_headers.py`
```python
from starlette.middleware.base import BaseHTTPMiddleware

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses."""
    
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        
        # NCA and OWASP recommended headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self' data:; "
            "connect-src 'self'"
        )
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        
        return response
```

### 4.3 Rate Limiting

**File**: `src/backend/middleware/rate_limiter.py`
```python
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
import redis.asyncio as redis
from datetime import timedelta

class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting to prevent brute force attacks."""
    
    def __init__(self, app, redis_url: str, requests_per_minute: int = 60):
        super().__init__(app)
        self.redis = redis.from_url(redis_url)
        self.rate_limit = requests_per_minute
    
    async def dispatch(self, request: Request, call_next):
        # Get client identifier (IP + User ID if authenticated)
        client_id = request.client.host
        if hasattr(request.state, "user"):
            client_id = f"{client_id}:{request.state.user.user_id}"
        
        # Check rate limit
        key = f"rate_limit:{client_id}"
        current = await self.redis.incr(key)
        
        if current == 1:
            await self.redis.expire(key, 60)  # 1 minute window
        
        if current > self.rate_limit:
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded. Please try again later."
            )
        
        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(self.rate_limit)
        response.headers["X-RateLimit-Remaining"] = str(max(0, self.rate_limit - current))
        
        return response
```

---

## 5. Implementation Checklist

### Week 1: Authentication & Authorization

- [ ] Day 1-2: Database schema and models
  - [ ] Create auth tables migration
  - [ ] Implement User, Role, Permission models
  - [ ] Create default roles and permissions seed data
  
- [ ] Day 3-4: Authentication logic
  - [ ] Implement JWT token generation/validation
  - [ ] Add password hashing and verification
  - [ ] Create login/logout endpoints
  - [ ] Add refresh token mechanism
  
- [ ] Day 5: Authorization
  - [ ] Implement RBAC permission checker
  - [ ] Add role-based dependencies
  - [ ] Update existing routes with auth requirements
  - [ ] Test permission enforcement

### Week 2: Encryption, Audit Logging, Security

- [ ] Day 6-7: Data encryption
  - [ ] Enable PostgreSQL TLS
  - [ ] Implement field-level encryption
  - [ ] Azure Key Vault integration
  - [ ] Migrate sensitive fields to encrypted columns
  
- [ ] Day 8-9: Audit logging
  - [ ] Create audit log schema and models
  - [ ] Implement audit middleware
  - [ ] Add audit log query endpoints
  - [ ] Test audit trail completeness
  
- [ ] Day 10: Security hardening
  - [ ] Add input validation to all schemas
  - [ ] Implement security headers middleware
  - [ ] Add rate limiting
  - [ ] Configure CORS properly
  - [ ] Security testing and vulnerability scan

---

## 6. Testing Requirements

### 6.1 Authentication Tests

```python
# tests/backend/test_auth.py
async def test_user_registration():
    """Test user can register with valid credentials."""
    
async def test_login_success():
    """Test user can login with correct password."""
    
async def test_login_failure():
    """Test login fails with incorrect password."""
    
async def test_jwt_token_validation():
    """Test JWT token is validated correctly."""
    
async def test_refresh_token():
    """Test refresh token can generate new access token."""
    
async def test_permission_enforcement():
    """Test users without permission are blocked."""
    
async def test_account_lockout():
    """Test account locks after failed attempts."""
```

### 6.2 Encryption Tests

```python
# tests/backend/test_encryption.py
async def test_field_encryption():
    """Test PII fields are encrypted in database."""
    
async def test_tls_connection():
    """Test database connection uses TLS."""
    
async def test_key_rotation():
    """Test encryption key rotation process."""
```

### 6.3 Audit Tests

```python
# tests/backend/test_audit.py
async def test_audit_log_creation():
    """Test audit log is created for all actions."""
    
async def test_audit_log_immutability():
    """Test audit logs cannot be modified/deleted."""
    
async def test_audit_log_retention():
    """Test audit logs are retained for 7 years."""
```

---

## 7. Success Criteria

### Functional Requirements
- [ ] Users can register, login, and logout
- [ ] JWT-based authentication works for all endpoints
- [ ] RBAC enforces permissions correctly
- [ ] All database connections use TLS
- [ ] PII fields are encrypted at rest
- [ ] All API requests are logged to audit trail
- [ ] Audit logs are tamper-proof and retained for 7 years
- [ ] Security headers are present on all responses
- [ ] Rate limiting prevents brute force attacks

### Compliance Requirements
- [ ] ECC-IS-3 (Access Control): 100% compliant
- [ ] ECC-IS-4 (Cryptography): 100% compliant
- [ ] CCC-SEC-01 (Data Encryption): 100% compliant
- [ ] CCC-SEC-04 (Logging & Monitoring): 80% compliant
- [ ] PDPL Article 29 (Security Measures): 75% compliant
- [ ] ISO 27001 A.9 (Access Control): 90% compliant
- [ ] NIST AC family: 85% compliant

### Performance Requirements
- [ ] Authentication adds < 50ms latency
- [ ] Audit logging is asynchronous and non-blocking
- [ ] Encryption/decryption overhead < 10ms per field

---

## 8. Next Steps After Phase 2.1

Upon completion of Phase 2.1, proceed to:
- **Phase 2.2**: Data Protection & Privacy (consent management, DSAR, breach notification)
- **Phase 2.3**: AI Governance & Operational Security
- **Phase 2.4**: Compliance Documentation & Certification

**Estimated Overall Timeline**: 8 weeks to reach 100% compliance readiness

---

**Document Version**: 1.0  
**Last Updated**: February 4, 2026  
**Owner**: SICO GRC Security Team
