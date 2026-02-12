#!/bin/bash

# SICO GRC Platform - Codespace Setup Script
# This script initializes the development environment in GitHub Codespaces

set -e

echo "🚀 Setting up SICO GRC Platform in Codespaces..."
echo ""

WORKSPACE_DIR="/workspaces/sanadcom"
cd $WORKSPACE_DIR

# 1. Install backend dependencies
echo "📦 Installing backend dependencies..."
cd $WORKSPACE_DIR/src/backend
pip install --no-cache-dir -r requirements.txt
echo "✅ Backend dependencies installed"
echo ""

# 2. Install AI dependencies
echo "🤖 Installing AI dependencies..."
if [ -f "$WORKSPACE_DIR/ai/requirements.txt" ]; then
    pip install --no-cache-dir -r $WORKSPACE_DIR/ai/requirements.txt
    echo "✅ AI dependencies installed"
else
    echo "⚠️  AI requirements.txt not found, skipping"
fi
echo ""

# 3. Install frontend dependencies
echo "📦 Installing frontend dependencies..."
if [ -d "$WORKSPACE_DIR/src/frontend" ]; then
    cd $WORKSPACE_DIR/src/frontend
    npm install
    echo "✅ Frontend dependencies installed"
fi
echo ""

# 4. Create .env file if not exists
echo "⚙️  Setting up environment configuration..."
cd $WORKSPACE_DIR
if [ ! -f ".env" ]; then
    if [ -f "config/env.example" ]; then
        cp config/env.example .env
        echo "✅ Created .env file from config/env.example"
    else
        echo "Creating basic .env file..."
        cat > .env <<EOF
# Database
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/sico_grc
REDIS_URL=redis://localhost:6379/0

# Vector Database
VECTOR_DB_HOST=localhost
VECTOR_DB_PORT=8001

# Security (Generate secure keys in production)
SECRET_KEY=dev-secret-key-change-in-production-must-be-at-least-32-characters-long
ENCRYPTION_KEY=

# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_PER_HOUR=1000

# TLS (Enable in production)
TLS_ENABLED=false

# Logging
AUDIT_LOG_RETENTION_YEARS=7
LOG_LEVEL=INFO
EOF
        echo "✅ Created basic .env file"
    fi
else
    echo "✅ .env file already exists"
fi
echo ""

# 5. Start Docker Compose services
echo "🐳 Starting Docker services (PostgreSQL, Redis, Chroma)..."
cd $WORKSPACE_DIR/deployment
docker-compose up -d postgres redis chroma
echo "✅ Docker services started"
echo ""

# 6. Wait for PostgreSQL to be ready
echo "⏳ Waiting for PostgreSQL to be ready..."
max_attempts=30
attempt=0

while [ $attempt -lt $max_attempts ]; do
    if docker-compose exec -T postgres pg_isready -U postgres > /dev/null 2>&1; then
        echo "✅ PostgreSQL is ready"
        break
    fi
    attempt=$((attempt + 1))
    if [ $attempt -eq $max_attempts ]; then
        echo "⚠️  PostgreSQL did not become ready in time, but continuing..."
        break
    fi
    echo "Waiting for PostgreSQL... (attempt $attempt/$max_attempts)"
    sleep 2
done
echo ""

# 7. Run database migrations
echo "🔧 Running database migrations..."
cd $WORKSPACE_DIR/src/backend
if [ -f "alembic.ini" ]; then
    alembic upgrade head 2>&1 || echo "⚠️  Migration failed or no migrations to run"
    echo "✅ Database migrations complete"
else
    echo "⚠️  alembic.ini not found, skipping migrations"
fi
echo ""

echo "================================================"
echo "✅ Setup complete! Your environment is ready."
echo "================================================"
echo ""
echo "🎯 Quick Start Commands:"
echo ""
echo "  Start Backend API:"
echo "    cd src/backend"
echo "    uvicorn main:app --reload --host 0.0.0.0"
echo ""
echo "  Start Frontend:"
echo "    cd src/frontend"
echo "    npm run dev"
echo ""
echo "  View Docker logs:"
echo "    cd deployment"
echo "    docker-compose logs -f"
echo ""
echo "📚 Access Points (after starting services):"
echo "  • Backend API:  http://localhost:8000"
echo "  • API Docs:     http://localhost:8000/docs"
echo "  • Frontend:     http://localhost:3000"
echo ""
echo "💡 Tips:"
echo "  • All database services are running in Docker"
echo "  • Backend and frontend should be started manually"
echo "  • Check QUICK_START.md for more details"
echo ""
