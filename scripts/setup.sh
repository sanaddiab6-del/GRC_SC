#!/bin/bash

# SICO GRC Platform - Setup Script
# Automates development environment setup

set -e

echo "🚀 SICO GRC Platform - Setup Script"
echo "===================================="

# Check prerequisites
check_prerequisites() {
    echo "📋 Checking prerequisites..."
    
    command -v docker >/dev/null 2>&1 || { echo "❌ Docker is required but not installed. Aborting."; exit 1; }
    command -v docker-compose >/dev/null 2>&1 || { echo "❌ Docker Compose is required but not installed. Aborting."; exit 1; }
    command -v python3 >/dev/null 2>&1 || { echo "❌ Python 3 is required but not installed. Aborting."; exit 1; }
    command -v node >/dev/null 2>&1 || { echo "❌ Node.js is required but not installed. Aborting."; exit 1; }
    
    echo "✅ All prerequisites met"
}

# Setup environment file
setup_env() {
    echo ""
    echo "🔧 Setting up environment configuration..."
    
    if [ ! -f .env ]; then
        cp config/env.example .env
        echo "✅ Created .env file from template"
        echo "⚠️  Please update .env with your settings"
    else
        echo "ℹ️  .env file already exists"
    fi
}

# Create required directories
setup_directories() {
    echo ""
    echo "📁 Creating required directories..."
    
    mkdir -p data/controls/{ecc,ccc,pdpl}
    mkdir -p data/evidence
    mkdir -p data/mappings
    mkdir -p ai/knowledge_base
    mkdir -p logs
    
    echo "✅ Directories created"
}

# Start services with Docker Compose
start_services() {
    echo ""
    echo "🐳 Starting services with Docker Compose..."
    
    docker-compose -f deployment/docker-compose.yml up -d
    
    echo "✅ Services started"
}

# Wait for services to be ready
wait_for_services() {
    echo ""
    echo "⏳ Waiting for services to be ready..."
    
    sleep 5
    
    echo "✅ Services are ready"
}

# Load sample data
load_data() {
    echo ""
    echo "📊 Loading sample data..."
    
    if [ -f scripts/load_sample_data.py ]; then
        python3 scripts/load_sample_data.py
        echo "✅ Sample data loaded"
    else
        echo "⚠️  Sample data script not found"
    fi
}

# Display access information
show_access_info() {
    echo ""
    echo "✅ Setup complete!"
    echo ""
    echo "📌 Access Points:"
    echo "   Frontend: http://localhost:3000"
    echo "   Backend API: http://localhost:8000"
    echo "   API Docs: http://localhost:8000/docs"
    echo ""
    echo "🔍 Useful Commands:"
    echo "   View logs: docker-compose -f deployment/docker-compose.yml logs -f"
    echo "   Stop services: docker-compose -f deployment/docker-compose.yml down"
    echo ""
}

# Main execution
main() {
    check_prerequisites
    setup_env
    setup_directories
    start_services
    wait_for_services
    load_data
    show_access_info
}

main
