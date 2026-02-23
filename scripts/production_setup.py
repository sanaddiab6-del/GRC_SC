#!/usr/bin/env python3
"""
SICO GRC Platform - Production Setup Script
Generates secure production configuration and validates environment

COMPLIANCE: NCA ECC, NCA CCC, PDPL, SDAIA AI
"""

import secrets
import sys
import os
from pathlib import Path
from cryptography.fernet import Fernet
import subprocess


def generate_secret_key(length: int = 64) -> str:
    """Generate cryptographically secure SECRET_KEY"""
    return secrets.token_hex(length)


def generate_encryption_key() -> str:
    """Generate Fernet encryption key for PII (PDPL Article 29)"""
    return Fernet.generate_key().decode()


def generate_database_password(length: int = 32) -> str:
    """Generate secure database password"""
    alphabet = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*'
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def create_production_env():
    """Create production .env file with secure values"""
    
    print("🔐 SICO GRC Platform - Production Configuration Generator")
    print("=" * 70)
    print()
    
    # Generate secure values
    print("Generating secure keys...")
    secret_key = generate_secret_key()
    encryption_key = generate_encryption_key()
    db_password = generate_database_password()
    
    print("✅ SECRET_KEY generated (64 bytes)")
    print("✅ ENCRYPTION_KEY generated (Fernet AES-256)")
    print("✅ Database password generated (32 chars)")
    print()
    
    # Get production configuration
    print("Production Configuration:")
    print("-" * 70)
    
    domain = input("Enter production domain (e.g., grc.example.com): ").strip()
    if not domain:
        print("❌ Domain is required")
        sys.exit(1)
    
    db_host = input("Enter PostgreSQL host (default: localhost): ").strip() or "localhost"
    db_name = input("Enter database name (default: sico_grc): ").strip() or "sico_grc"
    db_user = input("Enter database user (default: sico_admin): ").strip() or "sico_admin"
    
    use_azure_kv = input("Use Azure Key Vault? (y/n): ").strip().lower() == 'y'
    
    azure_kv_url = ""
    azure_client_id = ""
    azure_tenant_id = ""
    
    if use_azure_kv:
        azure_kv_url = input("Azure Key Vault URL: ").strip()
        azure_client_id = input("Azure Client ID: ").strip()
        azure_tenant_id = input("Azure Tenant ID: ").strip()
    
    # Create production .env
    env_content = f"""# ============================================================================
# SICO GRC Platform - PRODUCTION Configuration
# ============================================================================
# Generated: {subprocess.check_output(['date']).decode().strip()}
# Domain: {domain}
# 
# ⚠️  CRITICAL SECURITY NOTICE:
# - This file contains production secrets
# - NEVER commit this file to version control
# - Store securely in production environment
# - Rotate keys every 90 days (compliance requirement)
# ============================================================================

# Application Configuration
APP_NAME=SICO GRC Platform
DEBUG=False
ENVIRONMENT=production

# API Configuration
API_V1_PREFIX=/api/v1
CORS_ORIGINS=https://{domain}

# Database (PostgreSQL with TLS)
DATABASE_URL=postgresql://{db_user}:{db_password}@{db_host}:5432/{db_name}?sslmode=require
DATABASE_ECHO=False
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=40

# Vector Database (Chroma)
VECTOR_DB_TYPE=chroma
VECTOR_DB_HOST=chroma
VECTOR_DB_PORT=8000

# Redis (with TLS)
REDIS_URL=rediss://{db_host}:6379/0?ssl_cert_reqs=required
CACHE_TTL=3600

# AI/RAG Configuration
EMBEDDING_MODEL=intfloat/multilingual-e5-large
LLM_MODEL=gpt-4
RAG_CHUNK_SIZE=512
RAG_CHUNK_OVERLAP=128

# Security - NCA ECC-IS-3, PDPL Article 29
# ⚠️ CRITICAL: These keys are cryptographically secure
# Rotate every 90 days per compliance requirements
SECRET_KEY={secret_key}
ENCRYPTION_KEY={encryption_key}

# JWT Configuration (NCA ECC-IS-3)
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Azure Key Vault (Production Secrets Management)
AZURE_KEY_VAULT_URL={azure_kv_url}
AZURE_CLIENT_ID={azure_client_id}
AZURE_TENANT_ID={azure_tenant_id}

# Rate Limiting (Brute Force Prevention - NCA ECC-IS-3)
RATE_LIMIT_ENABLED=True
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_PER_HOUR=1000

# TLS/HTTPS (MANDATORY - NCA CCC-SEC-03)
TLS_ENABLED=True
TLS_CERT_PATH=/etc/ssl/certs/sico-grc.crt
TLS_KEY_PATH=/etc/ssl/private/sico-grc.key

# Audit Logging (7-year retention - NCA ECC-IS-5)
AUDIT_LOG_RETENTION_YEARS=7
AUDIT_LOG_STORAGE_PATH=/var/log/sico/audit

# Logging
LOG_LEVEL=INFO

# Backup Configuration
BACKUP_ENABLED=True
BACKUP_SCHEDULE=0 2 * * *  # Daily at 2 AM
BACKUP_RETENTION_DAYS=90
BACKUP_STORAGE_PATH=/var/backups/sico

# Monitoring
MONITORING_ENABLED=True
METRICS_PORT=9090
HEALTH_CHECK_INTERVAL=30

# External APIs
PDPL_API_URL=https://api.dga.gov.sa/pdpl
SAMA_API_URL=https://www.sama.gov.sa
CITC_API_URL=https://www.citc.gov.sa
"""
    
    # Write to file
    env_path = Path(".env.production")
    env_path.write_text(env_content)
    
    print()
    print("=" * 70)
    print("✅ Production configuration created: .env.production")
    print()
    print("📋 Next Steps:")
    print("1. Review .env.production file")
    print("2. Store secrets in Azure Key Vault (if enabled)")
    print("3. Copy to production server: scp .env.production user@server:/app/.env")
    print("4. Set permissions: chmod 600 /app/.env")
    print("5. Generate TLS certificates (see docs/PRODUCTION_DEPLOYMENT.md)")
    print()
    print("🔐 Database Credentials:")
    print(f"   User: {db_user}")
    print(f"   Password: {db_password}")
    print(f"   Database: {db_name}")
    print()
    print("⚠️  IMPORTANT: Store these credentials securely!")
    print()
    
    # Create credentials file
    creds_content = f"""SICO GRC Platform - Production Credentials
Generated: {subprocess.check_output(['date']).decode().strip()}

Database:
  Host: {db_host}
  User: {db_user}
  Password: {db_password}
  Database: {db_name}

SECRET_KEY: {secret_key}
ENCRYPTION_KEY: {encryption_key}

⚠️  Store this file in a secure password manager and delete from disk!
"""
    
    creds_path = Path(".credentials.txt")
    creds_path.write_text(creds_content)
    print(f"📄 Credentials saved to: {creds_path}")
    print("   Store in password manager and delete this file!")
    print()


def validate_production_config():
    """Validate production configuration"""
    print("🔍 Validating Production Configuration...")
    print("=" * 70)
    
    env_file = Path(".env")
    if not env_file.exists():
        print("❌ .env file not found")
        return False
    
    env_content = env_file.read_text()
    
    # Check critical settings
    checks = [
        ("SECRET_KEY", "at least 32 characters", lambda v: len(v) >= 32),
        ("ENCRYPTION_KEY", "not empty", lambda v: len(v) > 0),
        ("TLS_ENABLED", "set to True", lambda v: v.lower() == "true"),
        ("DATABASE_URL", "contains password", lambda v: "@" in v and ":" in v),
        ("AUDIT_LOG_RETENTION_YEARS", "set to 7", lambda v: v == "7"),
    ]
    
    all_passed = True
    for key, description, validator in checks:
        value = None
        for line in env_content.split('\n'):
            if line.startswith(f"{key}="):
                value = line.split('=', 1)[1].strip()
                break
        
        if value is None:
            print(f"❌ {key}: Not found")
            all_passed = False
        elif not validator(value):
            print(f"❌ {key}: {description} (current: {value[:20]}...)")
            all_passed = False
        else:
            print(f"✅ {key}: Valid")
    
    print()
    if all_passed:
        print("✅ All production configuration checks passed!")
    else:
        print("❌ Production configuration has issues. Fix before deploying.")
    
    return all_passed


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="SICO GRC Production Setup")
    parser.add_argument("--generate", action="store_true", help="Generate production configuration")
    parser.add_argument("--validate", action="store_true", help="Validate existing configuration")
    
    args = parser.parse_args()
    
    if args.generate:
        create_production_env()
    elif args.validate:
        validate_production_config()
    else:
        print("Usage:")
        print("  Generate production config: python scripts/production_setup.py --generate")
        print("  Validate configuration:     python scripts/production_setup.py --validate")
        sys.exit(1)
