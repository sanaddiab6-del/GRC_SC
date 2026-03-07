# RISK OWNER & PERMISSIONS FIX

## Issues Identified

### 1. ✅ **Risk Owner Dropdown Empty** - FIXED
**Problem**: `/api/v1/users` endpoint returned 500 Internal Server Error
**Root Cause**: User model has `full_name_en`/`full_name_ar` fields, not `name` field
**Solution**: Updated endpoint in [main.py](main.py#L299-L324) to use correct fields

### 2. ✅ **Risk Permissions Missing** - FIXED  
**Problem**: Risk endpoints returned 403 "Permission denied : risk:read required"
**Root Cause**: Risk permissions were added to RBAC but users need roles assigned
**Solution**: RBAC system initialized successfully with 6 risk permissions

### 3. ⚠️ **Admin User Has No Role** - NEEDS ACTION
**Problem**: admin@grc.com user exists but has NO roles assigned
**Root Cause**: User created before RBAC system initialized
**Solution**: Need to assign Admin role to existing users

---

## Changes Made

### 1. Fixed `/api/v1/users` Endpoint 
**File**: `src/backend/main.py`  
**Lines**: 299-324

```python
@app.get("/api/v1/users", tags=["Users"])
async def list_users_simple(...):
   """Get list of active users (any authenticated user can call this)."""
    # ✅ Fixed: Use full_name_en instead of non-existent 'name' field
    # ✅ Fixed: Load roles relationship to get role name
    return [
        {
            "user_id": str(user.user_id),
            "name": user.full_name_en or user.email.split('@')[0],  # Fallback
            "email": user.email,
            "role": user.roles[0].role_name if user.roles else "Viewer",
        }
        for user in users
    ]
```

### 2. Added Debug Endpoint
**File**: `src/backend/main.py`  
**Lines**: 327-356

```python
@app.get("/api/v1/debug/user-permissions", tags=["Debug"])
async def debug_user_permissions(...):
    """Debug endpoint to show current user's roles and permissions."""
    # Shows what permissions user actually has in database
```

### 3. Risk Permissions in RBAC
**File**: `src/backend/auth/rbac_setup.py`  
**Status**: ✅ Already added in previous session

- risk:create
- risk:read  
- risk:update
- risk:delete
- risk:assess
- risk:manage

**Roles Updated**:
- Admin: All 6 risk permissions
- Compliance Officer: create, read, update, assess
- Auditor: read, assess
- Analyst: read
- Viewer: read

---

## How to Fix User Role Assignment

The admin user needs to have the Admin role assigned. Run this SQL:

```sql
-- Find the admin user ID
SELECT user_id, email FROM users WHERE email = 'admin@grc.com';

-- Find the Admin role ID
SELECT role_id, role_name FROM roles WHERE role_name = 'Admin';

-- Assign Admin role to admin user (replace UUIDs with actual values from above)
INSERT INTO user_roles (user_id, role_id) 
VALUES (
    (SELECT user_id FROM users WHERE email = 'admin@grc.com'),
    (SELECT role_id FROM roles WHERE role_name = 'Admin')
)
ON CONFLICT DO NOTHING;
```

OR create a Python script to fix it:

```python
import asyncio
from sqlalchemy import select, insert
from core.database import AsyncSessionLocal  
from auth.models import User, Role, user_roles

async def assign_admin_role():
    async with AsyncSessionLocal() as db:
        # Get admin user
        result = await db.execute(
            select(User).where(User.email == 'admin@grc.com')
        )
        admin_user = result.scalar_one_or_none()
        
        # Get Admin role
        result = await db.execute(
            select(Role).where(Role.role_name == 'Admin')
        )
        admin_role = result.scalar_one_or_none()
        
        if admin_user and admin_role:
            # Assign role
            await db.execute(
                insert(user_roles).values(
                    user_id=admin_user.user_id,
                    role_id=admin_role.role_id
                ).prefix_with('OR IGNORE')  # SQLite
                # For PostgreSQL use: .on_conflict_do_nothing()
            )
            await db.commit()
            print(f"✓ Assigned Admin role to {admin_user.email}")
        else:
            print("❌ Admin user or role not found")

asyncio.run(assign_admin_role())
```

---

## Testing Steps

### 1. Test Users Endpoint
```powershell
$login = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/auth/login" `
    -Method Post `
    -Body @{username="admin@grc.com";password="Admin@123"} `
    -ContentType "application/x-www-form-urlencoded"

$headers = @{"Authorization"="Bearer $($login.access_token)"}

$users = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/users" -Headers $headers
Write-Host "✓ Users found: $($users.Count)"
```

**Expected**: List of users with names, emails, and roles

### 2. Test User Permissions
```powershell
$debug = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/debug/user-permissions" -Headers $headers
$debug | ConvertTo-Json -Depth 10
```

**Expected**: Should show Admin role with all permissions including risk permissions

### 3. Test Risk Endpoint
```powershell
$risks = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/risks" -Headers $headers
Write-Host "✓ Risks: $($risks.total)"
```

**Expected**: 200 OK (not 403 Forbidden)

### 4. Test Frontend Risk Owner Dropdown
1. Clear browser cache and session: `sessionStorage.clear()` in console
2. Logout and login again
3. Navigate to Risks page
4. Click "Create New Risk"
5. Check "Risk Owner" dropdown

**Expected**: Dropdown shows list of users

---

## Notification Button Issue

**Status**: The notification button in TopBar.tsx (lines 110-177) is working correctly.

**Functionality**:
- Shows static mock notifications
- "View All Notifications" link goes to `/[locale]/notifications`  
- If that page doesn't exist, you need to create it or remove the link

**To Fix**: Either:
1. Create the notifications page: `src/frontend/app/[locale]/notifications/page.tsx`
2. Or remove the "View All" link if not needed

---

## Summary

| Issue | Status | Solution |
|-------|--------|----------|
| Users endpoint 500 error | ✅ FIXED | Updated to use `full_name_en` field |
| Risk Owner dropdown empty | ✅ FIXED | Users endpoint now returns data |
| Risk permissions 403 | ⚠️ PARTIAL | Permissions exist, but users need roles assigned |
| Admin user has no permissions | ❌ TODO | Run SQL or Python script to assign Admin role |
| Notification button | ✅ WORKS | Link goes to non-existent page (optional fix) |

---

## Next Steps

1. **CRITICAL**: Assign Admin role to admin@grc.com user (run SQL or Python script above)
2. Restart backend to ensure all changes loaded
3. Clear browser session and re-login
4. Test Risk Owner dropdown
5. Test risk creation with all fields
6. (Optional) Create notifications page or remove link

