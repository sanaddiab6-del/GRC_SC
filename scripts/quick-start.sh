#!/bin/bash

# SICO GRC Platform - Quick Start Script

set -e

echo "🛡️  SICO GRC Platform - Quick Start"
echo "===================================="
echo ""

# Check prerequisites
check_prerequisites() {
    echo "Checking prerequisites..."
    
    if ! command -v docker &> /dev/null; then
        echo "❌ Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        echo "❌ Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    echo "✅ Prerequisites check passed"
    echo ""
}

# Setup environment
setup_environment() {
    echo "Setting up environment..."
    
    if [ ! -f .env ]; then
        cp config/env.example .env
        echo "✅ Created .env file from example"
        echo "⚠️  Please edit .env with your configuration"
    else
        echo "✅ .env file already exists"
    fi
    echo ""
}

# Start services
start_services() {
    echo "Starting services with Docker Compose..."
    docker-compose up -d
    echo ""
    echo "✅ Services started successfully!"
    echo ""
}

# Wait for services
wait_for_services() {
    echo "Waiting for services to be ready..."
    sleep 10
    
    # Check backend health
    max_retries=30
    retry=0
    while [ $retry -lt $max_retries ]; do
        if curl -f http://localhost:8000/health &> /dev/null; then
            echo "✅ Backend is ready"
            break
        fi
        retry=$((retry+1))
        sleep 2
    done
    
    if [ $retry -eq $max_retries ]; then
        echo "⚠️  Backend health check timeout"
    fi
    echo ""
}

# Display information
display_info() {
    echo "🎉 SICO GRC Platform is running!"
    echo ""
    echo "Access the platform:"
    echo "  Frontend:     http://localhost:3000"
    echo "  Backend API:  http://localhost:8000"
    echo "  API Docs:     http://localhost:8000/api/docs"
    echo ""
    echo "Services:"
    echo "  PostgreSQL:   localhost:5432"
    echo "  Redis:        localhost:6379"
    echo "  Chroma DB:    localhost:8001"
    echo ""
    echo "To stop the platform:"
    echo "  docker-compose down"
    echo ""
    echo "To view logs:"
    echo "  docker-compose logs -f"
    echo ""
}

# Main execution
main() {
    check_prerequisites
    setup_environment
    start_services
    wait_for_services
    display_info
}

main
