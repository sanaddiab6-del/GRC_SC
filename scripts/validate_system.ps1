# ============================================================================
# SICO GRC Platform - System Validation Script (PowerShell)
# ============================================================================
# Post-clone verification script that validates:
# - System prerequisites (Python, Node.js, Docker)
# - Configuration files and environment variables
# - Required dependencies
# - Directory structure
# - Service connectivity
#
# Usage: .\scripts\validate_system.ps1
# ============================================================================

$ErrorActionPreference = "Continue"

# Counters for summary
$script:PASSED = 0
$script:FAILED = 0
$script:WARNINGS = 0

# Helper functions
function Print-Header {
    param([string]$Message)
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Blue
    Write-Host $Message -ForegroundColor Blue
    Write-Host "========================================" -ForegroundColor Blue
    Write-Host ""
}

function Print-Section {
    param([string]$Message)
    Write-Host ""
    Write-Host "▶ $Message" -ForegroundColor Blue
}

function Check-Pass {
    param([string]$Message)
    Write-Host "✓ $Message" -ForegroundColor Green
    $script:PASSED++
}

function Check-Fail {
    param([string]$Message)
    Write-Host "✗ $Message" -ForegroundColor Red
    $script:FAILED++
}

function Check-Warn {
    param([string]$Message)
    Write-Host "⚠ $Message" -ForegroundColor Yellow
    $script:WARNINGS++
}

function Print-Info {
    param([string]$Message)
    Write-Host "  ℹ $Message" -ForegroundColor Cyan
}

# ============================================================================
# 1. SYSTEM PREREQUISITES
# ============================================================================
function Check-Prerequisites {
    Print-Header "1. System Prerequisites"
    
    # Check Python
    Print-Section "Python"
    try {
        $pythonVersion = python --version 2>&1 | Select-String -Pattern "Python (\d+\.\d+\.\d+)" | ForEach-Object { $_.Matches.Groups[1].Value }
        if ($pythonVersion) {
            $versionParts = $pythonVersion.Split('.')
            $major = [int]$versionParts[0]
            $minor = [int]$versionParts[1]
            
            if ($major -ge 3 -and $minor -ge 11) {
                Check-Pass "Python $pythonVersion (requirement: 3.11+)"
            } else {
                Check-Fail "Python $pythonVersion found, but 3.11+ required"
                Print-Info "Install Python 3.11+ from https://www.python.org/"
            }
        } else {
            Check-Fail "Python not found"
            Print-Info "Install Python 3.11+ from https://www.python.org/"
        }
    } catch {
        Check-Fail "Python not found"
        Print-Info "Install Python 3.11+ from https://www.python.org/"
    }
    
    # Check pip
    try {
        $pipVersion = pip --version 2>&1 | Select-String -Pattern "pip (\d+\.\d+\.\d+)" | ForEach-Object { $_.Matches.Groups[1].Value }
        if ($pipVersion) {
            Check-Pass "pip $pipVersion"
        } else {
            Check-Fail "pip not found"
            Print-Info "Install pip: python -m ensurepip"
        }
    } catch {
        Check-Fail "pip not found"
        Print-Info "Install pip: python -m ensurepip"
    }
    
    # Check Node.js
    Print-Section "Node.js"
    try {
        $nodeVersion = node --version 2>&1
        if ($nodeVersion -match "v(\d+)\.") {
            $major = [int]$Matches[1]
            $version = $nodeVersion.TrimStart('v')
            
            if ($major -ge 18) {
                Check-Pass "Node.js $version (requirement: 18+)"
            } else {
                Check-Fail "Node.js $version found, but 18+ required"
                Print-Info "Install Node.js 18+ from https://nodejs.org/"
            }
        } else {
            Check-Fail "Node.js not found"
            Print-Info "Install Node.js 18+ from https://nodejs.org/"
        }
    } catch {
        Check-Fail "Node.js not found"
        Print-Info "Install Node.js 18+ from https://nodejs.org/"
    }
    
    # Check npm
    try {
        $npmVersion = npm --version 2>&1
        if ($npmVersion) {
            Check-Pass "npm $npmVersion"
        } else {
            Check-Fail "npm not found (comes with Node.js)"
        }
    } catch {
        Check-Fail "npm not found (comes with Node.js)"
    }
    
    # Check Docker
    Print-Section "Docker"
    try {
        $dockerVersion = docker --version 2>&1
        if ($dockerVersion -match "Docker version (\S+)") {
            $version = $Matches[1].TrimEnd(',')
            Check-Pass "Docker $version"
            
            # Check if Docker daemon is running
            try {
                docker info 2>&1 | Out-Null
                if ($LASTEXITCODE -eq 0) {
                    Check-Pass "Docker daemon is running"
                } else {
                    Check-Fail "Docker daemon is not running"
                    Print-Info "Start Docker Desktop"
                }
            } catch {
                Check-Fail "Docker daemon is not running"
                Print-Info "Start Docker Desktop"
            }
        } else {
            Check-Fail "Docker not found"
            Print-Info "Install Docker Desktop from https://www.docker.com/"
        }
    } catch {
        Check-Fail "Docker not found"
        Print-Info "Install Docker Desktop from https://www.docker.com/"
    }
    
    # Check Docker Compose
    try {
        $composeVersion = docker-compose --version 2>&1
        if ($composeVersion -match "Docker Compose version (\S+)") {
            $version = $Matches[1].TrimEnd(',')
            Check-Pass "Docker Compose $version"
        } elseif ((docker compose version 2>&1) -match "Docker Compose version (\S+)") {
            $version = $Matches[1]
            Check-Pass "Docker Compose $version (plugin)"
        } else {
            Check-Fail "Docker Compose not found"
            Print-Info "Install Docker Desktop (includes Compose)"
        }
    } catch {
        Check-Fail "Docker Compose not found"
        Print-Info "Install Docker Desktop (includes Compose)"
    }
    
    # Check git
    Print-Section "Git"
    try {
        $gitVersion = git --version 2>&1
        if ($gitVersion -match "git version (\S+)") {
            $version = $Matches[1]
            Check-Pass "Git $version"
        } else {
            Check-Fail "Git not found"
            Print-Info "Install Git from https://git-scm.com/"
        }
    } catch {
        Check-Fail "Git not found"
        Print-Info "Install Git from https://git-scm.com/"
    }
}

# ============================================================================
# 2. DIRECTORY STRUCTURE
# ============================================================================
function Check-DirectoryStructure {
    Print-Header "2. Directory Structure"
    
    # Core directories
    $requiredDirs = @(
        "src\backend",
        "src\frontend",
        "ai",
        "data",
        "scripts",
        "deployment",
        "docs",
        "config",
        "tests"
    )
    
    foreach ($dir in $requiredDirs) {
        if (Test-Path $dir) {
            Check-Pass "Directory exists: $dir"
        } else {
            Check-Fail "Missing directory: $dir"
        }
    }
    
    # Data subdirectories
    Print-Section "Data Directories"
    $dataDirs = @(
        "data\controls",
        "data\mappings",
        "data\evidence"
    )
    
    foreach ($dir in $dataDirs) {
        if (Test-Path $dir) {
            Check-Pass "Directory exists: $dir"
        } else {
            Check-Warn "Optional directory missing: $dir"
        }
    }
}

# ============================================================================
# 3. CONFIGURATION FILES
# ============================================================================
function Check-Configuration {
    Print-Header "3. Configuration Files"
    
    # Check for .env file
    Print-Section "Environment Configuration"
    if (Test-Path ".env") {
        Check-Pass ".env file exists"
        
        # Load .env file for validation
        $envContent = Get-Content .env -ErrorAction SilentlyContinue
        $envVars = @{}
        foreach ($line in $envContent) {
            if ($line -match "^([^#][^=]+)=(.*)$") {
                $envVars[$Matches[1].Trim()] = $Matches[2].Trim()
            }
        }
        
        # Validate SECRET_KEY
        if ($envVars.ContainsKey("SECRET_KEY") -and $envVars["SECRET_KEY"]) {
            $keyLength = $envVars["SECRET_KEY"].Length
            if ($keyLength -ge 32) {
                Check-Pass "SECRET_KEY is set (length: $keyLength chars)"
            } else {
                Check-Fail "SECRET_KEY is too short (length: $keyLength, required: 32+)"
                Print-Info 'Generate with: python -c "import secrets; print(secrets.token_hex(32))"'
            }
        } else {
            Check-Fail "SECRET_KEY is not set"
        }
        
        # Validate ENCRYPTION_KEY
        if ($envVars.ContainsKey("ENCRYPTION_KEY") -and $envVars["ENCRYPTION_KEY"]) {
            Check-Pass "ENCRYPTION_KEY is set"
        } else {
            Check-Warn "ENCRYPTION_KEY is not set (required for PII encryption)"
            Print-Info 'Generate with: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"'
        }
        
        # Validate DATABASE_URL
        if ($envVars.ContainsKey("DATABASE_URL") -and $envVars["DATABASE_URL"]) {
            Check-Pass "DATABASE_URL is set"
        } else {
            Check-Warn "DATABASE_URL is not set"
        }
        
        # Validate REDIS_URL
        if ($envVars.ContainsKey("REDIS_URL") -and $envVars["REDIS_URL"]) {
            Check-Pass "REDIS_URL is set"
        } else {
            Check-Warn "REDIS_URL is not set"
        }
        
        # Check TLS configuration
        if ($envVars.ContainsKey("TLS_ENABLED") -and ($envVars["TLS_ENABLED"] -eq "True" -or $envVars["TLS_ENABLED"] -eq "true")) {
            Check-Pass "TLS is enabled (production ready)"
        } else {
            Check-Warn "TLS is disabled (not production ready)"
            Print-Info "Set TLS_ENABLED=True for production deployment"
        }
        
    } else {
        Check-Fail ".env file not found"
        Print-Info "Copy config\env.example to .env and configure"
    }
    
    # Check config/env.example
    if (Test-Path "config\env.example") {
        Check-Pass "config\env.example template exists"
    } else {
        Check-Warn "config\env.example template not found"
    }
    
    # Check docker-compose.yml
    Print-Section "Deployment Configuration"
    if (Test-Path "deployment\docker-compose.yml") {
        Check-Pass "deployment\docker-compose.yml exists"
    } else {
        Check-Fail "deployment\docker-compose.yml not found"
    }
}

# ============================================================================
# 4. DEPENDENCIES
# ============================================================================
function Check-Dependencies {
    Print-Header "4. Dependencies"
    
    # Backend dependencies
    Print-Section "Backend Python Dependencies"
    if (Test-Path "src\backend\requirements.txt") {
        Check-Pass "src\backend\requirements.txt exists"
        
        # Check if virtual environment exists
        if (-not (Test-Path "src\backend\venv") -and -not (Test-Path "venv")) {
            Check-Warn "No virtual environment detected"
            Print-Info "Create with: python -m venv venv"
        } else {
            Check-Pass "Virtual environment directory exists"
        }
        
        # Count required packages
        try {
            $backendPackages = (Get-Content "src\backend\requirements.txt" -ErrorAction SilentlyContinue | 
                               Where-Object { $_ -match "==" }).Count
            if ($backendPackages -gt 0) {
                Print-Info "Backend requires $backendPackages packages"
            } else {
                Print-Info "Backend requirements.txt exists but package count unavailable"
            }
        } catch {
            Print-Info "Backend requirements.txt exists but cannot be read"
        }
        
    } else {
        Check-Fail "src\backend\requirements.txt not found"
    }
    
    # Frontend dependencies
    Print-Section "Frontend Node.js Dependencies"
    if (Test-Path "src\frontend\package.json") {
        Check-Pass "src\frontend\package.json exists"
        
        # Check if node_modules exists
        if (Test-Path "src\frontend\node_modules") {
            Check-Pass "node_modules directory exists"
        } else {
            Check-Warn "node_modules not installed"
            Print-Info "Install with: cd src\frontend; npm install"
        }
        
    } else {
        Check-Fail "src\frontend\package.json not found"
    }
    
    # AI dependencies
    Print-Section "AI/RAG Dependencies"
    if (Test-Path "ai\requirements.txt") {
        Check-Pass "ai\requirements.txt exists"
        
        # Count AI packages
        try {
            $aiPackages = (Get-Content "ai\requirements.txt" -ErrorAction SilentlyContinue | 
                          Where-Object { $_ -match "==" }).Count
            if ($aiPackages -gt 0) {
                Print-Info "AI engine requires $aiPackages packages"
            } else {
                Print-Info "AI requirements.txt exists but package count unavailable"
            }
        } catch {
            Print-Info "AI requirements.txt exists but cannot be read"
        }
        
    } else {
        Check-Warn "ai\requirements.txt not found"
    }
}

# ============================================================================
# 5. SERVICE CONNECTIVITY
# ============================================================================
function Check-Services {
    Print-Header "5. Service Connectivity"
    
    Print-Section "Database Services"
    
    # Check PostgreSQL
    try {
        $postgresContainer = docker ps 2>&1 | Select-String "postgres"
        if ($postgresContainer) {
            Check-Pass "PostgreSQL container is running"
        } else {
            Check-Warn "PostgreSQL container not running"
            Print-Info "Start with: docker-compose -f deployment\docker-compose.yml up -d postgres"
        }
    } catch {
        Check-Warn "Cannot verify PostgreSQL (Docker not running)"
    }
    
    # Check Redis
    try {
        $redisContainer = docker ps 2>&1 | Select-String "redis"
        if ($redisContainer) {
            Check-Pass "Redis container is running"
        } else {
            Check-Warn "Redis container not running"
            Print-Info "Start with: docker-compose -f deployment\docker-compose.yml up -d redis"
        }
    } catch {
        Check-Warn "Cannot verify Redis (Docker not running)"
    }
    
    # Check Chroma
    Print-Section "Vector Database"
    try {
        $chromaContainer = docker ps 2>&1 | Select-String "chroma"
        if ($chromaContainer) {
            Check-Pass "Chroma container is running"
        } else {
            Check-Warn "Chroma container not running"
            Print-Info "Start with: docker-compose -f deployment\docker-compose.yml up -d chroma"
        }
    } catch {
        Check-Warn "Cannot verify Chroma (Docker not running)"
    }
}

# ============================================================================
# 6. ADDITIONAL CHECKS
# ============================================================================
function Check-Additional {
    Print-Header "6. Additional Checks"
    
    # Check Makefile (not required on Windows)
    Print-Section "Build Tools"
    if (Test-Path "Makefile") {
        Check-Pass "Makefile exists"
    } else {
        Check-Warn "Makefile not found (optional on Windows)"
    }
    
    # Check key scripts
    Print-Section "Setup Scripts"
    $scripts = @(
        "scripts\dev_setup.sh",
        "scripts\load_sample_data.py"
    )
    
    foreach ($script in $scripts) {
        if (Test-Path $script) {
            Check-Pass "Script exists: $script"
        } else {
            Check-Warn "Script not found: $script"
        }
    }
    
    # Check documentation
    Print-Section "Documentation"
    $docs = @(
        "README.md",
        "QUICK_START.md"
    )
    
    foreach ($doc in $docs) {
        if (Test-Path $doc) {
            Check-Pass "Documentation exists: $doc"
        } else {
            Check-Warn "Documentation not found: $doc"
        }
    }
}

# ============================================================================
# MAIN EXECUTION
# ============================================================================
function Main {
    Clear-Host
    Print-Header "🛡️  SICO GRC Platform - System Validation"
    Write-Host "Validating post-clone system setup..."
    Write-Host "Repository: sonaiso/sanadcom"
    
    # Run all checks
    Check-Prerequisites
    Check-DirectoryStructure
    Check-Configuration
    Check-Dependencies
    Check-Services
    Check-Additional
    
    # Print summary
    Print-Header "Validation Summary"
    Write-Host "✓ Passed:   $script:PASSED" -ForegroundColor Green
    Write-Host "✗ Failed:   $script:FAILED" -ForegroundColor Red
    Write-Host "⚠ Warnings: $script:WARNINGS" -ForegroundColor Yellow
    Write-Host ""
    
    # Determine overall status
    if ($script:FAILED -eq 0) {
        if ($script:WARNINGS -eq 0) {
            Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Green
            Write-Host "✓ System validation PASSED" -ForegroundColor Green
            Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Green
            Write-Host ""
            Write-Host "✅ Your system is ready for development!"
            Write-Host ""
            Write-Host "Next steps:"
            Write-Host "  1. Install backend deps:  cd src\backend; pip install -r requirements.txt"
            Write-Host "  2. Install frontend deps: cd src\frontend; npm install"
            Write-Host "  3. Start services:        docker-compose -f deployment\docker-compose.yml up -d"
            Write-Host "  4. Load sample data:      python scripts\load_sample_data.py"
            Write-Host ""
        } else {
            Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Yellow
            Write-Host "⚠ System validation PASSED with warnings" -ForegroundColor Yellow
            Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Yellow
            Write-Host ""
            Write-Host "Your system is ready, but please review the warnings above."
            Write-Host ""
        }
        exit 0
    } else {
        Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Red
        Write-Host "✗ System validation FAILED" -ForegroundColor Red
        Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Red
        Write-Host ""
        Write-Host "❌ Please fix the errors above before proceeding."
        Write-Host ""
        Write-Host "For help, see:"
        Write-Host "  - README.md"
        Write-Host "  - QUICK_START.md"
        Write-Host "  - https://github.com/sonaiso/sanadcom/issues"
        Write-Host ""
        exit 1
    }
}

# Run main function
Main
