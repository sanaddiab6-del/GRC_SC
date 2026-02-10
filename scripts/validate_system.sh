#!/bin/bash
# ============================================================================
# SICO GRC Platform - System Validation Script
# ============================================================================
# Post-clone verification script that validates:
# - System prerequisites (Python, Node.js, Docker)
# - Configuration files and environment variables
# - Required dependencies
# - Directory structure
# - Service connectivity
#
# Usage: ./scripts/validate_system.sh
# ============================================================================

# Don't use set -e as it conflicts with arithmetic expressions
# set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Counters for summary
PASSED=0
FAILED=0
WARNINGS=0

# Helper functions
print_header() {
    echo -e "\n${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}\n"
}

print_section() {
    echo -e "\n${BLUE}▶ $1${NC}"
}

check_pass() {
    echo -e "${GREEN}✓${NC} $1"
    ((PASSED++))
}

check_fail() {
    echo -e "${RED}✗${NC} $1"
    ((FAILED++))
}

check_warn() {
    echo -e "${YELLOW}⚠${NC} $1"
    ((WARNINGS++))
}

print_info() {
    echo -e "  ${BLUE}ℹ${NC} $1"
}

# ============================================================================
# 1. SYSTEM PREREQUISITES
# ============================================================================
check_prerequisites() {
    print_header "1. System Prerequisites"
    
    # Check Python
    print_section "Python"
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
        PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
        PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)
        
        if [ "$PYTHON_MAJOR" -ge 3 ] && [ "$PYTHON_MINOR" -ge 11 ]; then
            check_pass "Python $PYTHON_VERSION (requirement: 3.11+)"
        else
            check_fail "Python $PYTHON_VERSION found, but 3.11+ required"
            print_info "Install Python 3.11+ from https://www.python.org/"
        fi
    else
        check_fail "Python 3 not found"
        print_info "Install Python 3.11+ from https://www.python.org/"
    fi
    
    # Check pip
    if command -v pip3 &> /dev/null; then
        PIP_VERSION=$(pip3 --version 2>&1 | awk '{print $2}')
        check_pass "pip $PIP_VERSION"
    else
        check_fail "pip3 not found"
        print_info "Install pip: python3 -m ensurepip"
    fi
    
    # Check Node.js
    print_section "Node.js"
    if command -v node &> /dev/null; then
        NODE_VERSION=$(node --version 2>&1 | sed 's/v//')
        NODE_MAJOR=$(echo $NODE_VERSION | cut -d. -f1)
        
        if [ "$NODE_MAJOR" -ge 18 ]; then
            check_pass "Node.js $NODE_VERSION (requirement: 18+)"
        else
            check_fail "Node.js $NODE_VERSION found, but 18+ required"
            print_info "Install Node.js 18+ from https://nodejs.org/"
        fi
    else
        check_fail "Node.js not found"
        print_info "Install Node.js 18+ from https://nodejs.org/"
    fi
    
    # Check npm
    if command -v npm &> /dev/null; then
        NPM_VERSION=$(npm --version 2>&1)
        check_pass "npm $NPM_VERSION"
    else
        check_fail "npm not found (comes with Node.js)"
    fi
    
    # Check Docker
    print_section "Docker"
    if command -v docker &> /dev/null; then
        DOCKER_VERSION=$(docker --version 2>&1 | awk '{print $3}' | sed 's/,//')
        check_pass "Docker $DOCKER_VERSION"
        
        # Check if Docker daemon is running
        if docker info &> /dev/null; then
            check_pass "Docker daemon is running"
        else
            check_fail "Docker daemon is not running"
            print_info "Start Docker Desktop or Docker service"
        fi
    else
        check_fail "Docker not found"
        print_info "Install Docker from https://www.docker.com/"
    fi
    
    # Check Docker Compose
    if command -v docker-compose &> /dev/null; then
        COMPOSE_VERSION=$(docker-compose --version 2>&1 | awk '{print $4}' | sed 's/,//')
        check_pass "Docker Compose $COMPOSE_VERSION"
    elif docker compose version &> /dev/null 2>&1; then
        COMPOSE_VERSION=$(docker compose version 2>&1 | awk '{print $4}')
        check_pass "Docker Compose $COMPOSE_VERSION (plugin)"
    else
        check_fail "Docker Compose not found"
        print_info "Install Docker Compose or use Docker Desktop"
    fi
    
    # Check git
    print_section "Git"
    if command -v git &> /dev/null; then
        GIT_VERSION=$(git --version 2>&1 | awk '{print $3}')
        check_pass "Git $GIT_VERSION"
    else
        check_fail "Git not found"
    fi
}

# ============================================================================
# 2. DIRECTORY STRUCTURE
# ============================================================================
check_directory_structure() {
    print_header "2. Directory Structure"
    
    # Core directories
    REQUIRED_DIRS=(
        "src/backend"
        "src/frontend"
        "ai"
        "data"
        "scripts"
        "deployment"
        "docs"
        "config"
        "tests"
    )
    
    for dir in "${REQUIRED_DIRS[@]}"; do
        if [ -d "$dir" ]; then
            check_pass "Directory exists: $dir"
        else
            check_fail "Missing directory: $dir"
        fi
    done
    
    # Data subdirectories
    print_section "Data Directories"
    DATA_DIRS=(
        "data/controls"
        "data/mappings"
        "data/evidence"
    )
    
    for dir in "${DATA_DIRS[@]}"; do
        if [ -d "$dir" ]; then
            check_pass "Directory exists: $dir"
        else
            check_warn "Optional directory missing: $dir"
        fi
    done
}

# ============================================================================
# 3. CONFIGURATION FILES
# ============================================================================
check_configuration() {
    print_header "3. Configuration Files"
    
    # Check for .env file
    print_section "Environment Configuration"
    if [ -f ".env" ]; then
        check_pass ".env file exists"
        
        # Load .env file for validation
        source .env 2>/dev/null || true
        
        # Validate SECRET_KEY
        if [ -n "$SECRET_KEY" ]; then
            KEY_LENGTH=${#SECRET_KEY}
            if [ $KEY_LENGTH -ge 32 ]; then
                check_pass "SECRET_KEY is set (length: $KEY_LENGTH chars)"
            else
                check_fail "SECRET_KEY is too short (length: $KEY_LENGTH, required: 32+)"
                print_info "Generate with: python -c \"import secrets; print(secrets.token_hex(32))\""
            fi
        else
            check_fail "SECRET_KEY is not set"
        fi
        
        # Validate ENCRYPTION_KEY
        if [ -n "$ENCRYPTION_KEY" ]; then
            check_pass "ENCRYPTION_KEY is set"
        else
            check_warn "ENCRYPTION_KEY is not set (required for PII encryption)"
            print_info "Generate with: python -c \"from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())\""
        fi
        
        # Validate DATABASE_URL
        if [ -n "$DATABASE_URL" ]; then
            check_pass "DATABASE_URL is set"
        else
            check_warn "DATABASE_URL is not set"
        fi
        
        # Validate REDIS_URL
        if [ -n "$REDIS_URL" ]; then
            check_pass "REDIS_URL is set"
        else
            check_warn "REDIS_URL is not set"
        fi
        
        # Check TLS configuration
        if [ "$TLS_ENABLED" = "True" ] || [ "$TLS_ENABLED" = "true" ]; then
            check_pass "TLS is enabled (production ready)"
        else
            check_warn "TLS is disabled (not production ready)"
            print_info "Set TLS_ENABLED=True for production deployment"
        fi
        
    else
        check_fail ".env file not found"
        print_info "Copy config/env.example to .env and configure"
    fi
    
    # Check config/env.example
    if [ -f "config/env.example" ]; then
        check_pass "config/env.example template exists"
    else
        check_warn "config/env.example template not found"
    fi
    
    # Check docker-compose.yml
    print_section "Deployment Configuration"
    if [ -f "deployment/docker-compose.yml" ]; then
        check_pass "deployment/docker-compose.yml exists"
    else
        check_fail "deployment/docker-compose.yml not found"
    fi
}

# ============================================================================
# 4. DEPENDENCIES
# ============================================================================
check_dependencies() {
    print_header "4. Dependencies"
    
    # Backend dependencies
    print_section "Backend Python Dependencies"
    if [ -f "src/backend/requirements.txt" ]; then
        check_pass "src/backend/requirements.txt exists"
        
        # Check if virtual environment is recommended
        if [ ! -d "src/backend/venv" ] && [ ! -d "venv" ]; then
            check_warn "No virtual environment detected"
            print_info "Create with: python -m venv venv"
        else
            check_pass "Virtual environment directory exists"
        fi
        
        # Count required packages
        BACKEND_PACKAGES=$(grep -v "^#" src/backend/requirements.txt | grep -v "^$" | wc -l)
        print_info "Backend requires $BACKEND_PACKAGES packages"
        
    else
        check_fail "src/backend/requirements.txt not found"
    fi
    
    # Frontend dependencies
    print_section "Frontend Node.js Dependencies"
    if [ -f "src/frontend/package.json" ]; then
        check_pass "src/frontend/package.json exists"
        
        # Check if node_modules exists
        if [ -d "src/frontend/node_modules" ]; then
            check_pass "node_modules directory exists"
        else
            check_warn "node_modules not installed"
            print_info "Install with: cd src/frontend && npm install"
        fi
        
    else
        check_fail "src/frontend/package.json not found"
    fi
    
    # AI dependencies
    print_section "AI/RAG Dependencies"
    if [ -f "ai/requirements.txt" ]; then
        check_pass "ai/requirements.txt exists"
        
        # Count AI packages
        AI_PACKAGES=$(grep -v "^#" ai/requirements.txt | grep -v "^$" | wc -l)
        print_info "AI engine requires $AI_PACKAGES packages"
        
    else
        check_warn "ai/requirements.txt not found"
    fi
}

# ============================================================================
# 5. SERVICE CONNECTIVITY
# ============================================================================
check_services() {
    print_header "5. Service Connectivity"
    
    print_section "Database Services"
    
    # Check PostgreSQL
    if command -v psql &> /dev/null || command -v docker &> /dev/null; then
        # Try to connect via Docker first
        if docker ps 2>/dev/null | grep -q postgres; then
            check_pass "PostgreSQL container is running"
        else
            check_warn "PostgreSQL container not running"
            print_info "Start with: docker-compose -f deployment/docker-compose.yml up -d postgres"
        fi
    else
        check_warn "Cannot verify PostgreSQL (psql not installed)"
    fi
    
    # Check Redis
    if command -v redis-cli &> /dev/null || command -v docker &> /dev/null; then
        # Try to check via Docker
        if docker ps 2>/dev/null | grep -q redis; then
            check_pass "Redis container is running"
        else
            check_warn "Redis container not running"
            print_info "Start with: docker-compose -f deployment/docker-compose.yml up -d redis"
        fi
    else
        check_warn "Cannot verify Redis (redis-cli not installed)"
    fi
    
    # Check Chroma
    print_section "Vector Database"
    if docker ps 2>/dev/null | grep -q chroma; then
        check_pass "Chroma container is running"
    else
        check_warn "Chroma container not running"
        print_info "Start with: docker-compose -f deployment/docker-compose.yml up -d chroma"
    fi
}

# ============================================================================
# 6. ADDITIONAL CHECKS
# ============================================================================
check_additional() {
    print_header "6. Additional Checks"
    
    # Check Makefile
    print_section "Build Tools"
    if [ -f "Makefile" ]; then
        check_pass "Makefile exists"
    else
        check_warn "Makefile not found"
    fi
    
    # Check key scripts
    print_section "Setup Scripts"
    SCRIPTS=(
        "scripts/dev_setup.sh"
        "scripts/load_sample_data.py"
    )
    
    for script in "${SCRIPTS[@]}"; do
        if [ -f "$script" ]; then
            check_pass "Script exists: $script"
        else
            check_warn "Script not found: $script"
        fi
    done
    
    # Check documentation
    print_section "Documentation"
    DOCS=(
        "README.md"
        "QUICK_START.md"
    )
    
    for doc in "${DOCS[@]}"; do
        if [ -f "$doc" ]; then
            check_pass "Documentation exists: $doc"
        else
            check_warn "Documentation not found: $doc"
        fi
    done
}

# ============================================================================
# MAIN EXECUTION
# ============================================================================
main() {
    # Clear screen if in interactive terminal
    if [ -t 1 ]; then
        clear
    fi
    print_header "🛡️  SICO GRC Platform - System Validation"
    echo "Validating post-clone system setup..."
    echo "Repository: sonaiso/sanadcom"
    
    # Run all checks
    check_prerequisites
    check_directory_structure
    check_configuration
    check_dependencies
    check_services
    check_additional
    
    # Print summary
    print_header "Validation Summary"
    echo -e "${GREEN}✓ Passed:${NC}   $PASSED"
    echo -e "${RED}✗ Failed:${NC}   $FAILED"
    echo -e "${YELLOW}⚠ Warnings:${NC} $WARNINGS"
    echo ""
    
    # Determine overall status
    if [ $FAILED -eq 0 ]; then
        if [ $WARNINGS -eq 0 ]; then
            echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
            echo -e "${GREEN}✓ System validation PASSED${NC}"
            echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
            echo ""
            echo "✅ Your system is ready for development!"
            echo ""
            echo "Next steps:"
            echo "  1. Install dependencies: make install"
            echo "  2. Start services: make docker-up"
            echo "  3. Load sample data: python scripts/load_sample_data.py"
            echo "  4. Start development: make dev"
            echo ""
        else
            echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
            echo -e "${YELLOW}⚠ System validation PASSED with warnings${NC}"
            echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
            echo ""
            echo "Your system is ready, but please review the warnings above."
            echo ""
        fi
        exit 0
    else
        echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo -e "${RED}✗ System validation FAILED${NC}"
        echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo ""
        echo "❌ Please fix the errors above before proceeding."
        echo ""
        echo "For help, see:"
        echo "  - README.md"
        echo "  - QUICK_START.md"
        echo "  - https://github.com/sonaiso/sanadcom/issues"
        echo ""
        exit 1
    fi
}

# Run main function
main
