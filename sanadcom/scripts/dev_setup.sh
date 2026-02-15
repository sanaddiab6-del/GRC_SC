#!/bin/bash
# Development setup script

set -e

echo "🚀 SICO GRC Platform - Development Setup"
echo "========================================"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

echo ""
echo "1️⃣  Starting infrastructure services (PostgreSQL, Redis, Chroma)..."
docker-compose -f deployment/docker-compose.yml up -d postgres redis chroma

echo "⏳ Waiting for PostgreSQL to be ready..."
sleep 5

echo ""
echo "2️⃣  Installing backend dependencies..."
cd src/backend
pip install -r requirements.txt

echo ""
echo "3️⃣  Running database migrations..."
alembic upgrade head

echo ""
echo "4️⃣  Loading sample data..."
cd ../..
python scripts/load_sample_data.py

echo ""
echo "5️⃣  Installing AI dependencies..."
cd ai
pip install -r requirements.txt
cd ..

echo ""
echo "6️⃣  Installing frontend dependencies..."
cd src/frontend
npm install

echo ""
echo "✅ Setup complete!"
echo ""
echo "To start the development servers:"
echo "  Backend:  cd src/backend && uvicorn main:app --reload"
echo "  Frontend: cd src/frontend && npm run dev"
echo ""
echo "Or use Docker Compose:"
echo "  make docker-up"
