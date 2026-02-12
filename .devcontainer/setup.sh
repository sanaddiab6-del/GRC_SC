#!/bin/bash
set -e

echo "🚀 Setting up SICO GRC Platform development environment..."

# Update system packages
echo "📦 Updating system packages..."
sudo apt-get update

# Install PostgreSQL client
echo "🐘 Installing PostgreSQL client..."
sudo apt-get install -y postgresql-client

# Install Redis tools
echo "🔴 Installing Redis tools..."
sudo apt-get install -y redis-tools

# Backend setup
echo "🐍 Setting up Python backend..."
cd src/backend

# Install Python dependencies
if [ -f "requirements.txt" ]; then
    pip install --upgrade pip
    pip install -r requirements.txt
    echo "✅ Python dependencies installed"
fi

# Run database migrations if alembic is available
if command -v alembic &> /dev/null; then
    echo "🔄 Running database migrations..."
    alembic upgrade head || echo "⚠️  Migrations will run when database is available"
fi

# Frontend setup
echo "⚛️  Setting up Node.js frontend..."
cd ../frontend

# Install Node dependencies
if [ -f "package.json" ]; then
    npm install
fi

# Return to root
cd ../..

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p data/controls/ecc data/controls/ccc data/controls/pdpl
mkdir -p data/evidence
mkdir -p data/mappings
mkdir -p vectordb
mkdir -p logs

# Copy environment example if .env doesn't exist
if [ ! -f "src/backend/.env" ] && [ -f "config/env.example" ]; then
    echo "📝 Creating .env file from example..."
    cp config/env.example src/backend/.env
fi

# Set permissions
echo "🔒 Setting permissions..."
chmod +x scripts/*.sh
chmod +x start-dev.ps1
chmod +x deploy-launch.sh

echo "✅ Development environment setup complete!"
echo ""
echo "🎯 Quick Start Commands:"
echo "   Backend:  cd src/backend && uvicorn app.main:app --reload"
echo "   Frontend: cd src/frontend && npm run dev"
echo "   Full:     ./start-dev.ps1"
echo ""
echo "📚 Read QUICK_START.md for detailed instructions"
