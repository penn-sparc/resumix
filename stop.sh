#!/bin/bash

# RESUMIX Stop Script
echo "🛑 Stopping RESUMIX - AI Resume Helper"
echo "====================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to check if Docker is available
check_docker() {
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}❌ Docker is not installed or not available.${NC}"
        exit 1
    fi
}

# Function to check if Docker Compose is available
check_docker_compose() {
    if command -v docker-compose &> /dev/null; then
        COMPOSE_CMD="docker-compose"
    elif docker compose version &> /dev/null; then
        COMPOSE_CMD="docker compose"
    else
        COMPOSE_CMD=""
    fi
}

# Function to stop Docker Compose
stop_compose() {
    echo "🔄 Stopping with Docker Compose..."
    if $COMPOSE_CMD down; then
        echo -e "${GREEN}✅ Docker Compose containers stopped successfully${NC}"
        return 0
    else
        echo -e "${YELLOW}⚠️  Docker Compose stop failed, trying individual containers...${NC}"
        return 1
    fi
}

# Function to stop individual Docker containers
stop_containers() {
    echo "🔄 Stopping individual Docker containers..."
    
    # List of possible container names
    CONTAINERS=("resumix-container" "resumix-app" "resumix")
    
    STOPPED_ANY=false
    
    for container in "${CONTAINERS[@]}"; do
        if docker ps -q -f name=$container | grep -q .; then
            echo "🛑 Stopping container: $container"
            if docker stop $container; then
                echo -e "${GREEN}✅ Container $container stopped${NC}"
                STOPPED_ANY=true
                
                # Ask if user wants to remove the container
                read -p "🗑️  Remove container $container? (y/n): " -n 1 -r
                echo
                if [[ $REPLY =~ ^[Yy]$ ]]; then
                    if docker rm $container; then
                        echo -e "${GREEN}✅ Container $container removed${NC}"
                    else
                        echo -e "${YELLOW}⚠️  Failed to remove container $container${NC}"
                    fi
                fi
            else
                echo -e "${RED}❌ Failed to stop container $container${NC}"
            fi
        fi
    done
    
    if [ "$STOPPED_ANY" = false ]; then
        echo -e "${YELLOW}ℹ️  No RESUMIX containers found running${NC}"
    fi
}

# Function to clean up resources
cleanup_resources() {
    echo ""
    read -p "🧹 Clean up Docker resources? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "🧹 Cleaning up Docker resources..."
        
        # Remove stopped containers
        if docker container prune -f &>/dev/null; then
            echo -e "${GREEN}✅ Removed stopped containers${NC}"
        fi
        
        # Remove unused networks
        if docker network prune -f &>/dev/null; then
            echo -e "${GREEN}✅ Removed unused networks${NC}"
        fi
        
        # Ask about images
        read -p "🗑️  Remove RESUMIX Docker images? (y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            if docker images -q resumix | xargs -r docker rmi; then
                echo -e "${GREEN}✅ Removed RESUMIX images${NC}"
            else
                echo -e "${YELLOW}⚠️  No RESUMIX images found or failed to remove${NC}"
            fi
        fi
        
        # Ask about volumes
        read -p "🗑️  Remove Docker volumes? (y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            if docker volume prune -f &>/dev/null; then
                echo -e "${GREEN}✅ Removed unused volumes${NC}"
            fi
        fi
    fi
}

# Function to show status after stopping
show_status() {
    echo ""
    echo "📊 Current Docker Status:"
    echo "=========================="
    
    # Show running containers
    RUNNING_CONTAINERS=$(docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep -E "(resumix|RESUMIX)" || echo "No RESUMIX containers running")
    echo "🐳 Running Containers:"
    echo "$RUNNING_CONTAINERS"
    
    echo ""
    
    # Show available images
    IMAGES=$(docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}" | grep -E "(resumix|RESUMIX)" || echo "No RESUMIX images found")
    echo "💿 Available Images:"
    echo "$IMAGES"
}

# Main execution
main() {
    check_docker
    check_docker_compose
    
    echo "🔍 Detecting RESUMIX containers..."
    
    # Try Docker Compose first if available
    if [ -n "$COMPOSE_CMD" ] && [ -f "docker-compose.yml" ]; then
        echo "📋 Found docker-compose.yml"
        if ! stop_compose; then
            stop_containers
        fi
    else
        echo "📋 No docker-compose.yml found or Docker Compose not available"
        stop_containers
    fi
    
    # Optional cleanup
    cleanup_resources
    
    # Show final status
    show_status
    
    echo ""
    echo -e "${GREEN}🎉 RESUMIX shutdown complete!${NC}"
    echo "====================================="
    echo "📝 To start again: ./start.sh"
    echo "🔧 To rebuild: docker-compose build"
    echo "📊 Check status: docker ps"
}

# Handle command line arguments
case "${1:-}" in
    --help|-h)
        echo "RESUMIX Stop Script"
        echo ""
        echo "Usage: $0 [options]"
        echo ""
        echo "Options:"
        echo "  --help, -h     Show this help message"
        echo "  --force, -f    Force stop without prompts"
        echo "  --clean, -c    Stop and clean up all resources"
        echo ""
        echo "Examples:"
        echo "  $0              # Interactive stop"
        echo "  $0 --force      # Force stop without prompts"
        echo "  $0 --clean      # Stop and clean everything"
        exit 0
        ;;
    --force|-f)
        echo "🚀 Force stopping RESUMIX..."
        check_docker
        check_docker_compose
        
        if [ -n "$COMPOSE_CMD" ] && [ -f "docker-compose.yml" ]; then
            $COMPOSE_CMD down -v --remove-orphans
        fi
        
        # Force stop all resumix containers
        docker stop $(docker ps -q -f name=resumix) 2>/dev/null || true
        docker rm $(docker ps -aq -f name=resumix) 2>/dev/null || true
        
        echo -e "${GREEN}✅ Force stop completed${NC}"
        exit 0
        ;;
    --clean|-c)
        echo "🧹 Stopping and cleaning RESUMIX..."
        check_docker
        check_docker_compose
        
        # Stop everything
        if [ -n "$COMPOSE_CMD" ] && [ -f "docker-compose.yml" ]; then
            $COMPOSE_CMD down -v --remove-orphans --rmi all
        fi
        
        # Clean up containers, images, and volumes
        docker stop $(docker ps -q -f name=resumix) 2>/dev/null || true
        docker rm $(docker ps -aq -f name=resumix) 2>/dev/null || true
        docker rmi $(docker images -q resumix) 2>/dev/null || true
        docker volume prune -f
        docker container prune -f
        docker network prune -f
        
        echo -e "${GREEN}✅ Clean stop completed${NC}"
        exit 0
        ;;
    "")
        # No arguments, run interactive mode
        main
        ;;
    *)
        echo -e "${RED}❌ Unknown option: $1${NC}"
        echo "Use --help for usage information"
        exit 1
        ;;
esac
