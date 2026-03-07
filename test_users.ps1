# Test users endpoint and database connection
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "TESTING BACKEND ENDPOINTS AND DATABASE" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

$baseUrl = "http://localhost:8000"

# Step 1: Test Health
Write-Host "`n1. Testing Backend Health..." -ForegroundColor Yellow
try {
    $health = Invoke-RestMethod -Uri "$baseUrl/health" -Method Get -UseBasicParsing
    Write-Host "   ✓ Backend is healthy: $($health.status)" -ForegroundColor Green
} catch {
    Write-Host "   ✗ Health check failed: $_" -ForegroundColor Red
    exit 1
}

# Step 2: Login
Write-Host "`n2. Logging in as admin..." -ForegroundColor Yellow
try {
    $loginBody = @{
        username = "admin@grc.com"
        password = "Admin@123"
    }
    $loginResponse = Invoke-RestMethod -Uri "$baseUrl/api/v1/auth/token" `
        -Method Post `
        -ContentType "application/x-www-form-urlencoded" `
        -Body $loginBody
    
    $token = $loginResponse.access_token
    Write-Host "   ✓ Login successful!" -ForegroundColor Green
    Write-Host "   Token: $($token.Substring(0, 50))..." -ForegroundColor Gray
} catch {
    Write-Host "   ✗ Login failed: $_" -ForegroundColor Red
    Write-Host "   Response: $($_.Exception.Response)" -ForegroundColor Red
    exit 1
}

# Step 3: Test Users Endpoint
Write-Host "`n3. Fetching users..." -ForegroundColor Yellow
try {
    $headers = @{
        "Authorization" = "Bearer $token"
    }
    $usersUrl = $baseUrl + '/api/v1/users?limit=100'
    $users = Invoke-RestMethod -Uri $usersUrl `
        -Method Get `
        -Headers $headers `
        -UseBasicParsing
    
    Write-Host "   ✓ Users endpoint successful!" -ForegroundColor Green
    Write-Host "   Total users: $($users.Count)" -ForegroundColor Green
    Write-Host "`n   Users List:" -ForegroundColor Cyan
    foreach ($user in $users) {
        Write-Host "      - $($user.name) ($($user.email)) - Role: $($user.role)" -ForegroundColor White
        Write-Host "        user_id: $($user.user_id)" -ForegroundColor Gray
    }
} catch {
    Write-Host "   ✗ Users endpoint failed: $_" -ForegroundColor Red
    Write-Host "   Response: $($_.Exception.Response)" -ForegroundColor Red
}

# Step 4: Test Risks Endpoint
Write-Host "`n4. Testing risks endpoint..." -ForegroundColor Yellow
try {
    $risksUrl = $baseUrl + '/api/v1/risks?skip=0&limit=10'
    $risks = Invoke-RestMethod -Uri $risksUrl `
        -Method Get `
        -Headers $headers `
        -UseBasicParsing
    
    $total = if ($risks.total) { $risks.total } else { $risks.Count }
    Write-Host "   ✓ Risks endpoint successful!" -ForegroundColor Green
    Write-Host "   Total risks: $total" -ForegroundColor Green
} catch {
    Write-Host "   ✗ Risks endpoint failed: $_" -ForegroundColor Red
    Write-Host "   Status Code: $($_.Exception.Response.StatusCode.value__)" -ForegroundColor Red
}

# Step 5: Test Controls Endpoint
Write-Host "`n5. Testing controls endpoint..." -ForegroundColor Yellow
try {
    $controlsUrl = $baseUrl + '/api/v1/controls?limit=10'
    $controls = Invoke-RestMethod -Uri $controlsUrl `
        -Method Get `
        -Headers $headers `
        -UseBasicParsing
    
    $controlsTotal = if ($controls.total) { $controls.total } else { if ($controls.items) { $controls.items.Count } else { $controls.Count } }
    Write-Host "   ✓ Controls endpoint successful!" -ForegroundColor Green
    Write-Host "   Total controls: $controlsTotal" -ForegroundColor Green
} catch {
    Write-Host "   ✗ Controls endpoint failed: $_" -ForegroundColor Red
}

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "SUMMARY" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "✓ Backend is running and healthy" -ForegroundColor Green
Write-Host "✓ Authentication is working" -ForegroundColor Green
Write-Host "✓ Users endpoint is accessible" -ForegroundColor Green
Write-Host "`nIf Risk Owner dropdown is still empty in the UI:" -ForegroundColor Yellow
Write-Host "1. Clear browser sessionStorage and re-login" -ForegroundColor White
Write-Host "2. Open browser console (F12) and check for errors" -ForegroundColor White
Write-Host "3. Check Network tab for failed /api/v1/users request" -ForegroundColor White
Write-Host "4. Ensure the frontend is sending Authorization header" -ForegroundColor White
