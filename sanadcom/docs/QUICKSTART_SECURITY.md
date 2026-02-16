# Phase 2.1 Security Implementation - Quick Start Guide

## 🚀 Getting Started

This guide will help you set up and test the newly implemented security features.

---

## Prerequisites

- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- Docker & Docker Compose (optional)

---

## Installation Steps

### 1. Install Dependencies

```bash
cd src/backend
pip install -r requirements.txt
```

### 2. Generate Security Keys

```bash
python scripts/setup_security.py
```

This will:
- Generate SECRET_KEY (for JWT signing)
- Generate ENCRYPTION_KEY (for PII encryption)
- Update `.env` file
- Initialize RBAC system
- Create admin user

**Sample output:**
```
🔐 Security Key Generation
==================================================

SECRET_KEY (for JWT signing):
a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0

ENCRYPTION_KEY (for PII encryption):
xJc8kVdE3mR9nQwL2pYtZ5sHfG7jKbN4vC6xM8aU1oI0eT3rW6yQ9lP2hS5=

⚠️  IMPORTANT: Store these keys securely!
```

### 3. Update Environment Configuration

Check `.env` file was created with proper values:

```bash
cat .env | grep -E "(SECRET_KEY|ENCRYPTION_KEY)"
```

### 4. Run Database Migrations

```bash
cd src/backend
alembic upgrade head
```

This creates all authentication and authorization tables.

### 5. Start the Application

**Option A: Using Docker Compose**
```bash
docker-compose -f deployment/docker-compose.yml up -d
```

**Option B: Manual Start**
```bash
# Start PostgreSQL and Redis
docker-compose -f deployment/docker-compose.yml up -d postgres redis

# Start backend
cd src/backend
python main.py
```

### 6. Verify Security Status

```bash
curl http://localhost:8000/api/v1/security-status
```

Expected response:
```json
{
  "authentication": {
    "jwt_enabled": true,
    "oauth2_ready": true,
    "token_expiry_minutes": 30
  },
  "authorization": {
    "rbac_enabled": true,
    "roles": ["Admin", "Compliance Officer", "Auditor", "Analyst", "Viewer"]
  },
  "encryption": {
    "tls_enabled": false,
    "field_level_encryption": true,
    "algorithm": "AES-256"
  },
  ...
}
```

---

## Testing Authentication

### 1. Register a New User

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "SecurePass123!",
    "full_name_en": "Test User",
    "full_name_ar": "مستخدم تجريبي"
  }'
```

**Password Requirements:**
- Minimum 12 characters
- At least 1 uppercase letter
- At least 1 lowercase letter
- At least 1 digit
- At least 1 special character

### 2. Login

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test@example.com&password=SecurePass123!"
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

### 3. Access Protected Endpoint

```bash
# Save token from login response
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

curl -X GET http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer $TOKEN"
```

### 4. Test Rate Limiting

```bash
# Send 61 requests in a row (should get 429 on 61st)
for i in {1..61}; do
  curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8000/api/v1/health
done
```

Expected: First 60 requests return `200`, 61st returns `429 Too Many Requests`

### 5. Test Account Lockout

```bash
# Try to login with wrong password 6 times
for i in {1..6}; do
  curl -X POST http://localhost:8000/api/v1/auth/login \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "username=test@example.com&password=wrongpassword"
done
```

After 5 failed attempts, 6th attempt should return:
```json
{
  "detail": "Account locked. Try again in 30 minutes"
}
```

---

## Testing Authorization (RBAC)

### 1. Assign Admin Role to User

First, login with admin account, then:

```bash
# Get user ID
USER_ID=$(curl -X GET http://localhost:8000/api/v1/auth/users \
  -H "Authorization: Bearer $ADMIN_TOKEN" | jq -r '.[0].user_id')

# Get Admin role ID (from database)
ROLE_ID="..." # Query from roles table

# Assign role
curl -X POST http://localhost:8000/api/v1/auth/users/$USER_ID/roles \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"user_id\": \"$USER_ID\",
    \"role_ids\": [\"$ROLE_ID\"]
  }"
```

### 2. Test Permission Checks

```bash
# Try to access admin endpoint without admin role (should fail with 403)
curl -X GET http://localhost:8000/api/v1/auth/users \
  -H "Authorization: Bearer $USER_TOKEN"

# Try again with admin token (should succeed)
curl -X GET http://localhost:8000/api/v1/auth/users \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

---

## Verifying Security Features

### 1. Check Security Headers

```bash
curl -I http://localhost:8000/api/v1/health
```

Expected headers:
```
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Strict-Transport-Security: max-age=31536000; includeSubDomains
Content-Security-Policy: default-src 'self'
...
```

### 2. Verify Audit Logging

Query the audit logs in PostgreSQL:

```sql
-- Connect to database
psql -h localhost -U postgres -d sico_grc

-- View recent audit logs
SELECT 
  action,
  resource,
  status,
  ip_address,
  created_at
FROM audit_logs
ORDER BY created_at DESC
LIMIT 10;
```

### 3. Test Input Validation

```bash
# Try SQL injection
curl "http://localhost:8000/api/v1/controls?id=1'; DROP TABLE users--"

# Should return 400 Bad Request
```

### 4. Verify PII Encryption

```sql
-- Check that PII fields are encrypted in database
SELECT email, full_name_en FROM users LIMIT 1;

-- Should see base64-encoded encrypted values, not plaintext
```

---

## Common Issues & Troubleshooting

### Issue: "SECRET_KEY not configured"

**Solution:**
Run `python scripts/setup_security.py` or manually set in `.env`:
```bash
export SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))")
```

### Issue: "ENCRYPTION_KEY not configured"

**Solution:**
```bash
export ENCRYPTION_KEY=$(python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")
```

### Issue: "Could not validate credentials"

**Cause:** Token expired or invalid

**Solution:** 
1. Check token expiry time
2. Use refresh token to get new access token
3. Re-login if refresh token also expired

### Issue: "Account locked"

**Cause:** 5 failed login attempts

**Solution:** 
Wait 30 minutes or manually reset in database:
```sql
UPDATE users 
SET failed_login_attempts = 0, locked_until = NULL 
WHERE email = 'user@example.com';
```

### Issue: Rate limit exceeded

**Cause:** Too many requests

**Solution:**
1. Wait for rate limit window to reset
2. Adjust limits in `.env`:
   ```
   RATE_LIMIT_PER_MINUTE=120
   RATE_LIMIT_PER_HOUR=5000
   ```

---

## API Documentation

Full API documentation with authentication examples:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

In Swagger UI:
1. Click "Authorize" button at top
2. Enter access token from login response
3. Click "Authorize" to save
4. All subsequent requests will include the token

---

## Database Schema

### Key Tables

**users**: User accounts with security fields
- `user_id`, `email`, `password_hash`
- `failed_login_attempts`, `locked_until`
- `is_active`, `is_verified`

**roles**: RBAC roles
- `role_id`, `role_name`
- Default: Admin, Compliance Officer, Auditor, Analyst, Viewer

**permissions**: Granular permissions
- `permission_id`, `permission_name`
- Format: `resource:action` (e.g., `controls:read`)

**user_roles**: User-Role mapping (many-to-many)

**role_permissions**: Role-Permission mapping (many-to-many)

**refresh_tokens**: Active refresh tokens
- `token_id`, `user_id`, `token_hash`
- `expires_at`, `revoked_at`

**audit_logs**: Security audit trail (7-year retention)
- `log_id`, `user_id`, `action`, `resource`
- `ip_address`, `user_agent`, `status`
- `created_at`, `details` (JSONB)

---

## Next Steps

1. ✅ Complete Phase 2.1 testing
2. 📝 Document test results
3. 🔒 Deploy to staging environment
4. 🧪 Perform penetration testing
5. 📊 Move to Phase 2.2 (Data Protection)

---

## Support & Resources

- **Compliance Reports**: `docs/compliance/`
- **Implementation Details**: `docs/PHASE_2.1_IMPLEMENTATION_SUMMARY.md`
- **Remediation Plan**: `docs/compliance/PHASE_2.1_REMEDIATION_PLAN.md`
- **Architecture Docs**: `docs/architecture/`

---

## Security Contacts

- **Security Issues**: Report to security team
- **Compliance Questions**: Consult compliance officer
- **Technical Support**: Development team

**Last Updated**: February 5, 2026  
**Version**: 2.1.0 (Security Enhanced)
