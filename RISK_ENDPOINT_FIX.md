# Risk Endpoint 403 Forbidden - COMPLETE FIX

## Problem Analysis

The `/api/v1/risks` endpoint was returning **403 Forbidden** because:

1. ✗ **Missing Permissions**: Risk management permissions (`risk:read`, `risk:create`, etc.) were not defined in the RBAC system
2. ✗ **No Role Assignments**: No user roles had risk permissions assigned
3. ✗ **Poor Error Logging**: Permission denied errors didn't show which permissions the user needed

## Fixes Applied

### 1. Added Risk Permissions to RBAC System
**File**: `src/backend/auth/rbac_setup.py`

Added 6 new risk permissions:
- `risk:create` - Create new risks
- `risk:read` - View risks
- `risk:update` - Update risks  
- `risk:delete` - Delete risks
- `risk:assess` - Conduct risk assessments
- `risk:manage` - Manage third-party vendor risks

### 2. Assigned Permissions to Roles

| Role | Permissions |
|------|-------------|
| **Admin** | ALL risk permissions (create, read, update, delete, assess, manage) |
| **Compliance Officer** | create, read, update, assess |
| **Auditor** | read, assess |
| **Analyst** | read |
| **Viewer** | read |

### 3. Enhanced Permission Denied Logging
**File**: `src/backend/auth/security.py`

Added detailed logging that shows:
- User ID and email who was denied
- Required permission (`resource:action`)
- All permissions the user currently has
- Helps debug permission issues quickly

Example log output:
```
WARNING - Permission denied for user 123e4567-e89b-12d3-a456-426614174000 (admin@grc.com): 
Required 'risk:read', User has: controls:read, controls:create, evidence:read
```

### 4. Backend Restarted
The backend has been restarted to apply the new RBAC configuration.

## Testing Instructions

### Step 1: Verify Backend is Running
```powershell
(Invoke-WebRequest -Uri http://localhost:8000/health -UseBasicParsing).Content
```
Expected: `{"status":"healthy"}`

### Step 2: Clear Browser Cache and Re-Login

1. **Open Browser DevTools** (F12)
2. **Go to Application tab → Storage → Session Storage**
3. **Delete `access_token`** or clear all storage
4. **Refresh the page** (Ctrl + F5)
5. **Log in again** with your credentials

### Step 3: Test Risk Register Page

1. Navigate to **Risk Register** page
2. **Open Console** (F12 → Console tab)
3. Check for these successful API calls:
   ```
   ✓ GET /api/v1/risks?skip=0&limit=20 → 200 OK
   ✓ GET /api/v1/config/workflows?entity_type=risk → 200 OK
   ✓ GET /api/v1/config/custom-fields?entity_type=risk → 200 OK
   ✓ GET /api/v1/users?limit=100 → 200 OK
   ```

### Step 4: Verify Data Loads

- You should see the risks table
- "Create Risk" button should work  
- Users dropdown should populate

## If Still Getting 403 Error

### Check Backend Logs

Look for permission denied messages:
```
grep "Permission denied" backend_logs.txt
```

### Verify Your User Role

1. Check what role your user has
2. Verify the role has `risk:read` permission
3. Admin users should have ALL permissions

### Manual Permission Check

Run this SQL to check if permissions exist:
```sql
SELECT r.role_name, p.permission_name
FROM roles r
JOIN role_permissions rp ON r.id = rp.role_id
JOIN permissions p ON rp.permission_id = p.id
WHERE p.resource = 'risk'
ORDER BY r.role_name;
```

Expected output should show risk permissions for all roles.

## Frontend API Client Configuration

The frontend `apiClient` (in `lib/api-client.ts`) automatically:
- ✓ Attaches `Authorization: Bearer <token>` to ALL requests
- ✓ Refreshes token on 401 errors
- ✓ Redirects to login on auth failure

No frontend changes were needed - the auth token is already being sent correctly.

## Expected Outcome

After following the testing instructions:

✅ `/api/v1/risks` returns **200 OK**  
✅ Authenticated users can fetch risks successfully  
✅ Authorization header is consistently applied  
✅ Risk Register page loads without errors  
✅ Users can create new risks  

## Troubleshooting

### Error: "Permission denied: risk:read required"

**Cause**: Your user doesn't have the risk:read permission  
**Solution**: 
1. Log out and log back in (get fresh token with new permissions)
2. Contact admin to assign you a role with risk permissions  
3. Check if RBAC was re-initialized (backend logs should show "RBAC system initialized")

### Error: Still showing cached 403 errors

**Cause**: Browser cached the failed requests  
**Solution**:
1. Hard refresh: Ctrl + Shift + R (Chrome) or Ctrl + F5
2. Clear browser cache completely
3. Open in incognito/private browser tab

### Error: Empty risks list but 200 OK

**Cause**: No risks in database yet (this is normal)  
**Solution**: Click "Create Risk" to add your first risk

## Summary

All fixes have been applied:
1. ✅ Risk permissions created in RBAC system
2. ✅ Permissions assigned to all user roles  
3. ✅ Enhanced error logging for debugging
4. ✅ Backend restarted with new configuration
5. ✅ Frontend API client already sends auth tokens correctly

**The /api/v1/risks endpoint should now return 200 OK for authenticated users.**

If you still experience issues after re-logging in, check the backend logs for detailed permission information.
