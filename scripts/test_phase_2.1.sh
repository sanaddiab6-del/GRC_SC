#!/bin/bash
# Test Phase 2.1 Security Features

echo "========================================"
echo " SICO GRC - Phase 2.1 Security Testing"
echo "========================================"

# Check if backend is running
echo -e "\n[1/5] Checking backend status..."
curl -s http://localhost:8000/ | grep -q "SICO GRC" && echo "✓ Backend running" || echo "✗ Backend not running - Start with: python -m uvicorn main:app --reload"

# Register test user
echo -e "\n[2/5] Registering test user..."
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@sico.sa","username":"testuser","password":"Secure123!@#","full_name":"Test User"}' \
  2>/dev/null | grep -q "user_id" && echo "✓ User registered" || echo "✗ Registration failed"

# Login and get token
echo -e "\n[3/5] Testing login..."
TOKEN=$(curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=testuser&password=Secure123!@#" \
  2>/dev/null | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

if [ -n "$TOKEN" ]; then
  echo "✓ Login successful - Token: ${TOKEN:0:20}..."
else
  echo "✗ Login failed"
  exit 1
fi

# Test protected endpoint
echo -e "\n[4/5] Testing protected endpoint..."
curl -s http://localhost:8000/api/v1/enterprise/organizations \
  -H "Authorization: Bearer $TOKEN" | grep -q "name_en" && echo "✓ Protected endpoint accessible with auth" || echo "✗ Auth failed"

# Test unauthorized access
echo -e "\n[5/5] Testing unauthorized access..."
curl -s http://localhost:8000/api/v1/enterprise/organizations 2>&1 | grep -q "401" && echo "✓ Unauthorized access blocked" || echo "⚠ Endpoint may not require auth"

echo -e "\n========================================"
echo " Phase 2.1 Security Tests Complete"
echo "========================================"
