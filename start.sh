#!/bin/bash

# RESUMIX Startup Script
echo "🚀 Starting RESUMIX - AI Resume Helper"
echo "=================================="

# Function to check if Docker is installed
check_docker() {
    if ! command -v docker &> /dev/null; then
        echo "❌ Docker is not installed. Please install Docker first."
        echo "Visit: https://docs.docker.com/get-docker/"
        exit 1
    fi
    echo "✅ Docker is available"
}

# Function to check if Docker Compose is available
check_docker_compose() {
    if command -v docker-compose &> /dev/null; then
        COMPOSE_CMD="docker-compose"
    elif docker compose version &> /dev/null; then
        COMPOSE_CMD="docker compose"
    else
        echo "❌ Docker Compose is not available. Using Docker directly."
        COMPOSE_CMD=""
    fi
    echo "✅ Docker Compose: $COMPOSE_CMD"
}

# Check dependencies
check_docker
check_docker_compose

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p uploads logs

# Build and start the application
echo "🔨 Building and starting RESUMIX..."

if [ -n "$COMPOSE_CMD" ]; then
    # Use Docker Compose if available
    echo "Using Docker Compose..."
    $COMPOSE_CMD down 2>/dev/null || true
    $COMPOSE_CMD build
    $COMPOSE_CMD up -d
else
    # Use Docker directly
    echo "Using Docker directly..."
    docker stop resumix-container 2>/dev/null || true
    docker rm resumix-container 2>/dev/null || true
    docker build -t resumix .
    docker run -d -p 8501:8501 -p 8000:8000 --name resumix-container \
        -v $(pwd)/uploads:/app/uploads \
        -v $(pwd)/logs:/app/logs \
        resumix
fi

echo ""
echo "🎉 RESUMIX is starting up!"
echo "=================================="
echo "📱 Frontend (Streamlit): http://localhost:8501"
echo "🔧 Backend API (FastAPI): http://localhost:8000"
echo ""
echo "⏳ Please wait a few seconds for the services to initialize..."
echo ""
echo "To check status: docker ps"
echo "To view logs:    docker logs resumix-container"
echo "To stop:         docker stop resumix-container"
echo ""
echo "🚀 Happy resume building!"
