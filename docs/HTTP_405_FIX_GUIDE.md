"""
HTTP 405 ERROR FIX GUIDE & IMPLEMENTATION
Fixes all Method Not Allowed errors in SICO GRC Platform
"""

# ============================================================================
# 405 ERROR ANALYSIS
# ============================================================================

"""
IDENTIFIED 405 ISSUES:
1. Enterprise Router: No POST/PUT/DELETE endpoints for CRUD operations
2. Controls Router: Possible missing endpoints  
3. Evidence Router: Possible missing endpoints
4. Risk Router: Possible missing endpoints
5. Missing OPTIONS preflight handlers for CORS

FIX STRATEGY:
- Add complete CRUD endpoints (POST, PUT, DELETE) for all resources
- Ensure all routes have proper HTTP method decorators
- Add OPTIONS handlers for CORS preflight requests
- Implement proper error handling and validation
- Add middleware to catch and handle 405 errors gracefully
"""

# ============================================================================
# COMPREHENSIVE ENDPOINT CHECKLIST
# ============================================================================

REQUIRED_ENDPOINTS = {
    # Organizations
    "/enterprise/organizations": ["GET", "POST"],
    "/enterprise/organizations/{org_id}": ["GET", "PUT", "DELETE"],
    
    # Users
    "/enterprise/users": ["GET", "POST"],
    "/enterprise/users/{user_id}": ["GET", "PUT", "DELETE"],
    "/enterprise/users/{user_id}/roles": ["GET", "POST"],
    
    # Assets
    "/enterprise/assets": ["GET", "POST"],
    "/enterprise/assets/{asset_id}": ["GET", "PUT", "DELETE"],
    
    # Controls
    "/api/v1/controls": ["GET", "POST"],
    "/api/v1/controls/{control_id}": ["GET", "PUT", "DELETE", "PATCH"],
    
    # Risks  
    "/enterprise/risks": ["GET", "POST"],
    "/enterprise/risks/{risk_id}": ["GET", "PUT", "DELETE"],
    
    # Audit Findings
    "/enterprise/audit-findings": ["GET", "POST"],
    "/enterprise/audit-findings/{finding_id}": ["GET", "PUT", "DELETE"],
    
    # Evidence
    "/api/v1/evidence": ["GET", "POST"],
    "/api/v1/evidence/{evidence_id}": ["GET", "PUT", "DELETE"],
    
    # PDPL
    "/enterprise/pdpl/ropa": ["GET", "POST"],
    "/enterprise/pdpl/ropa/{ropa_id}": ["GET", "PUT", "DELETE"],
    "/enterprise/pdpl/dsar": ["GET", "POST"],
    "/enterprise/pdpl/dsar/{request_id}": ["GET", "PUT", "DELETE"],
    "/enterprise/pdpl/breaches": ["GET", "POST"],
    "/enterprise/pdpl/breaches/{breach_id}": ["GET", "PUT", "DELETE"],
    
    # Vendors
    "/enterprise/vendors": ["GET", "POST"],
    "/enterprise/vendors/{vendor_id}": ["GET", "PUT", "DELETE"],
    
    # Workflows
    "/enterprise/workflows/cases": ["GET", "POST"],
    "/enterprise/workflows/cases/{case_id}": ["GET", "PUT", "DELETE"],
}

# ============================================================================
# IMPLEMENTATION REQUIREMENTS
# ============================================================================

IMPLEMENTATION_CHECKLIST = """
FOR EACH RESOURCE ENDPOINT:

1. GET /resource (List)
   - Required: ✓ Already implemented
   - Must support: filtering, pagination, sorting
   - Error handling: 400 for invalid filters, 500 for DB errors

2. GET /resource/{id} (Read Single)
   - Required: ✓ Already implemented
   - Must return 404 if not found
   - Error handling: 403 for unauthorized access

3. POST /resource (Create)
   - Required: ✗ MISSING - ADD THIS
   - Request schema with validation
   - Response: 201 Created with resource
   - Error handling: 400 for validation errors, 409 for conflicts

4. PUT /resource/{id} (Update Full)
   - Required: ✗ MISSING - ADD THIS
   - Request schema with validation
   - Response: 200 OK with updated resource
   - Error handling: 404 not found, 400 validation

5. PATCH /resource/{id} (Update Partial)
   - Optional but recommended for large resources
   - Only update provided fields
   - Response: 200 OK with updated resource

6. DELETE /resource/{id} (Delete)
   - Required: ✗ MISSING - ADD THIS
   - Response: 204 No Content
   - Error handling: 404 not found, 409 if resource has dependencies

7. OPTIONS /resource (CORS Preflight)
   - Required: Add middleware to handle automatically
   - Response: 200 with Allow header listing available methods

ERROR RESPONSES:
- 400: Bad Request (validation failed)
- 401: Unauthorized (not authenticated)
- 403: Forbidden (authenticated but not authorized)
- 404: Not Found
- 405: Method Not Allowed (WRONG HTTP METHOD)
- 409: Conflict (duplicate key, resource exists)
- 422: Unprocessable Entity (validation error)
- 500: Internal Server Error
"""

# ============================================================================
# MIDDLEWARE FOR 405 ERROR HANDLING
# ============================================================================

MIDDLEWARE_CODE = """
from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

class Handle405Middleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            
            # Intercept 405 errors and provide helpful message
            if response.status_code == 405:
                return JSONResponse(
                    status_code=405,
                    content={
                        "message_en": f"Method {request.method} not allowed for {request.url.path}",
                        "message_ar": f"الطريقة {request.method} غير مسموحة لـ {request.url.path}",
                        "allowed_methods": response.headers.get("allow", ""),
                        "hint": "Check the endpoint definition or use a different HTTP method"
                    }
                )
            
            return response
        except Exception as e:
            return JSONResponse(
                status_code=500,
                content={"error": str(e)}
            )

# In main.py, add before mounting routers:
app.add_middleware(Handle405Middleware)
"""

print(__doc__)
