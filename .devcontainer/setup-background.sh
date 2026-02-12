#!/bin/bash

# SICO GRC Platform - Background Setup Script
# This runs in the background so the Codespace UI is available immediately

# Log file for user to check progress
LOG_FILE="/tmp/setup.log"
WORKSPACE_DIR="/workspaces/sanadcom"

echo "================================================" | tee -a $LOG_FILE
echo "🚀 SICO GRC Platform - Background Setup" | tee -a $LOG_FILE
echo "================================================" | tee -a $LOG_FILE
echo "Started at: $(date)" | tee -a $LOG_FILE
echo "Log file: $LOG_FILE" | tee -a $LOG_FILE
echo "" | tee -a $LOG_FILE
echo "✨ Your Codespace is ready to use!" | tee -a $LOG_FILE
echo "   Dependencies are installing in the background." | tee -a $LOG_FILE
echo "" | tee -a $LOG_FILE
echo "📊 Check progress: tail -f $LOG_FILE" | tee -a $LOG_FILE
echo "================================================" | tee -a $LOG_FILE
echo "" | tee -a $LOG_FILE

cd $WORKSPACE_DIR || exit 1

# 1. Install essential backend dependencies (fast)
echo "📦 [1/5] Installing essential backend dependencies..." | tee -a $LOG_FILE
cd $WORKSPACE_DIR/src/backend
if [ -f "requirements.txt" ]; then
    # Install only essential packages first (without heavy AI deps)
    pip install --no-cache-dir -q fastapi uvicorn sqlalchemy asyncpg alembic redis pydantic python-dotenv 2>&1 | tee -a $LOG_FILE
    echo "✅ Essential backend packages installed" | tee -a $LOG_FILE
else
    echo "⚠️  requirements.txt not found" | tee -a $LOG_FILE
fi
echo "" | tee -a $LOG_FILE

# 2. Install frontend dependencies (can be slow)
echo "📦 [2/5] Installing frontend dependencies..." | tee -a $LOG_FILE
if [ -d "$WORKSPACE_DIR/src/frontend" ]; then
    cd $WORKSPACE_DIR/src/frontend
    # Use npm ci for faster, reproducible installs
    if [ -f "package-lock.json" ]; then
        npm ci --prefer-offline --no-audit 2>&1 | tee -a $LOG_FILE || npm install 2>&1 | tee -a $LOG_FILE
    else
        npm install --prefer-offline --no-audit 2>&1 | tee -a $LOG_FILE
    fi
    echo "✅ Frontend dependencies installed" | tee -a $LOG_FILE
else
    echo "⚠️  Frontend directory not found" | tee -a $LOG_FILE
fi
echo "" | tee -a $LOG_FILE

# 3. Create .env file if not exists
echo "⚙️  [3/5] Setting up environment configuration..." | tee -a $LOG_FILE
cd $WORKSPACE_DIR
if [ ! -f ".env" ]; then
    if [ -f "config/env.example" ]; then
        cp config/env.example .env
        echo "✅ Created .env file from config/env.example" | tee -a $LOG_FILE
    else
        echo "Creating basic .env file..." | tee -a $LOG_FILE
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
        echo "✅ Created basic .env file" | tee -a $LOG_FILE
    fi
else
    echo "✅ .env file already exists" | tee -a $LOG_FILE
fi
echo "" | tee -a $LOG_FILE

# 4. Install remaining backend dependencies (slower packages)
echo "📦 [4/5] Installing remaining backend dependencies..." | tee -a $LOG_FILE
cd $WORKSPACE_DIR/src/backend
if [ -f "requirements.txt" ]; then
    pip install --no-cache-dir -q -r requirements.txt 2>&1 | tee -a $LOG_FILE
    echo "✅ All backend dependencies installed" | tee -a $LOG_FILE
else
    echo "⚠️  requirements.txt not found" | tee -a $LOG_FILE
fi
echo "" | tee -a $LOG_FILE

# 5. Optional: Install AI dependencies (can skip if not needed)
echo "🤖 [5/5] Installing AI dependencies (optional, may take a while)..." | tee -a $LOG_FILE
if [ -f "$WORKSPACE_DIR/ai/requirements.txt" ]; then
    echo "   This may take 5-10 minutes for ML packages..." | tee -a $LOG_FILE
    pip install --no-cache-dir -q -r $WORKSPACE_DIR/ai/requirements.txt 2>&1 | tee -a $LOG_FILE
    echo "✅ AI dependencies installed" | tee -a $LOG_FILE
else
    echo "⚠️  AI requirements.txt not found, skipping" | tee -a $LOG_FILE
fi
echo "" | tee -a $LOG_FILE

echo "================================================" | tee -a $LOG_FILE
echo "✅ Background setup complete!" | tee -a $LOG_FILE
echo "================================================" | tee -a $LOG_FILE
echo "Completed at: $(date)" | tee -a $LOG_FILE
echo "" | tee -a $LOG_FILE
echo "🎯 Quick Start:" | tee -a $LOG_FILE
echo "" | tee -a $LOG_FILE
echo "  Start Docker services (when needed):" | tee -a $LOG_FILE
echo "    cd deployment && docker-compose up -d" | tee -a $LOG_FILE
echo "" | tee -a $LOG_FILE
echo "  Start Backend API:" | tee -a $LOG_FILE
echo "    cd src/backend && uvicorn main:app --reload --host 0.0.0.0" | tee -a $LOG_FILE
echo "" | tee -a $LOG_FILE
echo "  Start Frontend:" | tee -a $LOG_FILE
echo "    cd src/frontend && npm run dev" | tee -a $LOG_FILE
echo "" | tee -a $LOG_FILE
echo "📚 Access Points:" | tee -a $LOG_FILE
echo "  • Backend API:  http://localhost:8000" | tee -a $LOG_FILE
echo "  • API Docs:     http://localhost:8000/docs" | tee -a $LOG_FILE
echo "  • Frontend:     http://localhost:3000" | tee -a $LOG_FILE
echo "" | tee -a $LOG_FILE
echo "💡 View this message anytime: cat $LOG_FILE" | tee -a $LOG_FILE
echo "================================================" | tee -a $LOG_FILE
