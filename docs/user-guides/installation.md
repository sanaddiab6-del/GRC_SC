# SICO GRC Platform - Installation Guide

## Prerequisites

Before installing the SICO GRC Platform, ensure you have the following installed:

### Required Software

- **Docker** (20.10 or later)
- **Docker Compose** (2.0 or later)
- **Python** (3.11 or later)
- **Node.js** (18.0 or later)
- **npm** (9.0 or later)
- **Git**

### System Requirements

- **RAM**: Minimum 8GB (16GB recommended)
- **Storage**: 20GB free space
- **OS**: Linux, macOS, or Windows with WSL2

## Quick Start with Docker Compose

The fastest way to get started is using Docker Compose:

### 1. Clone Repository

```bash
git clone https://github.com/sonaiso/sanadcom.git
cd sanadcom
```

### 2. Run Setup Script

```bash
./scripts/setup.sh
```

This script will:
- Check prerequisites
- Create environment configuration
- Start all services with Docker Compose
- Load sample data
- Display access information

### 3. Access the Platform

After setup completes:

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Interactive API**: http://localhost:8000/redoc

## Manual Installation

If you prefer manual installation or need to customize the setup:

### Step 1: Environment Configuration

Create `.env` file from template:

```bash
cp config/env.example .env
```

Edit `.env` and update the following settings:

```bash
# Application
APP_NAME=SICO GRC Platform
DEBUG=True

# Database
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/sico_grc

# Redis
REDIS_URL=redis://localhost:6379/0

# Vector Database
VECTOR_DB_HOST=localhost
VECTOR_DB_PORT=8001

# AI Configuration
EMBEDDING_MODEL=intfloat/multilingual-e5-large
LLM_MODEL=gpt-4

# Security (CHANGE IN PRODUCTION)
SECRET_KEY=your-secret-key-here
```

### Step 2: Start Infrastructure Services

Start PostgreSQL, Redis, and Chroma using Docker Compose:

```bash
docker-compose -f deployment/docker-compose.yml up -d postgres redis chroma
```

Wait for services to be ready (~30 seconds):

```bash
docker-compose -f deployment/docker-compose.yml logs -f
# Press Ctrl+C when you see "database system is ready to accept connections"
```

### Step 3: Backend Setup

#### Install Python Dependencies

```bash
cd src/backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

#### Run Database Migrations

```bash
alembic upgrade head
```

#### Load Sample Data

```bash
cd ../..
python scripts/load_sample_data.py
```

#### Start Backend Server

```bash
cd src/backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be available at http://localhost:8000

### Step 4: Frontend Setup

Open a new terminal:

#### Install Node Dependencies

```bash
cd src/frontend
npm install
```

#### Start Development Server

```bash
npm run dev
```

Frontend will be available at http://localhost:3000

### Step 5: Verify Installation

1. **Check Backend Health**:
   ```bash
   curl http://localhost:8000/health
   ```

2. **Check API Documentation**:
   Open http://localhost:8000/docs in browser

3. **Check Frontend**:
   Open http://localhost:3000 in browser

4. **Test Control API**:
   ```bash
   curl http://localhost:8000/api/v1/controls?framework=ECC
   ```

5. **Test RAG Query**:
   ```bash
   curl -X POST http://localhost:8000/api/v1/ai/query \
     -H "Content-Type: application/json" \
     -d '{"query": "What are the governance requirements?"}'
   ```

## Production Deployment

### Using Docker

Build production images:

```bash
# Backend
docker build -f deployment/Dockerfile.backend -t sico-backend:latest src/backend

# Frontend
docker build -f deployment/Dockerfile.frontend -t sico-frontend:latest src/frontend
```

Run with production compose file:

```bash
docker-compose -f deployment/docker-compose.prod.yml up -d
```

### Using Kubernetes

(Coming in Phase 3)

Apply Kubernetes manifests:

```bash
kubectl apply -f deployment/k8s/
```

## Configuration

### Database Configuration

Edit `config/settings.yaml` or set environment variables:

```yaml
database:
  url: "postgresql://user:pass@host:5432/dbname"
  pool_size: 10
  max_overflow: 20
```

### AI/RAG Configuration

Configure embedding and LLM models:

```yaml
ai:
  embedding_model: "intfloat/multilingual-e5-large"
  llm_model: "gpt-4"
  rag:
    chunk_size: 512
    chunk_overlap: 128
    max_results: 5
```

### Security Configuration

**IMPORTANT**: Change default secret key in production:

```bash
# Generate secure secret key
openssl rand -hex 32

# Update .env
SECRET_KEY=your-generated-secret-key-here
```

## Troubleshooting

### Database Connection Errors

**Error**: `could not connect to server`

**Solution**:
```bash
# Check if PostgreSQL is running
docker-compose ps postgres

# Check logs
docker-compose logs postgres

# Restart if needed
docker-compose restart postgres
```

### Port Already in Use

**Error**: `Bind for 0.0.0.0:3000 failed: port is already allocated`

**Solution**:
```bash
# Find and kill process using port
# On Linux/Mac:
lsof -ti:3000 | xargs kill -9

# On Windows:
netstat -ano | findstr :3000
taskkill /PID <PID> /F
```

### Frontend Build Errors

**Error**: `Module not found` or `Cannot find module`

**Solution**:
```bash
cd src/frontend
rm -rf node_modules package-lock.json
npm install
npm run build
```

### Backend Import Errors

**Error**: `ModuleNotFoundError: No module named 'src'`

**Solution**:
```bash
cd src/backend
export PYTHONPATH=$PYTHONPATH:$(pwd)/../..
# Or add to .env:
echo "PYTHONPATH=../.." >> .env
```

### Vector Database Issues

**Error**: Cannot connect to Chroma

**Solution**:
```bash
# Restart Chroma
docker-compose restart chroma

# Rebuild embeddings
python ai/scripts/generate_embeddings.py
```

## Development Workflow

### Running Tests

```bash
# Backend tests
cd src/backend
pytest tests/ -v

# Frontend tests
cd src/frontend
npm test

# Run all tests
make test
```

### Linting and Formatting

```bash
# Backend
cd src/backend
black .
flake8 .

# Frontend
cd src/frontend
npm run lint
```

### Database Migrations

```bash
# Create new migration
cd src/backend
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback one version
alembic downgrade -1
```

## Useful Commands

### Docker Compose

```bash
# Start all services
make docker-up

# Stop all services
make docker-down

# View logs
docker-compose -f deployment/docker-compose.yml logs -f

# Restart specific service
docker-compose restart backend

# Rebuild images
docker-compose build --no-cache
```

### Database

```bash
# Connect to PostgreSQL
docker-compose exec postgres psql -U postgres -d sico_grc

# Backup database
docker-compose exec postgres pg_dump -U postgres sico_grc > backup.sql

# Restore database
docker-compose exec -T postgres psql -U postgres sico_grc < backup.sql
```

### Maintenance

```bash
# Clear Redis cache
docker-compose exec redis redis-cli FLUSHALL

# Reset database (WARNING: deletes all data)
cd src/backend
alembic downgrade base
alembic upgrade head
python ../../scripts/load_sample_data.py
```

## Next Steps

After installation:

1. **Explore the API**: Visit http://localhost:8000/docs
2. **Review Controls**: Browse control library in frontend
3. **Test RAG**: Try bilingual queries in Arabic and English
4. **Read Documentation**: Check `/docs` folder for guides
5. **Customize**: Modify controls and evidence catalogs for your organization

## Support

For issues or questions:

- **GitHub Issues**: https://github.com/sonaiso/sanadcom/issues
- **Documentation**: [docs/](../../docs/)
- **Contributing**: [CONTRIBUTING.md](../../CONTRIBUTING.md)

## Security Note

This installation guide is for development environments. For production deployments:

1. Complete **Phase 2.1 Security Remediation** first
2. Enable authentication and authorization
3. Configure TLS/HTTPS
4. Implement field-level encryption
5. Set up comprehensive audit logging
6. Follow security best practices in [SECURITY_PIPELINE.md](../SECURITY_PIPELINE.md)
