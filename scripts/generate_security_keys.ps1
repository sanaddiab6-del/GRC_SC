# Quick Start: Generate secure keys and create your .env file

Write-Host "`n================================================================" -ForegroundColor Cyan
Write-Host "      SICO GRC - Security Configuration Generator" -ForegroundColor Cyan
Write-Host "================================================================`n" -ForegroundColor Cyan

# Generate SECRET_KEY (for JWT tokens)
$secretKey = -join ((48..57) + (65..90) + (97..122) + @(45,95) | Get-Random -Count 48 | ForEach-Object {[char]$_})

Write-Host "[OK] Generated SECRET_KEY (JWT token signing)" -ForegroundColor Green

# Generate ENCRYPTION_KEY (Fernet key for PII encryption)
try {
    $encryptionKey = python -c "from cryptography.fernet import Fernet; key = Fernet.generate_key(); print(key.decode())"
    Write-Host "[OK] Generated ENCRYPTION_KEY (PII field encryption)" -ForegroundColor Green
} catch {
    Write-Host "[WARN] Installing cryptography package..." -ForegroundColor Yellow
    python -m pip install cryptography --quiet
    $encryptionKey = python -c "from cryptography.fernet import Fernet; key = Fernet.generate_key(); print(key.decode())"
    Write-Host "[OK] Generated ENCRYPTION_KEY (PII field encryption)" -ForegroundColor Green
}

# Create .env file content
$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
$envContent = @"
# SICO GRC Platform - Environment Configuration
# Auto-generated: $timestamp
# WARNING: Never commit this file to version control!

APP_NAME=SICO GRC Platform
DEBUG=False
LOG_LEVEL=INFO

# Database
DATABASE_URL=sqlite+aiosqlite:///./sico_grc.db
DATABASE_URL_SYNC=sqlite:///./sico_grc.db

# Security - NCA ECC-IS-3 & PDPL Compliant
SECRET_KEY=$secretKey
ENCRYPTION_KEY=$encryptionKey
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Rate Limiting
RATE_LIMIT_ENABLED=True
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_PER_HOUR=1000

# TLS/HTTPS
TLS_ENABLED=True

# Audit Logging
AUDIT_LOG_RETENTION_YEARS=7
AUDIT_LOG_STORAGE_PATH=./logs/audit

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:3001

# Redis
REDIS_URL=redis://localhost:6379/0
CACHE_TTL=3600

# AI/RAG
EMBEDDING_MODEL=intfloat/multilingual-e5-large
LLM_MODEL=gpt-4
RAG_CHUNK_SIZE=512

# Vector DB
VECTOR_DB_TYPE=chroma
VECTOR_DB_HOST=localhost
VECTOR_DB_PORT=8001

# Regulatory APIs
SUPPORTED_FRAMEWORKS=ECC,CCC,PDPL
DEFAULT_LANGUAGE=ar
"@

# Write .env file
$envPath = "src\backend\.env"
$envContent | Out-File -FilePath $envPath -Encoding UTF8 -NoNewline

Write-Host "`n================================================================" -ForegroundColor Green
Write-Host "                  SECURITY KEYS GENERATED" -ForegroundColor Green
Write-Host "================================================================" -ForegroundColor Green

Write-Host "`nSECRET_KEY (JWT):" -ForegroundColor Yellow
Write-Host $secretKey -ForegroundColor White

Write-Host "`nENCRYPTION_KEY (PII):" -ForegroundColor Yellow
Write-Host $encryptionKey -ForegroundColor White

Write-Host "`n----------------------------------------------------------------" -ForegroundColor Red
Write-Host "IMPORTANT SECURITY NOTES:" -ForegroundColor Red
Write-Host "----------------------------------------------------------------" -ForegroundColor Yellow
Write-Host "1. Never commit .env file to Git" -ForegroundColor White
Write-Host "2. Store keys in Azure Key Vault for production" -ForegroundColor White
Write-Host "3. Rotate keys every 90 days (NCA requirement)" -ForegroundColor White
Write-Host "4. Enable TLS/HTTPS in production" -ForegroundColor White
Write-Host "5. Use PostgreSQL instead of SQLite for production" -ForegroundColor White
Write-Host "----------------------------------------------------------------`n" -ForegroundColor Yellow

Write-Host "[OK] Configuration file created: $envPath" -ForegroundColor Green
Write-Host "[OK] Ready to start backend: python -m uvicorn main:app --reload`n" -ForegroundColor Green
