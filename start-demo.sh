#!/bin/bash

echo "=========================================="
echo "🚀 SICO GRC Platform - Quick Start"
echo "=========================================="
echo ""

# Kill any existing servers
echo "🔧 Stopping any existing servers..."
pkill -f "uvicorn main:app" 2>/dev/null
pkill -f "next dev" 2>/dev/null
pkill -f "python3 -m http.server" 2>/dev/null
sleep 2

# Start backend
echo "🔵 Starting Backend API (FastAPI)..."
cd /workspaces/sanadcom/src/backend
uvicorn main:app --host 0.0.0.0 --port 8000 --reload > /tmp/backend.log 2>&1 &
BACKEND_PID=$!
echo "   Backend PID: $BACKEND_PID"

sleep 5

# Check backend health
echo "🔍 Checking backend health..."
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "   ✅ Backend is running on http://localhost:8000"
else
    echo "   ⚠️  Backend might still be starting..."
fi

# Start frontend
echo "🟢 Starting Frontend (Next.js)..."
cd /workspaces/sanadcom/src/frontend
npm run dev > /tmp/frontend.log 2>&1 &
FRONTEND_PID=$!
echo "   Frontend PID: $FRONTEND_PID"

sleep 8

# Check frontend
echo "🔍 Checking frontend..."
if curl -s http://localhost:3000 > /dev/null 2>&1; then
    echo "   ✅ Frontend is running on http://localhost:3000"
else
    echo "   ⚠️  Frontend might still be starting..."
fi

echo ""
echo "=========================================="
echo "✅ PLATFORM READY!"
echo "=========================================="
echo ""
echo "📊 Access Points:"
echo "   🌐 Frontend Dashboard:  http://localhost:3000"
echo "   ⚙️  Backend API:         http://localhost:8000"
echo "   📖 API Documentation:   http://localhost:8000/docs"
echo ""
echo "🔑 Demo Credentials:"
echo "   Email:    admin@snb.sa"
echo "   Password: Password123!"
echo ""
echo "📝 Logs:"
echo "   Backend:  tail -f /tmp/backend.log"
echo "   Frontend: tail -f /tmp/frontend.log"
echo ""
echo "🛑 To stop servers:"
echo "   kill $BACKEND_PID $FRONTEND_PID"
echo ""
echo "=========================================="
