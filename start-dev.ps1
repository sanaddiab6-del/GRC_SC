# SICO GRC Platform - Development Startup Script
# This script starts the backend and frontend servers for local development

Write-Host "🛡️ SICO GRC Platform - Starting Development Environment..." -ForegroundColor Cyan
Write-Host ""

# Set environment variables for development
$env:DATABASE_URL = "sqlite:///./sico_dev.db"
$env:SECRET_KEY = "dev-secret-key-change-in-production"
$env:RATE_LIMIT_ENABLED = "false"
$env:TLS_ENABLED = "false"
$env:LOG_LEVEL = "DEBUG"

Write-Host "✅ Environment configured for development" -ForegroundColor Green
Write-Host ""

# Check if backend dependencies are installed
Write-Host "📦 Checking backend dependencies..." -ForegroundColor Yellow
$backendPath = "src\backend"
if (-not (Test-Path "$backendPath\requirements.txt")) {
    Write-Host "❌ Backend directory not found!" -ForegroundColor Red
    exit 1
}

# Start Backend Server
Write-Host "🚀 Starting FastAPI Backend Server..." -ForegroundColor Cyan
Write-Host "   URL: http://localhost:8000" -ForegroundColor White
Write-Host "   API Docs: http://localhost:8000/docs" -ForegroundColor White
Write-Host ""

$backendCmd = "Set-Location '$PWD\$backendPath'; python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000"
Start-Process powershell -ArgumentList "-NoExit", "-Command", $backendCmd

Start-Sleep -Seconds 3

# Start Frontend Server
Write-Host "🎨 Starting Next.js Frontend Server..." -ForegroundColor Cyan
Write-Host "   URL: http://localhost:3000" -ForegroundColor White
Write-Host ""

$frontendPath = "src\frontend"
if (Test-Path "$frontendPath\package.json") {
    $frontendCmd = "Set-Location '$PWD\$frontendPath'; npm run dev"
    Start-Process powershell -ArgumentList "-NoExit", "-Command", $frontendCmd
}
else {
    Write-Host "⚠️  Frontend not found - skipping" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "✅ Development servers starting..." -ForegroundColor Green
Write-Host ""
Write-Host "📖 Access the application:" -ForegroundColor Cyan
Write-Host "   Frontend: http://localhost:3000" -ForegroundColor White
Write-Host "   Backend API: http://localhost:8000" -ForegroundColor White
Write-Host "   API Docs: http://localhost:8000/docs" -ForegroundColor White
Write-Host ""
Write-Host "Press Ctrl+C in each terminal window to stop the servers" -ForegroundColor Yellow
