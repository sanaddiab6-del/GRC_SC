# Sanadcom GRC Platform - Makefile
# Production-ready automation for security tasks

.PHONY: help install test security-scan generate-certs setup-vault run-dev run-prod clean

# Colors for output
RED=\033[0;31m
GREEN=\033[0;32m
YELLOW=\033[1;33m
NC=\033[0m # No Color

help:
	@echo "$(GREEN)Sanadcom GRC Platform - Available Commands$(NC)"
	@echo ""
	@echo "$(YELLOW)Setup Commands:$(NC)"
	@echo "  make install          - Install all dependencies"
	@echo "  make generate-certs   - Generate SSL/TLS certificates for development"
	@echo "  make setup-vault      - Setup Azure Key Vault secrets"
	@echo ""
	@echo "$(YELLOW)Testing Commands:$(NC)"
	@echo "  make test             - Run all tests"
	@echo "  make test-security    - Run security tests only"
	@echo "  make test-jwt         - Run JWT authentication tests"
	@echo "  make test-coverage    - Run tests with coverage report"
	@echo ""
	@echo "$(YELLOW)Security Commands:$(NC)"
	@echo "  make security-scan    - Run all security scans"
	@echo "  make bandit           - Run Bandit SAST scanner"
	@echo "  make safety           - Run Safety dependency scanner"
	@echo "  make gitleaks         - Run Gitleaks secrets scanner"
	@echo ""
	@echo "$(YELLOW)Quality Commands:$(NC)"
	@echo "  make lint             - Run code linting (Ruff)"
	@echo "  make format           - Format code (Black + isort)"
	@echo "  make typecheck        - Run type checking (MyPy)"
	@echo ""
	@echo "$(YELLOW)Run Commands:$(NC)"
	@echo "  make run-dev          - Run development server (HTTP)"
	@echo "  make run-prod         - Run production server (HTTPS)"
	@echo "  make docker-up        - Start Docker containers"
	@echo "  make docker-down      - Stop Docker containers"
	@echo ""
	@echo "$(YELLOW)Cleanup Commands:$(NC)"
	@echo "  make clean            - Clean temporary files"
	@echo "  make clean-all        - Clean everything including venv"

# ============================================================================
# Setup Commands
# ============================================================================

install:
	@echo "$(GREEN)Installing dependencies...$(NC)"
	pip install -r src/backend/requirements.txt
	pip install -r ai/requirements.txt
	@echo "$(GREEN)✓ Dependencies installed$(NC)"

generate-certs:
	@echo "$(GREEN)Generating SSL/TLS certificates...$(NC)"
	mkdir -p certs
	openssl req -x509 -newkey rsa:4096 -nodes \
		-keyout certs/key.pem \
		-out certs/cert.pem \
		-days 365 \
		-subj "/C=SA/ST=Riyadh/L=Riyadh/O=Sanadcom/CN=localhost"
	@echo "$(GREEN)✓ Certificates generated in certs/$(NC)"

setup-vault:
	@echo "$(GREEN)Setting up Azure Key Vault secrets...$(NC)"
	@echo "$(YELLOW)Creating Key Vault (if not exists)...$(NC)"
	az keyvault create \
		--name $(VAULT_NAME) \
		--resource-group $(RESOURCE_GROUP) \
		--location saudicentral
	@echo "$(YELLOW)Adding secrets...$(NC)"
	az keyvault secret set --vault-name $(VAULT_NAME) --name JWT-SECRET-KEY --value "$(JWT_SECRET)"
	az keyvault secret set --vault-name $(VAULT_NAME) --name DATABASE-URL --value "$(DB_URL)"
	az keyvault secret set --vault-name $(VAULT_NAME) --name DATABASE-PASSWORD --value "$(DB_PASSWORD)"
	az keyvault secret set --vault-name $(VAULT_NAME) --name REDIS-URL --value "$(REDIS_URL)"
	az keyvault secret set --vault-name $(VAULT_NAME) --name AZURE-TENANT-ID --value "$(AZURE_TENANT_ID)"
	az keyvault secret set --vault-name $(VAULT_NAME) --name AZURE-CLIENT-ID --value "$(AZURE_CLIENT_ID)"
	az keyvault secret set --vault-name $(VAULT_NAME) --name AZURE-CLIENT-SECRET --value "$(AZURE_CLIENT_SECRET)"
	az keyvault secret set --vault-name $(VAULT_NAME) --name DATA-ENCRYPTION-KEY --value "$(ENCRYPTION_KEY)"
	@echo "$(GREEN)✓ Secrets added to Key Vault$(NC)"

# ============================================================================
# Testing Commands
# ============================================================================

test:
	@echo "$(GREEN)Running all tests...$(NC)"
	pytest tests/ -v --tb=short

test-security:
	@echo "$(GREEN)Running security tests...$(NC)"
	pytest tests/security/ -v --tb=short

test-jwt:
	@echo "$(GREEN)Running JWT authentication tests...$(NC)"
	pytest tests/security/test_jwt_auth.py -v

test-secrets:
	@echo "$(GREEN)Running secrets management tests...$(NC)"
	pytest tests/security/test_secrets.py -v

test-coverage:
	@echo "$(GREEN)Running tests with coverage...$(NC)"
	pytest tests/ --cov=src/backend --cov=ai --cov-report=html --cov-report=term
	@echo "$(GREEN)✓ Coverage report generated in htmlcov/$(NC)"

# ============================================================================
# Security Scanning
# ============================================================================

security-scan: bandit safety gitleaks
	@echo "$(GREEN)✓ All security scans complete$(NC)"

bandit:
	@echo "$(GREEN)Running Bandit SAST...$(NC)"
	bandit -r src/backend/ ai/ -ll -f json -o bandit-report.json || true
	bandit -r src/backend/ ai/ -ll
	@echo "$(GREEN)✓ Bandit scan complete$(NC)"

safety:
	@echo "$(GREEN)Running Safety dependency scan...$(NC)"
	safety check --json --output safety-report.json || true
	safety check
	@echo "$(GREEN)✓ Safety scan complete$(NC)"

gitleaks:
	@echo "$(GREEN)Running Gitleaks secrets scan...$(NC)"
	docker run --rm -v $(PWD):/path zricethezav/gitleaks:latest detect --source /path -v
	@echo "$(GREEN)✓ Gitleaks scan complete$(NC)"

# ============================================================================
# Code Quality
# ============================================================================

lint:
	@echo "$(GREEN)Running Ruff linter...$(NC)"
	ruff check src/backend/ ai/ tests/
	@echo "$(GREEN)✓ Linting complete$(NC)"

format:
	@echo "$(GREEN)Formatting code...$(NC)"
	black src/backend/ ai/ tests/
	isort src/backend/ ai/ tests/
	@echo "$(GREEN)✓ Code formatted$(NC)"

typecheck:
	@echo "$(GREEN)Running MyPy type checker...$(NC)"
	mypy src/backend/ ai/
	@echo "$(GREEN)✓ Type checking complete$(NC)"

# ============================================================================
# Run Commands
# ============================================================================

run-dev:
	@echo "$(GREEN)Starting development server (HTTP)...$(NC)"
	cd src/backend && python main.py

run-prod:
	@echo "$(GREEN)Starting production server (HTTPS)...$(NC)"
	@if [ ! -f certs/key.pem ]; then \
		echo "$(RED)Error: SSL certificates not found. Run 'make generate-certs' first.$(NC)"; \
		exit 1; \
	fi
	cd src/backend && python main.py

docker-up:
	@echo "$(GREEN)Starting Docker containers...$(NC)"
	docker-compose -f deployment/docker-compose.yml up -d
	@echo "$(GREEN)✓ Containers started$(NC)"

docker-down:
	@echo "$(GREEN)Stopping Docker containers...$(NC)"
	docker-compose -f deployment/docker-compose.yml down
	@echo "$(GREEN)✓ Containers stopped$(NC)"

docker-logs:
	@echo "$(GREEN)Viewing Docker logs...$(NC)"
	docker-compose -f deployment/docker-compose.yml logs -f

# ============================================================================
# Database Commands
# ============================================================================

db-migrate:
	@echo "$(GREEN)Running database migrations...$(NC)"
	cd src/backend && alembic upgrade head
	@echo "$(GREEN)✓ Migrations complete$(NC)"

db-rollback:
	@echo "$(GREEN)Rolling back last migration...$(NC)"
	cd src/backend && alembic downgrade -1
	@echo "$(GREEN)✓ Rollback complete$(NC)"

db-reset:
	@echo "$(YELLOW)WARNING: This will delete all data!$(NC)"
	@read -p "Are you sure? (yes/no): " confirm && [ "$$confirm" = "yes" ]
	cd src/backend && alembic downgrade base
	cd src/backend && alembic upgrade head
	@echo "$(GREEN)✓ Database reset$(NC)"

# ============================================================================
# Cleanup Commands
# ============================================================================

clean:
	@echo "$(GREEN)Cleaning temporary files...$(NC)"
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	rm -rf htmlcov/ .coverage
	rm -f bandit-report.json safety-report.json
	@echo "$(GREEN)✓ Cleanup complete$(NC)"

clean-all: clean
	@echo "$(YELLOW)Removing virtual environment...$(NC)"
	rm -rf venv/
	rm -rf certs/
	@echo "$(GREEN)✓ Full cleanup complete$(NC)"

# ============================================================================
# CI/CD Commands
# ============================================================================

ci-test:
	@echo "$(GREEN)Running CI test pipeline...$(NC)"
	pytest tests/ -v --tb=short --cov=src/backend --cov=ai --cov-report=xml

ci-security:
	@echo "$(GREEN)Running CI security pipeline...$(NC)"
	bandit -r src/backend/ ai/ -ll -f json -o bandit-report.json
	safety check --json --output safety-report.json
	@echo "$(GREEN)✓ CI security checks complete$(NC)"

ci-quality:
	@echo "$(GREEN)Running CI quality pipeline...$(NC)"
	ruff check src/backend/ ai/ tests/
	mypy src/backend/ ai/
	@echo "$(GREEN)✓ CI quality checks complete$(NC)"

# ============================================================================
# Documentation Commands
# ============================================================================

docs:
	@echo "$(GREEN)Building documentation...$(NC)"
	@echo "$(YELLOW)Documentation available in docs/$(NC)"
	@echo "  - AI Security: docs/ai/AI_SECURITY_ARCHITECTURE.md"
	@echo "  - Developer Guide: docs/ai/DEVELOPER_GUIDE.md"
	@echo "  - Executive Summary: docs/ai/EXECUTIVE_AUDIT_REPORT.md"

# ============================================================================
# Utility Commands
# ============================================================================

logs:
	@echo "$(GREEN)Viewing application logs...$(NC)"
	tail -f logs/ai_audit.jsonl

check-env:
	@echo "$(GREEN)Checking environment configuration...$(NC)"
	@echo "Python version: $$(python --version)"
	@echo "Pip version: $$(pip --version)"
	@echo "Azure CLI: $$(az --version | head -n1)"
	@echo "Docker: $$(docker --version)"
	@echo "$(GREEN)✓ Environment check complete$(NC)"

.DEFAULT_GOAL := help
