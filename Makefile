# SICO GRC Platform Makefile

.PHONY: help install dev test clean docker-up docker-down security security-deps security-sast security-scan git-setup check-conflicts

help:
	@echo "SICO GRC Platform - Available Commands"
	@echo "======================================"
	@echo ""
	@echo "📦 Setup & Installation:"
	@echo "  install       - Install all dependencies"
	@echo ""
	@echo "🚀 Development:"
	@echo "  dev           - Start development environment"
	@echo "  docker-up     - Start Docker containers"
	@echo "  docker-down   - Stop Docker containers"
	@echo ""
	@echo "🧪 Testing & Quality:"
	@echo "  test          - Run all tests"
	@echo "  lint          - Run linters"
	@echo ""
	@echo "🔒 Security:"
	@echo "  security      - Run all security scans"
	@echo "  security-deps - Scan dependencies for vulnerabilities"
	@echo "  security-sast - Run static application security testing"
	@echo ""
	@echo "🔀 Git & Merge:"
	@echo "  git-setup     - Configure git for optimal merge handling"
	@echo "  check-conflicts - Check for potential merge conflicts with main"
	@echo ""
	@echo "🧹 Maintenance:"
	@echo "  clean         - Clean build artifacts"
	@echo ""
	@echo "📖 Documentation:"
	@echo "  Security: docs/SECURITY_PIPELINE.md"
	@echo "  Conflicts: docs/CONFLICT_RESOLUTION_GUIDE.md"

install:
	@echo "Installing backend dependencies..."
	cd src/backend && pip install -r requirements.txt
	@echo "Installing frontend dependencies..."
	cd src/frontend && npm install
	@echo "Installing AI dependencies..."
	cd ai && pip install -r requirements.txt

dev:
	@echo "Starting development environment..."
	docker-compose -f deployment/docker-compose.yml up -d

test:
	@echo "Running backend tests..."
	cd src/backend && pytest tests/
	@echo "Running frontend tests..."
	cd src/frontend && npm test

lint:
	@echo "Linting backend..."
	cd src/backend && black . && flake8
	@echo "Linting frontend..."
	cd src/frontend && npm run lint

docker-up:
	docker-compose -f deployment/docker-compose.yml up -d

docker-down:
	docker-compose -f deployment/docker-compose.yml down

clean:
	@echo "Cleaning build artifacts..."
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf src/frontend/.next
	rm -rf src/frontend/node_modules

security: security-deps security-sast
	@echo "✅ All security scans completed"

security-deps:
	@echo "Running dependency vulnerability scans..."
	@echo "Checking Python dependencies..."
	cd src/backend && pip install safety 2>/dev/null || true
	cd src/backend && safety check --json || true
	@echo "Checking Node.js dependencies..."
	cd src/frontend && npm audit --json || true

security-sast:
	@echo "Running SAST (Static Application Security Testing)..."
	@echo "Installing Bandit for Python SAST..."
	pip install bandit 2>/dev/null || true
	@echo "Scanning backend for security issues..."
	bandit -r src/backend -f json -o bandit-report.json || true
	@echo "Report saved to bandit-report.json"

security-scan: security
	@echo "Security scan complete. Check reports for details."

git-setup:
	@echo "Configuring git for optimal merge handling..."
	@bash scripts/setup_git_config.sh

check-conflicts:
	@echo "Checking for potential merge conflicts with main..."
	@bash scripts/check_conflicts.sh main -v
