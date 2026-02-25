# ============================================================================
# SICO GRC Platform - Alembic Migration Runner (Windows PowerShell)
# Safely handles multiple heads and migration conflicts
# ============================================================================

param(
    [string]$Command = "upgrade",
    [switch]$CheckOnly = $false
)

$ErrorActionPreference = "Stop"

Write-Host "Database Migration Manager" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Navigate to backend directory
$BackendDir = Join-Path $PSScriptRoot "..\src\backend"
Push-Location $BackendDir

try {
    Write-Host "Working Directory: $BackendDir`n" -ForegroundColor Yellow

    # Step 1: Check Alembic installation
    Write-Host "Step 1: Verifying Alembic installation..." -ForegroundColor Green
    $alembicVersion = python -m alembic --version 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: Alembic is not installed!" -ForegroundColor Red
        Write-Host "   Run: python -m pip install alembic" -ForegroundColor Yellow
        exit 1
    }
    Write-Host "   Alembic Version: $alembicVersion`n" -ForegroundColor Gray

    # Step 2: Check for multiple heads
    Write-Host "Step 2: Checking for multiple head revisions..." -ForegroundColor Green
    $heads = python -m alembic heads 2>&1 | Where-Object { $_ -match "^\w+" }
    $headCount = ($heads | Measure-Object).Count
    
    if ($headCount -eq 0) {
        Write-Host "   No heads found - database may not be initialized" -ForegroundColor Yellow
        $headCount = 1  # Treat as single head to allow first migration
    }
    elseif ($headCount -gt 1) {
        Write-Host "   WARNING: Multiple heads detected ($headCount heads)" -ForegroundColor Yellow
        Write-Host "`n   Current heads:" -ForegroundColor Yellow
        python -m alembic heads -v
        
        Write-Host "`n   To merge heads manually:" -ForegroundColor Cyan
        Write-Host "      cd src\backend" -ForegroundColor Gray
        Write-Host "      python -m alembic merge -m 'merge heads' heads" -ForegroundColor Gray
        Write-Host "      python -m alembic upgrade head`n" -ForegroundColor Gray
        
        if (-not $CheckOnly) {
            Write-Host "   Attempting automatic merge..." -ForegroundColor Yellow
            python -m alembic merge -m "auto merge multiple heads" heads 2>&1
            if ($LASTEXITCODE -eq 0) {
                Write-Host "   Merge migration created successfully`n" -ForegroundColor Green
            }
            else {
                Write-Host "   Auto-merge failed. Please merge manually.`n" -ForegroundColor Red
                exit 1
            }
        }
        else {
            exit 1
        }
    }
    else {
        Write-Host "   Single head found (healthy state)`n" -ForegroundColor Green
    }

    if ($CheckOnly) {
        Write-Host "Migration check completed successfully`n" -ForegroundColor Green
        exit 0
    }

    # Step 3: Show migration history
    Write-Host "Step 3: Current migration status..." -ForegroundColor Green
    python -m alembic current
    Write-Host ""

    # Step 4: Run the migration
    if ($Command -eq "upgrade") {
        Write-Host "Step 4: Running database upgrade..." -ForegroundColor Green
        python -m alembic upgrade head
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "`nDatabase migrations completed successfully!" -ForegroundColor Green
        }
        else {
            Write-Host "`nMigration failed with exit code $LASTEXITCODE" -ForegroundColor Red
            exit $LASTEXITCODE
        }
    }
    elseif ($Command -eq "downgrade") {
        Write-Host "Step 4: Running database downgrade..." -ForegroundColor Green
        python -m alembic downgrade -1
    }
    elseif ($Command -eq "history") {
        Write-Host "Step 4: Showing migration history..." -ForegroundColor Green
        python -m alembic history
    }
    else {
        Write-Host "Unknown command: $Command" -ForegroundColor Red
        Write-Host "   Valid commands: upgrade, downgrade, history" -ForegroundColor Yellow
        exit 1
    }

    Write-Host "`nFinal migration status:" -ForegroundColor Cyan
    python -m alembic current -v

    Write-Host "`nAll operations completed successfully!`n" -ForegroundColor Green

}
catch {
    Write-Host "`nERROR: $_" -ForegroundColor Red
    exit 1
}
finally {
    Pop-Location
}
