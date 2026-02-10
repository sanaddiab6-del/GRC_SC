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
	@echo "  security          - Run all security scans (deps + SAST + secrets + containers)"
	@echo "  security-deps     - Scan dependencies for vulnerabilities"
	@echo "  security-sast     - Run static application security testing"
	@echo "  security-secrets  - Detect hardcoded secrets (requires gitleaks)"
	@echo "  security-containers - Scan Docker containers (requires trivy)"
	@echo "  security-sbom     - Generate Software Bill of Materials"
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

security: security-deps security-sast security-secrets security-containers
	@echo "✅ All security scans completed"
	@echo ""
	@echo "📊 Security Summary:"
	@echo "  - Dependency vulnerabilities: Check safety-report.json + npm-audit.json"
	@echo "  - Code security issues: Check bandit-report.json"
	@echo "  - Secrets detected: Check gitleaks output"
	@echo "  - Container vulnerabilities: Check trivy-*.json"
	@echo ""
	@echo "📖 See docs/SECURITY_PIPELINE.md for details"

security-deps:
	@echo "Running dependency vulnerability scans..."
	@echo "Checking Python dependencies..."
	cd src/backend && pip install safety 2>/dev/null || true
	cd src/backend && safety check --json > ../../safety-report.json || true
	cd src/backend && safety check || true
	@echo "Checking Node.js dependencies..."
	cd src/frontend && npm audit --json > ../../npm-audit.json || true
	cd src/frontend && npm audit || true

security-sast:
	@echo "Running SAST (Static Application Security Testing)..."
	@echo "Installing Bandit for Python SAST..."
	pip install bandit 2>/dev/null || true
	@echo "Scanning backend for security issues..."
	bandit -r src/backend -f json -o bandit-report.json || true
	bandit -r src/backend || true
	@echo "Report saved to bandit-report.json"

security-secrets:
	@echo "Running secret detection scan..."
	@which gitleaks > /dev/null || (echo "⚠️  Gitleaks not installed. Install from: https://github.com/gitleaks/gitleaks" && exit 1)
	gitleaks detect --source . --verbose --report-path gitleaks-report.json || true

security-containers:
	@echo "Running container security scans..."
	@which trivy > /dev/null || (echo "⚠️  Trivy not installed. Install from: https://aquasecurity.github.io/trivy/" && exit 1)
	@echo "Building backend container..."
	docker build -t sico-grc-backend:local -f deployment/Dockerfile.backend . || true
	@echo "Scanning backend container..."
	trivy image --format json --output trivy-backend.json sico-grc-backend:local || true
	trivy image sico-grc-backend:local || true
	@echo "Building frontend container..."
	docker build -t sico-grc-frontend:local -f deployment/Dockerfile.frontend . || true
	@echo "Scanning frontend container..."
	trivy image --format json --output trivy-frontend.json sico-grc-frontend:local || true
	trivy image sico-grc-frontend:local || true

security-sbom:
	@echo "Generating Software Bill of Materials (SBOM)..."
	@echo "Installing CycloneDX tools..."
	pip install cyclonedx-bom 2>/dev/null || true
	npm install -g @cyclonedx/cyclonedx-npm 2>/dev/null || true
	@echo "Generating Python SBOM..."
	cd src/backend && cyclonedx-py requirements -i requirements.txt -o ../../sbom-python.json --output-format json || true
	@echo "Generating Node.js SBOM..."
	cd src/frontend && cyclonedx-npm --output-file ../../sbom-nodejs.json || true
	@echo "✅ SBOM files generated: sbom-python.json, sbom-nodejs.json"

security-scan: security
	@echo "Security scan complete. Check reports for details."

git-setup:
	@echo "Configuring git for optimal merge handling..."
	@bash scripts/setup_git_config.sh

check-conflicts:
	@echo "Checking for potential merge conflicts with main..."
	@bash scripts/check_conflicts.sh main -v
