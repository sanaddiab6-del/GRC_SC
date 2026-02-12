#!/bin/bash

# SICO GRC Platform - Codespace Setup Script
# This script can be run manually for full setup
# For quick start, use: bash .devcontainer/quick-start.sh

set -e

echo "🚀 Setting up SICO GRC Platform in Codespaces..."
echo ""
echo "⚡ Tip: This installs everything. For faster setup, use:"
echo "   bash .devcontainer/quick-start.sh"
echo ""

WORKSPACE_DIR="/workspaces/sanadcom"
cd $WORKSPACE_DIR

# 1. Install backend dependencies
echo "📦 [1/6] Installing backend dependencies..."
cd $WORKSPACE_DIR/src/backend
pip install --no-cache-dir -r requirements.txt
echo "✅ Backend dependencies installed"
echo ""

# 2. Install AI dependencies (optional)
echo "🤖 [2/6] Installing AI dependencies..."
if [ -f "$WORKSPACE_DIR/ai/requirements.txt" ]; then
    echo "   ⏳ This may take 5-10 minutes for ML packages..."
    pip install --no-cache-dir -r $WORKSPACE_DIR/ai/requirements.txt
    echo "✅ AI dependencies installed"
else
    echo "⚠️  AI requirements.txt not found, skipping"
fi
echo ""

# 3. Install frontend dependencies
echo "📦 [3/6] Installing frontend dependencies..."
if [ -d "$WORKSPACE_DIR/src/frontend" ]; then
    cd $WORKSPACE_DIR/src/frontend
    if [ -f "package-lock.json" ]; then
        npm ci --prefer-offline --no-audit
    else
        npm install --prefer-offline --no-audit
    fi
    echo "✅ Frontend dependencies installed"
fi
echo ""

# 4. Create .env file if not exists
echo "⚙️  [4/6] Setting up environment configuration..."
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

# 5. Start Docker Compose services (optional)
echo "🐳 [5/6] Docker services (optional)..."
echo "   Run manually when needed: cd deployment && docker-compose up -d"
echo "   Services: PostgreSQL, Redis, Chroma"
echo ""

# 6. Database migrations (optional)
echo "🔧 [6/6] Database migrations (optional)..."
echo "   Run after Docker is up: cd src/backend && alembic upgrade head"
echo ""

echo "================================================"
echo "✅ Setup complete! Your environment is ready."
echo "================================================"
echo ""
echo "🎯 Quick Start Commands:"
echo ""
echo "  Start Docker services:"
echo "    cd deployment && docker-compose up -d"
echo ""
echo "  Start Backend API:"
echo "    cd src/backend"
echo "    uvicorn main:app --reload --host 0.0.0.0"
echo ""
echo "  Start Frontend:"
echo "    cd src/frontend"
echo "    npm run dev"
echo ""
echo "📚 Access Points (after starting services):"
echo "  • Backend API:  http://localhost:8000"
echo "  • API Docs:     http://localhost:8000/docs"
echo "  • Frontend:     http://localhost:3000"
echo ""
echo "💡 Tips:"
echo "  • For minimal setup: bash .devcontainer/quick-start.sh"
echo "  • Check background setup: tail -f /tmp/setup.log"
echo "  • See QUICK_START.md for more details"
echo ""
