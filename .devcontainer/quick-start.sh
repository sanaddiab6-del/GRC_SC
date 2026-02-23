#!/bin/bash

# Quick Start Script - Minimal setup for immediate development
# Run this if you want to start coding right away without waiting for full setup

set -e

echo "⚡ Quick Start - Minimal Setup"
echo "================================"
echo ""

WORKSPACE_DIR="/workspaces/sanadcom"
cd $WORKSPACE_DIR

# 1. Create .env if needed
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file..."
    cat > .env <<EOF
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/sico_grc
REDIS_URL=redis://localhost:6379/0
VECTOR_DB_HOST=localhost
VECTOR_DB_PORT=8001
SECRET_KEY=dev-secret-key-change-in-production-must-be-at-least-32-characters-long
ENCRYPTION_KEY=
RATE_LIMIT_ENABLED=true
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_PER_HOUR=1000
TLS_ENABLED=false
AUDIT_LOG_RETENTION_YEARS=7
LOG_LEVEL=INFO
EOF
    echo "✅ .env created"
fi

# 2. Install minimal backend dependencies
echo ""
echo "📦 Installing minimal backend dependencies..."
cd $WORKSPACE_DIR/src/backend
pip install -q fastapi uvicorn sqlalchemy asyncpg alembic redis pydantic python-dotenv httpx

echo ""
echo "✅ Quick start complete!"
echo ""
echo "🎯 Next steps:"
echo "  1. Start Docker services: cd deployment && docker-compose up -d"
echo "  2. Start backend: cd src/backend && uvicorn main:app --reload --host 0.0.0.0"
echo ""
echo "💡 For full setup: bash .devcontainer/setup.sh"
echo "💡 Background setup log: tail -f /tmp/setup.log"
echo ""
