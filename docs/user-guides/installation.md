# Installation Guide

## Prerequisites

Before installing SICO GRC Platform, ensure you have:

- **Python 3.11+**
- **Node.js 20+**
- **PostgreSQL 15+**
- **Redis**
- **Git**

## Quick Start with Docker (Recommended)

The fastest way to get started is using Docker Compose:

```bash
# Clone the repository
git clone https://github.com/sonaiso/sanadcom.git
cd sanadcom

# Start all services
docker-compose -f deployment/docker-compose.yml up -d

# Check status
docker-compose -f deployment/docker-compose.yml ps
```

Access the application:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/api/docs

## Manual Installation

### 1. Clone Repository

```bash
git clone https://github.com/sonaiso/sanadcom.git
cd sanadcom
```

### 2. Backend Setup

```bash
cd src/backend

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment configuration
cp ../../config/env.example .env

# Edit .env with your configuration
nano .env
```

### 3. Frontend Setup

```bash
cd ../frontend

# Install dependencies
npm install

# Copy environment configuration
cp ../../config/env.example .env.local

# Edit .env.local with your configuration
nano .env.local
```

### 4. Database Setup

```bash
# Start PostgreSQL
sudo systemctl start postgresql

# Create database
createdb sico_grc

# Run migrations (once implemented)
# alembic upgrade head
```

### 5. Start Services

**Terminal 1 - Backend:**
```bash
cd src/backend
source venv/bin/activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd src/frontend
npm run dev
```

**Terminal 3 - Redis (if not using system service):**
```bash
redis-server
```

## Verification

### Backend Health Check
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "sico-grc-api"
}
```

### Frontend
Open your browser and navigate to http://localhost:3000

## Troubleshooting

### Port Already in Use
If ports 3000 or 8000 are already in use:

```bash
# For backend, change port in .env:
API_PORT=8080

# For frontend, run with custom port:
npm run dev -- -p 3001
```

### Database Connection Issues
Verify your PostgreSQL is running:
```bash
sudo systemctl status postgresql
```

Check your DATABASE_URL in .env matches your PostgreSQL configuration.

### Node.js Dependency Issues
```bash
cd src/frontend
rm -rf node_modules package-lock.json
npm install
```

## Next Steps

- Configure your environment variables in `config/.env`
- Read the [User Guide](../user-guides/getting-started.md)
- Explore the [API Documentation](http://localhost:8000/api/docs)
- Check the [Architecture Overview](../architecture/overview.md)
