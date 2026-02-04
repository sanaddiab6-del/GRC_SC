#!/bin/bash

# SICO GRC Platform Setup Script

set -e

echo "🛡️  SICO GRC Platform - Setup Script"
echo "====================================="
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Python $python_version detected"

# Check Node.js version
echo "Checking Node.js version..."
node_version=$(node --version 2>&1)
echo "✓ Node.js $node_version detected"

# Backend setup
echo ""
echo "Setting up backend..."
cd src/backend

if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

echo "Activating virtual environment..."
source venv/bin/activate

echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "✓ Backend setup complete"

# Frontend setup
echo ""
echo "Setting up frontend..."
cd ../frontend

if [ ! -d "node_modules" ]; then
    echo "Installing Node.js dependencies..."
    npm install
fi

echo "✓ Frontend setup complete"

# Configuration
cd ../..
echo ""
echo "Setting up configuration..."
if [ ! -f "config/.env" ]; then
    cp config/env.example config/.env
    echo "✓ Created config/.env from template"
    echo "⚠️  Please update config/.env with your actual configuration"
else
    echo "✓ config/.env already exists"
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "To start the backend:"
echo "  cd src/backend"
echo "  source venv/bin/activate"
echo "  uvicorn main:app --reload"
echo ""
echo "To start the frontend:"
echo "  cd src/frontend"
echo "  npm run dev"
echo ""
echo "Or use Docker:"
echo "  docker-compose -f deployment/docker-compose.yml up"
echo ""
