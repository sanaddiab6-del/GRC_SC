# ==============================================================================
# SICO GRC Platform - Production Launch Script
# Saudi Regulatory Compliance Platform (ECC, CCC, PDPL)
# ==============================================================================

Write-Host "🛡️  SICO GRC PLATFORM - LAUNCH SEQUENCE" -ForegroundColor Cyan
Write-Host "=======================================" -ForegroundColor Cyan
Write-Host ""

# Configuration
$ProjectRoot = "c:\Users\Shahd\Downloads\SICO_GRC_PRODUCTION_V1\sanadcom"
$BackendPath = "$ProjectRoot\src\backend"
$FrontendPath = "$ProjectRoot\src\frontend"
$VenvPython = "C:/Users/Shahd/Downloads/SICO_GRC_PRODUCTION_V1/.venv/Scripts/python.exe"

# Check Database
Write-Host "📊 Checking database..." -ForegroundColor Yellow
if (Test-Path "$BackendPath\sico_dev.db") {
    $conn = New-Object System.Data.SQLite.SQLiteConnection
    $conn.ConnectionString = "Data Source=$BackendPath\sico_dev.db"
    try {
        $conn.Open()
        $cmd = $conn.CreateCommand()
        $cmd.CommandText = "SELECT COUNT(*) FROM controls"
        $controlCount = $cmd.ExecuteScalar()
        $conn.Close()
        Write-Host "✅ Database ready: $controlCount controls loaded" -ForegroundColor Green
    } catch {
        Write-Host "⚠️  Database exists but may need initialization" -ForegroundColor Yellow
    }
} else {
    Write-Host "❌ Database not found! Run setup first." -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "🚀 Starting Backend API..." -ForegroundColor Cyan
$backendCmd = "cd '$BackendPath'; `$env:PYTHONPATH = '$BackendPath'; & '$VenvPython' -m uvicorn main:app --reload --host 0.0.0.0 --port 8000"
Start-Process powershell -ArgumentList "-NoExit", "-Command", $backendCmd

Write-Host "⏳ Waiting for backend to initialize..." -ForegroundColor Yellow
Start-Sleep -Seconds 8 

Write-Host ""
Write-Host "🎨 Starting Frontend UI..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$FrontendPath'; npm run dev"

Write-Host ""
Write-Host "════════════════════════════════════════" -ForegroundColor Green
Write-Host "✅ SICO GRC PLATFORM LAUNCHED!" -ForegroundColor Green
Write-Host "════════════════════════════════════════" -ForegroundColor Green
Write-Host ""
Write-Host "📍 Access Points:" -ForegroundColor White
Write-Host "   Frontend (Arabic): http://localhost:3000/ar/dashboard" -ForegroundColor Cyan
Write-Host "   Frontend (English): http://localhost:3000/en/dashboard" -ForegroundColor Cyan
Write-Host "   API Health: http://localhost:8000/api/v1/health" -ForegroundColor Cyan
Write-Host "   API Docs: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "🔐 Demo Credentials:" -ForegroundColor White
Write-Host "   Email: admin@sico.sa" -ForegroundColor Yellow
Write-Host "   Password: Password123!" -ForegroundColor Yellow
Write-Host ""
Write-Host "📊 Loaded Frameworks:" -ForegroundColor White
Write-Host "   ✓ NCA ECC - Essential Cybersecurity Controls" -ForegroundColor Green
Write-Host "   ✓ NCA CCC - Cloud Cybersecurity Controls" -ForegroundColor Green
Write-Host "   ✓ PDPL - Personal Data Protection Law" -ForegroundColor Green
Write-Host ""
Write-Host "Press Ctrl+C to stop all services" -ForegroundColor Gray
