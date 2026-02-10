# System Validation Scripts

## Overview

The SICO GRC Platform includes comprehensive system validation scripts that verify all prerequisites, dependencies, and configurations before development setup. These scripts help identify issues early and provide clear guidance for resolving them.

## Available Scripts

### 1. Bash Script (Linux/macOS)
**Location:** `scripts/validate_system.sh`

**Usage:**
```bash
# Direct execution
./scripts/validate_system.sh

# Via Make
make validate
```

### 2. PowerShell Script (Windows)
**Location:** `scripts/validate_system.ps1`

**Usage:**
```powershell
# Direct execution
.\scripts\validate_system.ps1

# With execution policy (if needed)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\scripts\validate_system.ps1
```

## What Gets Validated

### 1. System Prerequisites
- ✅ **Python**: Version 3.11 or higher
- ✅ **pip**: Python package manager
- ✅ **Node.js**: Version 18 or higher  
- ✅ **npm**: Node package manager
- ✅ **Docker**: Docker Engine
- ✅ **Docker Compose**: Orchestration tool
- ✅ **Git**: Version control

### 2. Directory Structure
**Core Directories:**
- `src/backend` - FastAPI application
- `src/frontend` - Next.js application
- `ai` - AI/RAG engine
- `data` - Control libraries and mappings
- `scripts` - Utility scripts
- `deployment` - Docker and K8s configs
- `docs` - Documentation
- `config` - Configuration templates
- `tests` - Test suites

**Data Subdirectories:**
- `data/controls` - ECC/CCC/PDPL controls
- `data/mappings` - Framework mappings
- `data/evidence` - Evidence catalog

### 3. Configuration Files
- ✅ **.env file**: Environment configuration
- ✅ **SECRET_KEY**: Minimum 32 characters (security requirement)
- ✅ **ENCRYPTION_KEY**: PII encryption key (PDPL Article 29)
- ✅ **DATABASE_URL**: PostgreSQL connection string
- ✅ **REDIS_URL**: Redis connection string
- ✅ **TLS_ENABLED**: Production TLS configuration
- ✅ **config/env.example**: Configuration template
- ✅ **deployment/docker-compose.yml**: Container orchestration

### 4. Dependencies
**Backend (Python):**
- `src/backend/requirements.txt` - 39+ packages
- Virtual environment recommendation
- FastAPI, SQLAlchemy, cryptography, etc.

**Frontend (Node.js):**
- `src/frontend/package.json` - Package manifest
- `node_modules` installation check
- Next.js, React, TypeScript, etc.

**AI/RAG Engine:**
- `ai/requirements.txt` - 8+ packages
- LangChain, Chroma, transformers, etc.

### 5. Service Connectivity
**Database Services:**
- PostgreSQL container (port 5432)
- Redis container (port 6379)

**Vector Database:**
- Chroma container (port 8001)

### 6. Additional Checks
**Build Tools:**
- Makefile (Linux/macOS)

**Setup Scripts:**
- `scripts/dev_setup.sh`
- `scripts/load_sample_data.py`

**Documentation:**
- `README.md`
- `QUICK_START.md`

## Output Format

### Success Example
```
========================================
🛡️  SICO GRC Platform - System Validation
========================================

✓ Passed:   35
✗ Failed:   0
⚠ Warnings: 3

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✓ System validation PASSED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Your system is ready for development!

Next steps:
  1. Install dependencies: make install
  2. Start services: make docker-up
  3. Load sample data: python scripts/load_sample_data.py
  4. Start development: make dev
```

### Failure Example
```
========================================
Validation Summary
========================================

✓ Passed:   20
✗ Failed:   3
⚠ Warnings: 5

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✗ System validation FAILED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

❌ Please fix the errors above before proceeding.

For help, see:
  - README.md
  - QUICK_START.md
  - https://github.com/sonaiso/sanadcom/issues
```

## Color Coding

- 🟢 **Green (✓)**: Check passed
- 🔴 **Red (✗)**: Check failed (blocking issue)
- 🟡 **Yellow (⚠)**: Warning (non-blocking issue)
- 🔵 **Blue (ℹ)**: Information/guidance

## Common Issues and Solutions

### Issue: Python Version Too Old
**Error:** `Python 3.10 found, but 3.11+ required`

**Solution:**
```bash
# Linux/macOS
brew install python@3.11  # macOS
sudo apt-get install python3.11  # Ubuntu/Debian

# Windows
# Download from https://www.python.org/downloads/
```

### Issue: Docker Not Running
**Error:** `Docker daemon is not running`

**Solution:**
```bash
# Linux
sudo systemctl start docker

# macOS/Windows
# Start Docker Desktop application
```

### Issue: SECRET_KEY Too Short
**Error:** `SECRET_KEY is too short (length: 20, required: 32+)`

**Solution:**
```bash
# Generate a secure key
python -c "import secrets; print(secrets.token_hex(32))"

# Update .env file with the generated key
```

### Issue: Missing .env File
**Error:** `.env file not found`

**Solution:**
```bash
# Copy the template
cp config/env.example .env

# Edit and configure
nano .env  # or use your preferred editor
```

### Issue: Node.js Version Too Old
**Error:** `Node.js 16.x found, but 18+ required`

**Solution:**
```bash
# macOS
brew install node@18

# Linux (using nvm)
nvm install 18
nvm use 18

# Windows
# Download from https://nodejs.org/
```

### Issue: Services Not Running
**Warning:** `PostgreSQL container not running`

**Solution:**
```bash
# Start all services
docker-compose -f deployment/docker-compose.yml up -d

# Or start specific service
docker-compose -f deployment/docker-compose.yml up -d postgres
```

## Exit Codes

- **0**: All checks passed (may have warnings)
- **1**: One or more critical checks failed

## Integration with CI/CD

The validation script can be integrated into CI/CD pipelines:

```yaml
# GitHub Actions example
- name: Validate System
  run: |
    chmod +x scripts/validate_system.sh
    ./scripts/validate_system.sh
```

## When to Run

### Required:
1. **After cloning the repository** - First-time setup
2. **After system updates** - OS or dependency upgrades
3. **Before starting development** - Daily development workflow
4. **In CI/CD pipelines** - Automated validation

### Optional:
- **After long periods of inactivity** - Verify environment still works
- **When troubleshooting issues** - Diagnose setup problems
- **After dependency changes** - Verify new requirements

## Extending the Scripts

To add new validation checks:

1. Add a new function following the existing pattern
2. Call the function in the `main()` function
3. Use the helper functions for consistent output:
   - `check_pass()` - Green checkmark
   - `check_fail()` - Red X
   - `check_warn()` - Yellow warning
   - `print_info()` - Blue information

Example:
```bash
check_custom_requirement() {
    print_section "Custom Requirement"
    
    if command -v mycmd &> /dev/null; then
        check_pass "Custom command found"
    else
        check_fail "Custom command not found"
        print_info "Install with: apt-get install mycmd"
    fi
}
```

## Support

For issues or questions about the validation scripts:

1. Check the [QUICK_START.md](../QUICK_START.md) guide
2. Review the [README.md](../README.md) documentation
3. Search existing [GitHub Issues](https://github.com/sonaiso/sanadcom/issues)
4. Create a new issue with the validation output

## Related Documentation

- [QUICK_START.md](../QUICK_START.md) - Quick setup guide
- [README.md](../README.md) - Project overview
- [docs/architecture/](../docs/architecture/) - Architecture documentation
- [deployment/docker-compose.yml](../deployment/docker-compose.yml) - Service configuration
