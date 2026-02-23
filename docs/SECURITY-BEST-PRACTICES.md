# Security Best Practices Guide

## 🔐 SICO GRC Platform - Cybersecurity Best Practices

**Audience**: Developers, DevOps Engineers, Security Teams  
**Compliance**: NCA ECC, CCC, PDPL Standards  
**Version**: 1.0

This guide provides comprehensive security best practices for developing, deploying, and maintaining the SICO GRC Platform following Saudi Arabian National Cybersecurity Authority (NCA) standards.

---

## 📚 Table of Contents

1. [Secure Development Lifecycle](#secure-development-lifecycle)
2. [Code Security](#code-security)
3. [Dependency Management](#dependency-management)
4. [Authentication & Authorization](#authentication--authorization)
5. [Data Protection](#data-protection)
6. [API Security](#api-security)
7. [Container Security](#container-security)
8. [Infrastructure Security](#infrastructure-security)
9. [Monitoring & Logging](#monitoring--logging)
10. [Incident Response](#incident-response)

---

## 🔄 Secure Development Lifecycle

### 1. Planning Phase

**Security Requirements**:
- [ ] Identify sensitive data and processing activities
- [ ] Define authentication and authorization requirements
- [ ] Document compliance requirements (ECC, CCC, PDPL)
- [ ] Conduct threat modeling
- [ ] Define security acceptance criteria

**NCA Compliance**: ECC 1-1-1 (Cybersecurity Policy)

### 2. Design Phase

**Security Architecture**:
- [ ] Apply principle of least privilege
- [ ] Implement defense in depth
- [ ] Design for fail-secure (not fail-open)
- [ ] Document security controls
- [ ] Review architecture with security team

**NCA Compliance**: ECC 2-1-1 (Data Classification)

### 3. Development Phase

**Secure Coding**:
- [ ] Follow OWASP Top 10 guidelines
- [ ] Use security linters (Bandit, ESLint security plugin)
- [ ] Implement input validation
- [ ] Use parameterized queries
- [ ] Handle errors securely (no sensitive data in errors)

**Code Review**:
- [ ] Mandatory peer review for all code
- [ ] Security-focused review for critical components
- [ ] Use automated security scanning tools
- [ ] Document security decisions

**NCA Compliance**: ECC 2-5-1 (Vulnerability Assessment)

### 4. Testing Phase

**Security Testing**:
- [ ] Unit tests for security functions
- [ ] Integration tests for authentication/authorization
- [ ] Security regression tests
- [ ] Penetration testing (for production releases)
- [ ] Vulnerability scanning

**NCA Compliance**: ECC 2-5-1 (Vulnerability Assessment)

### 5. Deployment Phase

**Secure Deployment**:
- [ ] All security scans passed
- [ ] No HIGH/CRITICAL vulnerabilities
- [ ] Secrets properly configured
- [ ] TLS/SSL certificates valid
- [ ] Monitoring and alerting configured

**NCA Compliance**: ECC 2-5-2 (Vulnerability Remediation)

### 6. Maintenance Phase

**Ongoing Security**:
- [ ] Regular security updates
- [ ] Vulnerability monitoring
- [ ] Security patch management
- [ ] Periodic security audits
- [ ] Incident response readiness

**NCA Compliance**: ECC 2-5-2 (Vulnerability Remediation)

---

## 💻 Code Security

### Input Validation

**Always validate and sanitize user input**:

```python
# ❌ BAD - Direct use of user input
user_id = request.args.get('user_id')
query = f"SELECT * FROM users WHERE id = {user_id}"

# ✅ GOOD - Parameterized query
user_id = request.args.get('user_id')
if not user_id.isdigit():
    raise ValueError("Invalid user ID")
query = "SELECT * FROM users WHERE id = ?"
cursor.execute(query, (user_id,))
```

**Validation Rules**:
- Whitelist allowed characters
- Validate data types
- Check length constraints
- Verify format (email, phone, etc.)
- Sanitize before use

### SQL Injection Prevention

```python
# ❌ BAD - String concatenation
username = request.form['username']
query = f"SELECT * FROM users WHERE username = '{username}'"

# ✅ GOOD - ORM or parameterized queries
from sqlalchemy import text

username = request.form['username']
query = text("SELECT * FROM users WHERE username = :username")
result = session.execute(query, {"username": username})
```

### Cross-Site Scripting (XSS) Prevention

```javascript
// ❌ BAD - Direct HTML insertion
element.innerHTML = userInput;

// ✅ GOOD - Text content only
element.textContent = userInput;

// ✅ GOOD - Sanitized HTML
import DOMPurify from 'dompurify';
const clean = DOMPurify.sanitize(userInput);
element.innerHTML = clean;
```

### Command Injection Prevention

```python
# ❌ BAD - Shell command with user input
import os
filename = request.args.get('file')
os.system(f"cat {filename}")

# ✅ GOOD - Use safe alternatives
import subprocess
filename = request.args.get('file')
# Validate filename
if not re.match(r'^[a-zA-Z0-9_-]+\.txt$', filename):
    raise ValueError("Invalid filename")
result = subprocess.run(['cat', filename], capture_output=True, text=True)
```

### Path Traversal Prevention

```python
# ❌ BAD - Direct file path from user
file_path = request.args.get('file')
with open(file_path, 'r') as f:
    content = f.read()

# ✅ GOOD - Validate and sanitize path
import os
from pathlib import Path

base_dir = Path('/app/uploads')
file_name = request.args.get('file')

# Remove any path traversal attempts
safe_path = base_dir / Path(file_name).name

# Verify path is within base directory
if not safe_path.resolve().is_relative_to(base_dir.resolve()):
    raise ValueError("Invalid file path")

with open(safe_path, 'r') as f:
    content = f.read()
```

---

## 📦 Dependency Management

### Keep Dependencies Updated

```bash
# Python - Check for outdated packages
pip list --outdated

# Node.js - Check for updates
npm outdated

# Update dependencies regularly
pip install --upgrade <package>
npm update
```

### Vulnerability Scanning

**Automated Scanning**:
```bash
# Python
pip-audit
safety check

# Node.js
npm audit
npm audit fix
```

**Our CI/CD Pipeline**:
- Automatically scans dependencies daily
- Fails builds on HIGH/CRITICAL vulnerabilities
- Generates SBOM for traceability

### Dependency Pinning

**Python - requirements.txt**:
```text
# ❌ BAD - Unpinned versions
fastapi
pydantic

# ✅ GOOD - Pinned versions
fastapi==0.104.1
pydantic==2.5.0
```

**Node.js - package.json**:
```json
{
  "dependencies": {
    "next": "14.0.4",
    "react": "18.2.0"
  }
}
```

### License Compliance

**Check Licenses**:
```bash
# Python
pip-licenses

# Node.js
npm-license-checker
```

**Avoid GPL Licenses** (unless compatible with your use case)

---

## 🔐 Authentication & Authorization

### Password Security

```python
# ✅ Use bcrypt for password hashing
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Hash password
hashed = pwd_context.hash(plain_password)

# Verify password
is_valid = pwd_context.verify(plain_password, hashed)
```

**Password Requirements**:
- Minimum 12 characters
- Mix of uppercase, lowercase, numbers, special characters
- No common passwords (use dictionary check)
- Implement rate limiting on login attempts
- Force password change on first login

### JWT Token Security

```python
# ✅ Secure JWT implementation
from jose import JWTError, jwt
from datetime import datetime, timedelta

SECRET_KEY = os.getenv("JWT_SECRET_KEY")  # From environment
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
```

**JWT Best Practices**:
- Short expiration times (15-30 minutes)
- Use refresh tokens for extended sessions
- Include minimal data in payload
- Validate signature on every request
- Implement token revocation list

### Multi-Factor Authentication (MFA)

```python
# ✅ Implement TOTP-based MFA
import pyotp

# Generate secret for user
secret = pyotp.random_base32()

# Verify TOTP code
totp = pyotp.TOTP(secret)
is_valid = totp.verify(user_code)
```

### Role-Based Access Control (RBAC)

```python
# ✅ Implement RBAC
from enum import Enum
from fastapi import Depends, HTTPException

class Role(Enum):
    ADMIN = "admin"
    USER = "user"
    AUDITOR = "auditor"

def require_role(required_role: Role):
    def role_checker(current_user = Depends(get_current_user)):
        if current_user.role != required_role:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return current_user
    return role_checker

# Usage
@app.get("/admin/users")
async def list_users(user = Depends(require_role(Role.ADMIN))):
    # Only admins can access
    return {"users": []}
```

---

## 🔒 Data Protection

### Encryption at Rest

```python
# ✅ Encrypt sensitive data before storing
from cryptography.fernet import Fernet

# Generate key (store securely!)
key = Fernet.generate_key()
cipher = Fernet(key)

# Encrypt
encrypted = cipher.encrypt(sensitive_data.encode())

# Decrypt
decrypted = cipher.decrypt(encrypted).decode()
```

**What to Encrypt**:
- Passwords (use bcrypt/argon2)
- API keys and secrets
- Personal Identifiable Information (PII)
- Financial data
- Health information

**NCA Compliance**: PDPL Article 20 (Security Measures)

### Encryption in Transit

```python
# ✅ Enforce HTTPS
from fastapi import FastAPI
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware

app = FastAPI()

# Redirect HTTP to HTTPS
if os.getenv("ENVIRONMENT") == "production":
    app.add_middleware(HTTPSRedirectMiddleware)
```

**TLS Configuration**:
- Use TLS 1.3 (minimum TLS 1.2)
- Strong cipher suites only
- Valid certificates from trusted CA
- Enable HSTS (HTTP Strict Transport Security)

### Data Masking

```python
# ✅ Mask sensitive data in logs
def mask_sensitive(data: str, show_last: int = 4) -> str:
    if len(data) <= show_last:
        return '*' * len(data)
    return '*' * (len(data) - show_last) + data[-show_last:]

# Usage
credit_card = "1234567890123456"
print(f"Card: {mask_sensitive(credit_card, 4)}")  # Card: ************3456
```

### Data Retention

```python
# ✅ Implement data retention policies
from datetime import datetime, timedelta

def cleanup_old_data():
    """Delete data older than retention period"""
    retention_days = 90
    cutoff_date = datetime.utcnow() - timedelta(days=retention_days)
    
    # Delete old records
    session.query(AuditLog).filter(
        AuditLog.created_at < cutoff_date
    ).delete()
    
    session.commit()
```

**NCA Compliance**: PDPL Article 17 (Retention Limitation)

---

## 🌐 API Security

### Rate Limiting

```python
# ✅ Implement rate limiting
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.get("/api/data")
@limiter.limit("60/minute")
async def get_data(request: Request):
    return {"data": "value"}
```

### CORS Configuration

```python
# ✅ Restrict CORS appropriately
from fastapi.middleware.cors import CORSMiddleware

allowed_origins = [
    "https://app.sicogrc.com",
    "https://admin.sicogrc.com"
]

if os.getenv("ENVIRONMENT") == "development":
    allowed_origins.append("http://localhost:3000")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)
```

### API Authentication

```python
# ✅ Require authentication for all endpoints
from fastapi import Security
from fastapi.security import HTTPBearer

security = HTTPBearer()

@app.get("/api/secure")
async def secure_endpoint(token = Security(security)):
    # Verify token
    payload = verify_token(token.credentials)
    return {"message": "Authorized"}
```

### Input Validation

```python
# ✅ Use Pydantic for request validation
from pydantic import BaseModel, validator, EmailStr

class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str
    
    @validator('username')
    def username_alphanumeric(cls, v):
        if not v.isalnum():
            raise ValueError('Username must be alphanumeric')
        if len(v) < 3 or len(v) > 20:
            raise ValueError('Username must be 3-20 characters')
        return v
    
    @validator('password')
    def password_strong(cls, v):
        if len(v) < 12:
            raise ValueError('Password must be at least 12 characters')
        # Add more password rules
        return v
```

---

## 🐳 Container Security

### Use Minimal Base Images

```dockerfile
# ❌ BAD - Large base image
FROM ubuntu:latest

# ✅ GOOD - Minimal base image
FROM python:3.11-slim-alpine

# ✅ BETTER - Distroless
FROM gcr.io/distroless/python3-debian11
```

### Run as Non-Root

```dockerfile
# ✅ Create and use non-root user
FROM python:3.11-slim

# Create app user
RUN useradd -m -u 1000 appuser

# Set working directory
WORKDIR /app

# Copy and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Change ownership
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Run application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0"]
```

### Multi-Stage Builds

```dockerfile
# ✅ Multi-stage build for security
# Stage 1: Build
FROM python:3.11 as builder

WORKDIR /app
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim

# Copy only necessary files
COPY --from=builder /root/.local /root/.local
COPY app/ /app/

# Make sure scripts are in PATH
ENV PATH=/root/.local/bin:$PATH

# Run as non-root
RUN useradd -m appuser
USER appuser

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0"]
```

### Scan Images

```bash
# ✅ Scan before pushing
trivy image myapp:latest

# ✅ Our CI/CD does this automatically
# See .github/workflows/security-scan.yml
```

---

## 🏗️ Infrastructure Security

### Secrets Management

```bash
# ❌ BAD - Hardcoded secrets
DATABASE_URL="postgresql://user:password@localhost/db"

# ✅ GOOD - Environment variables
DATABASE_URL="${DATABASE_URL}"

# ✅ BETTER - Secrets manager
# AWS Secrets Manager, Azure Key Vault, HashiCorp Vault
```

### Network Segmentation

```yaml
# ✅ Docker network isolation
networks:
  frontend:
    driver: bridge
  backend:
    driver: bridge
  database:
    driver: bridge
    internal: true  # No external access

services:
  frontend:
    networks:
      - frontend
  
  backend:
    networks:
      - frontend
      - backend
  
  database:
    networks:
      - database  # Isolated from internet
```

### Firewall Rules

```bash
# ✅ Restrictive firewall rules
# Allow only necessary ports
# - 443 (HTTPS)
# - 22 (SSH, restricted to bastion)

# Block all other inbound traffic
```

---

## 📊 Monitoring & Logging

### Security Event Logging

```python
# ✅ Log security events
import logging

security_logger = logging.getLogger('security')

def log_security_event(event_type: str, user_id: str, details: dict):
    security_logger.info(
        f"Security Event: {event_type}",
        extra={
            "event_type": event_type,
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat(),
            "details": details
        }
    )

# Usage
log_security_event(
    "failed_login",
    user_id="user123",
    details={"ip": "192.168.1.1", "attempts": 3}
)
```

**What to Log**:
- Authentication events (success/failure)
- Authorization failures
- Data access (especially sensitive data)
- Configuration changes
- Security exceptions
- Admin actions

**What NOT to Log**:
- Passwords (even hashed)
- Credit card numbers
- API keys
- Session tokens

### Monitoring Alerts

```yaml
# ✅ Alert on security events
alerts:
  - name: Multiple failed logins
    condition: failed_login_count > 5
    window: 5m
    action: notify_security_team
  
  - name: Unusual data access
    condition: data_access_outside_hours
    action: notify_admin
  
  - name: Critical vulnerability detected
    condition: vuln_severity == "CRITICAL"
    action: block_deployment
```

---

## 🚨 Incident Response

### Incident Response Plan

1. **Preparation**
   - Maintain incident response playbooks
   - Define roles and responsibilities
   - Keep contact lists updated

2. **Detection**
   - Monitor security events
   - Review alerts
   - Analyze anomalies

3. **Containment**
   - Isolate affected systems
   - Disable compromised accounts
   - Block malicious IPs

4. **Eradication**
   - Remove malware
   - Close vulnerabilities
   - Patch systems

5. **Recovery**
   - Restore from backups
   - Verify system integrity
   - Resume normal operations

6. **Lessons Learned**
   - Document incident
   - Update procedures
   - Improve controls

### Security Incident Documentation

```markdown
# Security Incident Report

## Incident Details
- **ID**: INC-2026-001
- **Date**: 2026-02-04
- **Severity**: High
- **Status**: Resolved

## Description
Brief description of the incident

## Timeline
- 14:00 - Incident detected
- 14:15 - Containment measures applied
- 15:00 - Root cause identified
- 16:00 - Issue resolved

## Impact
- Systems affected
- Data accessed
- Users impacted

## Root Cause
Detailed root cause analysis

## Remediation
- Actions taken
- Preventive measures

## Lessons Learned
- What went well
- What could be improved
```

---

## ✅ Security Checklist

### Pre-Commit Checklist

- [ ] No secrets in code
- [ ] Input validation implemented
- [ ] Error handling doesn't leak sensitive info
- [ ] Security linters pass (Bandit, ESLint)
- [ ] Dependencies updated
- [ ] Tests pass including security tests

### Pre-Deployment Checklist

- [ ] All security scans passed
- [ ] No HIGH/CRITICAL vulnerabilities
- [ ] SBOM generated
- [ ] Configuration reviewed
- [ ] Secrets properly configured
- [ ] TLS/SSL configured
- [ ] Monitoring enabled
- [ ] Backups configured
- [ ] Incident response plan ready

### Regular Maintenance Checklist (Monthly)

- [ ] Review security logs
- [ ] Update dependencies
- [ ] Review access controls
- [ ] Test backups
- [ ] Review and update security policies
- [ ] Security training completed
- [ ] Vulnerability scan results reviewed

---

## 📚 Resources

### Standards & Frameworks
- [NCA Essential Cybersecurity Controls](https://nca.gov.sa/en/pages/controls.html)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)
- [CIS Controls](https://www.cisecurity.org/controls)

### Tools
- [Bandit](https://bandit.readthedocs.io/) - Python security linter
- [Safety](https://pyup.io/safety/) - Python dependency checker
- [Trivy](https://trivy.dev/) - Container scanner
- [OWASP Dependency-Check](https://owasp.org/www-project-dependency-check/)

### Training
- [OWASP Security Training](https://owasp.org/www-project-security-knowledge-framework/)
- [Secure Code Warrior](https://www.securecodewarrior.com/)
- [NCA Training Programs](https://nca.gov.sa/en/pages/training.html)

---

**Version**: 1.0  
**Last Updated**: February 2026  
**Maintained by**: SICO Security Team

**Compliant with**:
- NCA Essential Cybersecurity Controls (ECC)
- NCA Cloud Cybersecurity Controls (CCC)
- Saudi Personal Data Protection Law (PDPL)
- OWASP Security Guidelines
