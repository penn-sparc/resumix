#!/bin/bash

# RESUMIX Restart Script
echo "🔄 Restarting RESUMIX - AI Resume Helper"
echo "========================================"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to check if scripts exist
check_scripts() {
    if [ ! -f "./stop.sh" ]; then
        echo "❌ stop.sh not found in current directory"
        exit 1
    fi
    
    if [ ! -f "./start.sh" ]; then
        echo "❌ start.sh not found in current directory"
        exit 1
    fi
}

# Function to restart with Docker Compose
restart_compose() {
    echo "🔄 Restarting with Docker Compose..."
    
    if command -v docker-compose &> /dev/null; then
        COMPOSE_CMD="docker-compose"
    elif docker compose version &> /dev/null; then
        COMPOSE_CMD="docker compose"
    else
        echo -e "${YELLOW}⚠️  Docker Compose not available, using manual restart...${NC}"
        return 1
    fi
    
    if [ -f "docker-compose.yml" ]; then
        echo "📋 Using docker-compose.yml"
        $COMPOSE_CMD down
        $COMPOSE_CMD up -d --build
        return 0
    else
        return 1
    fi
}

# Function to restart manually
restart_manual() {
    echo "🔄 Manual restart process..."
    
    echo "1️⃣  Stopping RESUMIX..."
    ./stop.sh --force
    
    echo ""
    echo "2️⃣  Starting RESUMIX..."
    ./start.sh
}

# Main execution
main() {
    check_scripts
    
    echo "🔍 Detecting restart method..."
    
    # Try Docker Compose restart first
    if ! restart_compose; then
        echo -e "${YELLOW}📋 Docker Compose restart failed, using manual method...${NC}"
        restart_manual
    fi
    
    echo ""
    echo -e "${GREEN}🎉 RESUMIX restart complete!${NC}"
    echo "========================================"
    echo "📱 Frontend: http://localhost:8501"
    echo "🔧 Backend API: http://localhost:8000"
    echo "📊 Check status: docker ps"
    echo "📝 View logs: docker logs resumix-container"
}

# Handle command line arguments
case "${1:-}" in
    --help|-h)
        echo "RESUMIX Restart Script"
        echo ""
        echo "Usage: $0 [options]"
        echo ""
        echo "Options:"
        echo "  --help, -h     Show this help message"
        echo "  --build, -b    Rebuild images before restarting"
        echo "  --clean, -c    Clean restart (remove everything first)"
        echo ""
        echo "Examples:"
        echo "  $0              # Normal restart"
        echo "  $0 --build      # Rebuild and restart"
        echo "  $0 --clean      # Clean restart"
        exit 0
        ;;
    --build|-b)
        echo "🔨 Rebuild and restart RESUMIX..."
        check_scripts
        
        ./stop.sh --force
        
        # Rebuild images
        if [ -f "docker-compose.yml" ]; then
            if command -v docker-compose &> /dev/null; then
                docker-compose build --no-cache
                docker-compose up -d
            elif docker compose version &> /dev/null; then
                docker compose build --no-cache
                docker compose up -d
            else
                docker build --no-cache -t resumix .
                ./start.sh
            fi
        else
            docker build --no-cache -t resumix .
            ./start.sh
        fi
        
        echo -e "${GREEN}✅ Rebuild and restart completed${NC}"
        exit 0
        ;;
    --clean|-c)
        echo "🧹 Clean restart RESUMIX..."
        check_scripts
        
        ./stop.sh --clean
        ./start.sh
        
        echo -e "${GREEN}✅ Clean restart completed${NC}"
        exit 0
        ;;
    "")
        # No arguments, run normal restart
        main
        ;;
    *)
        echo "❌ Unknown option: $1"
        echo "Use --help for usage information"
        exit 1
        ;;
esac
