# 🚀 Repository Bootstrap Commands

## Quick Start (5 Minutes)

```bash
# 1. Clone repository
git clone https://github.com/sonaiso/sanadcom.git
cd sanadcom

# 2. Quick start with Docker (recommended)
make docker-up

# Access points:
# - Frontend: http://localhost:3000
# - Backend API: http://localhost:8000
# - API Docs: http://localhost:8000/docs
# - Chroma Vector DB: http://localhost:8001
```

---

## Manual Setup (Development)

### Prerequisites

- **Python 3.11+** (`python --version`)
- **Node.js 20+** (`node --version`)
- **Docker & Docker Compose** (`docker --version`)
- **PostgreSQL 15+** (can use Docker)
- **Redis 7+** (can use Docker)
- **Git** (`git --version`)

---

### Backend Setup

```bash
# 1. Navigate to backend directory
cd src/backend

# 2. Create Python virtual environment
python -m venv venv

# 3. Activate virtual environment
# Linux/macOS:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# 4. Upgrade pip
pip install --upgrade pip

# 5. Install dependencies
pip install -r requirements.txt

# 6. Copy environment template
cp ../../config/env.example .env

# 7. Edit .env file (configure database, secrets, etc.)
# Required variables:
#   - DATABASE_URL=postgresql://user:pass@localhost:5432/sico_grc
#   - SECRET_KEY=<generate with: openssl rand -hex 32>
#   - ENCRYPTION_KEY=<generate with: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())">
nano .env  # or use your preferred editor

# 8. Start PostgreSQL (if using Docker)
docker run -d \
  --name sico-postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=sico_grc \
  -p 5432:5432 \
  postgres:15

# 9. Start Redis (if using Docker)
docker run -d \
  --name sico-redis \
  -p 6379:6379 \
  redis:7

# 10. Run database migrations
alembic upgrade head

# 11. Load sample data (optional, for testing)
python scripts/load_sample_data.py

# 12. Start backend server
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Server will start at: http://localhost:8000
# API docs available at: http://localhost:8000/docs
```

---

### Frontend Setup

```bash
# 1. Navigate to frontend directory (in a new terminal)
cd src/frontend

# 2. Install dependencies
npm install

# 3. Copy environment template
cp ../../config/env.example .env.local

# 4. Edit .env.local file
# Required variables:
#   - NEXT_PUBLIC_API_URL=http://localhost:8000
nano .env.local

# 5. Start development server
npm run dev

# Server will start at: http://localhost:3000
```

---

### AI/RAG Engine Setup (Optional)

```bash
# 1. Navigate to AI directory
cd ai

# 2. Install AI dependencies
pip install -r requirements.txt

# 3. Download embedding model (first time only, ~1GB download)
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('intfloat/multilingual-e5-large')"

# 4. Start Chroma vector database (Docker)
docker run -d \
  --name sico-chroma \
  -p 8001:8000 \
  chromadb/chroma:latest

# 5. Generate embeddings (ingest control documents)
python scripts/generate_embeddings.py --framework all

# 6. Test RAG query (optional)
python -m pytest tests/test_rag_retrieval.py -v
```

---

## Docker Compose Setup (Recommended for Production-Like Environment)

```bash
# 1. Navigate to project root
cd sanadcom

# 2. Copy environment file
cp .env.production.example .env.production

# 3. Edit .env.production (set database passwords, secrets, etc.)
nano .env.production

# 4. Start all services (backend, frontend, PostgreSQL, Redis, Chroma)
docker-compose -f deployment/docker-compose.yml up -d

# 5. Check service status
docker-compose -f deployment/docker-compose.yml ps

# 6. View logs
docker-compose -f deployment/docker-compose.yml logs -f

# 7. Run database migrations (first time only)
docker-compose -f deployment/docker-compose.yml exec backend alembic upgrade head

# 8. Load sample data (optional)
docker-compose -f deployment/docker-compose.yml exec backend python scripts/load_sample_data.py

# Access points:
# - Frontend: http://localhost:3000
# - Backend API: http://localhost:8000
# - API Docs: http://localhost:8000/docs
# - Chroma Vector DB: http://localhost:8001

# 9. Stop services
docker-compose -f deployment/docker-compose.yml down

# 10. Stop and remove volumes (WARNING: deletes database)
docker-compose -f deployment/docker-compose.yml down -v
```

---

## Running Tests

### Backend Tests

```bash
cd src/backend

# Run all tests
pytest tests/ -v

# Run with coverage report
pytest tests/ --cov=. --cov-report=html

# Run specific test file
pytest tests/test_auth.py -v

# Run specific test
pytest tests/test_auth.py::test_login_success -v

# Run tests in parallel (faster)
pytest tests/ -n auto
```

### Frontend Tests

```bash
cd src/frontend

# Run unit tests
npm test

# Run tests in watch mode
npm test -- --watch

# Run tests with coverage
npm test -- --coverage

# Run end-to-end tests (requires backend running)
npm run test:e2e
```

### AI/RAG Tests

```bash
cd ai

# Run RAG tests
pytest tests/ -v

# Test retrieval accuracy
pytest tests/test_rag_retrieval.py -v

# Test citation validation
pytest tests/test_citations.py -v
```

---

## Running Security Scans

### Local Security Scans (via Makefile)

```bash
# Run all security scans
make security

# Run dependency vulnerability scans only
make security-deps

# Run SAST (Static Application Security Testing) only
make security-sast
```

### Manual Security Scans

```bash
# Python dependency scan (Safety)
cd src/backend
pip install safety
safety check --json

# Node.js dependency scan (npm audit)
cd src/frontend
npm audit --json

# Python SAST (Bandit)
cd src/backend
pip install bandit
bandit -r . -f json -o bandit-report.json

# Secret scanning (Gitleaks)
# Install: https://github.com/gitleaks/gitleaks
gitleaks detect --source . --verbose

# Generate SBOM (Software Bill of Materials)
# Python
cd src/backend
pip install cyclonedx-bom
cyclonedx-py requirements -i requirements.txt -o sbom-python.json

# Node.js
cd src/frontend
npm install -g @cyclonedx/cyclonedx-npm
cyclonedx-npm --output-file sbom-nodejs.json
```

---

## Code Quality Checks

### Backend (Python)

```bash
cd src/backend

# Install tools
pip install ruff mypy black

# Run linter (ruff)
ruff check .

# Fix auto-fixable issues
ruff check . --fix

# Run type checker (mypy)
mypy .

# Format code (black)
black .

# Check formatting without changes
black . --check
```

### Frontend (TypeScript/JavaScript)

```bash
cd src/frontend

# Run linter (ESLint)
npm run lint

# Fix auto-fixable issues
npm run lint -- --fix

# Type check
npm run type-check

# Format code (Prettier)
npm run format

# Check formatting without changes
npm run format:check
```

---

## Database Operations

### Migrations

```bash
cd src/backend

# Create new migration (auto-generate based on model changes)
alembic revision --autogenerate -m "Add new table for X"

# Apply migrations (upgrade to latest)
alembic upgrade head

# Downgrade one migration
alembic downgrade -1

# Show current migration version
alembic current

# Show migration history
alembic history
```

### Database Utilities

```bash
cd src/backend

# Reset database (WARNING: deletes all data)
alembic downgrade base
alembic upgrade head

# Backup database (PostgreSQL)
pg_dump -U postgres -d sico_grc -f backup_$(date +%Y%m%d).sql

# Restore database
psql -U postgres -d sico_grc < backup_20260210.sql

# Load sample data
python scripts/load_sample_data.py

# Load control libraries (ECC/CCC/PDPL)
python scripts/load_controls.py --framework ECC
python scripts/load_controls.py --framework CCC
python scripts/load_controls.py --framework PDPL
python scripts/load_controls.py --framework all
```

---

## Pre-Commit Hooks (Recommended)

```bash
# Install pre-commit framework
pip install pre-commit

# Install git hooks (run from project root)
pre-commit install

# Run hooks manually on all files
pre-commit run --all-files

# Update hooks to latest versions
pre-commit autoupdate
```

---

## Environment Variables Reference

### Backend (.env)

```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/sico_grc

# Security
SECRET_KEY=<generate with: openssl rand -hex 32>
ENCRYPTION_KEY=<generate with Fernet.generate_key()>
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# TLS/HTTPS (production only)
TLS_ENABLED=true
TLS_CERT_PATH=/path/to/cert.pem
TLS_KEY_PATH=/path/to/key.pem

# Redis
REDIS_URL=redis://localhost:6379/0

# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_PER_HOUR=1000

# Audit Logging
AUDIT_LOG_RETENTION_YEARS=7
LOG_LEVEL=INFO

# AI/RAG
CHROMA_URL=http://localhost:8001
OPENAI_API_KEY=sk-... (optional, for GPT-4)
AZURE_OPENAI_ENDPOINT=https://... (alternative to OpenAI)

# Email (for alerts)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@example.com
SMTP_PASSWORD=your-app-password
```

### Frontend (.env.local)

```bash
# API
NEXT_PUBLIC_API_URL=http://localhost:8000

# i18n
NEXT_PUBLIC_DEFAULT_LOCALE=ar
NEXT_PUBLIC_LOCALES=en,ar

# Analytics (optional)
NEXT_PUBLIC_GA_ID=G-XXXXXXXXXX
```

---

## Troubleshooting

### Issue: Backend won't start - "connection refused" to PostgreSQL

**Solution:**
```bash
# Check if PostgreSQL is running
docker ps | grep postgres

# If not running, start it:
docker run -d --name sico-postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=sico_grc \
  -p 5432:5432 \
  postgres:15

# Or use system PostgreSQL:
sudo systemctl start postgresql  # Linux
brew services start postgresql   # macOS
```

### Issue: Frontend can't connect to backend (CORS error)

**Solution:**
```bash
# Check backend is running:
curl http://localhost:8000/api/v1/health

# If not running, start backend:
cd src/backend && uvicorn main:app --reload

# Check CORS settings in src/backend/core/config.py
# Ensure ALLOWED_ORIGINS includes http://localhost:3000
```

### Issue: "Module not found" errors in Python

**Solution:**
```bash
# Ensure virtual environment is activated:
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# Reinstall dependencies:
pip install -r requirements.txt

# If still failing, clear pip cache:
pip cache purge
pip install -r requirements.txt --no-cache-dir
```

### Issue: Docker Compose fails with "port already in use"

**Solution:**
```bash
# Find process using the port (e.g., 8000):
lsof -i :8000  # Linux/macOS
netstat -ano | findstr :8000  # Windows

# Kill the process:
kill -9 <PID>  # Linux/macOS
taskkill /PID <PID> /F  # Windows

# Or change port in docker-compose.yml
```

### Issue: Alembic migration fails

**Solution:**
```bash
# Check current migration state:
alembic current

# If "out of sync", reset to base and re-apply:
alembic downgrade base
alembic upgrade head

# If still failing, manually drop alembic_version table:
psql -U postgres -d sico_grc -c "DROP TABLE alembic_version;"
alembic upgrade head
```

---

## Performance Tips

### Backend
- Use `uvicorn` with `--workers 4` for production (4 = CPU cores)
- Enable Redis caching for frequently accessed data
- Use database connection pooling (configured in `core/database.py`)
- Index frequently queried columns (see migrations)

### Frontend
- Build for production: `npm run build` (much faster than dev mode)
- Enable CDN for static assets (Vercel/Netlify auto-does this)
- Use `next/image` for automatic image optimization
- Enable SWR caching for API calls

### Database
- Run `VACUUM ANALYZE` monthly (PostgreSQL maintenance)
- Monitor slow queries with `pg_stat_statements`
- Increase `shared_buffers` to 25% of RAM (PostgreSQL config)

---

## Next Steps

1. ✅ Complete backend setup → Test at http://localhost:8000/docs
2. ✅ Complete frontend setup → Test at http://localhost:3000
3. ✅ Run security scans → `make security`
4. ✅ Run tests → `pytest tests/ -v` (backend), `npm test` (frontend)
5. ✅ Load sample data → `python scripts/load_sample_data.py`
6. ✅ Review documentation:
   - [90-Day Engineering Plan](docs/engineering/90_DAY_ENGINEERING_PLAN.md)
   - [Security Pipeline](docs/SECURITY_PIPELINE.md)
   - [API Documentation](docs/api/README.md)

---

**Last Updated:** 2026-02-10  
**Version:** 1.0  
**Maintained by:** SICO GRC Platform Team
