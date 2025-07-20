#!/bin/bash

# RESUMIX Status Script
echo "📊 RESUMIX Status - AI Resume Helper"
echo "===================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to check if Docker is available
check_docker() {
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}❌ Docker is not installed or not available.${NC}"
        exit 1
    fi
}

# Function to check container status
check_containers() {
    echo -e "${BLUE}🐳 Container Status:${NC}"
    echo "===================="
    
    # Check for RESUMIX containers
    CONTAINERS=$(docker ps -a --filter "name=resumix" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}\t{{.Image}}")
    
    if [ -z "$CONTAINERS" ] || [ "$CONTAINERS" = "NAMES	STATUS	PORTS	IMAGE" ]; then
        echo -e "${YELLOW}ℹ️  No RESUMIX containers found${NC}"
        
        # Check if there are any containers with 'resumix' in the image name
        IMAGE_CONTAINERS=$(docker ps -a --filter "ancestor=resumix" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}\t{{.Image}}")
        if [ ! -z "$IMAGE_CONTAINERS" ] && [ "$IMAGE_CONTAINERS" != "NAMES	STATUS	PORTS	IMAGE" ]; then
            echo -e "${BLUE}Found containers with resumix image:${NC}"
            echo "$IMAGE_CONTAINERS"
        fi
    else
        echo "$CONTAINERS"
        
        # Check if containers are running
        RUNNING=$(docker ps --filter "name=resumix" --format "{{.Names}}")
        if [ ! -z "$RUNNING" ]; then
            echo -e "${GREEN}✅ Running containers: $RUNNING${NC}"
        else
            echo -e "${RED}❌ No RESUMIX containers are currently running${NC}"
        fi
    fi
    echo ""
}

# Function to check Docker images
check_images() {
    echo -e "${BLUE}💿 Docker Images:${NC}"
    echo "=================="
    
    IMAGES=$(docker images --filter "reference=resumix*" --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}\t{{.CreatedAt}}")
    
    if [ -z "$IMAGES" ] || [ "$IMAGES" = "REPOSITORY	TAG	SIZE	CREATED AT" ]; then
        echo -e "${YELLOW}ℹ️  No RESUMIX images found${NC}"
    else
        echo "$IMAGES"
    fi
    echo ""
}

# Function to check service connectivity
check_services() {
    echo -e "${BLUE}🌐 Service Connectivity:${NC}"
    echo "========================"
    
    # Check frontend (Streamlit)
    if curl -s -o /dev/null -w "%{http_code}" http://localhost:8501/ | grep -q "200"; then
        echo -e "${GREEN}✅ Frontend (Streamlit): http://localhost:8501 - ACCESSIBLE${NC}"
    else
        echo -e "${RED}❌ Frontend (Streamlit): http://localhost:8501 - NOT ACCESSIBLE${NC}"
    fi
    
    # Check backend (FastAPI)
    if curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/ 2>/dev/null | grep -q "200\|404"; then
        echo -e "${GREEN}✅ Backend (FastAPI): http://localhost:8000 - ACCESSIBLE${NC}"
    else
        echo -e "${RED}❌ Backend (FastAPI): http://localhost:8000 - NOT ACCESSIBLE${NC}"
    fi
    echo ""
}

# Function to check Docker Compose status
check_compose() {
    echo -e "${BLUE}📋 Docker Compose Status:${NC}"
    echo "=========================="
    
    if [ -f "docker-compose.yml" ]; then
        echo -e "${GREEN}✅ docker-compose.yml found${NC}"
        
        # Check if docker-compose command is available
        if command -v docker-compose &> /dev/null; then
            COMPOSE_CMD="docker-compose"
        elif docker compose version &> /dev/null; then
            COMPOSE_CMD="docker compose"
        else
            echo -e "${YELLOW}⚠️  Docker Compose not available${NC}"
            echo ""
            return
        fi
        
        # Show compose services status
        echo "Services status:"
        $COMPOSE_CMD ps 2>/dev/null || echo -e "${YELLOW}⚠️  No compose services running${NC}"
    else
        echo -e "${YELLOW}⚠️  docker-compose.yml not found${NC}"
    fi
    echo ""
}

# Function to show resource usage
check_resources() {
    echo -e "${BLUE}💻 Resource Usage:${NC}"
    echo "=================="
    
    # Get container resource usage
    CONTAINER_STATS=$(docker stats --no-stream --filter "name=resumix" --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}" 2>/dev/null)
    
    if [ ! -z "$CONTAINER_STATS" ] && [ "$CONTAINER_STATS" != "NAME	CPU %	MEM USAGE / LIMIT	NET I/O" ]; then
        echo "$CONTAINER_STATS"
    else
        echo -e "${YELLOW}ℹ️  No running RESUMIX containers to show stats${NC}"
    fi
    
    # Show disk usage
    echo ""
    echo "Docker disk usage:"
    docker system df 2>/dev/null | head -4
    echo ""
}

# Function to show recent logs
check_logs() {
    echo -e "${BLUE}📜 Recent Logs (last 10 lines):${NC}"
    echo "================================="
    
    # Find the main container
    MAIN_CONTAINER=$(docker ps --filter "name=resumix" --format "{{.Names}}" | head -1)
    
    if [ ! -z "$MAIN_CONTAINER" ]; then
        echo -e "${GREEN}Logs from: $MAIN_CONTAINER${NC}"
        docker logs --tail 10 "$MAIN_CONTAINER" 2>/dev/null || echo -e "${YELLOW}⚠️  Unable to fetch logs${NC}"
    else
        # Try to get logs from any resumix container (even stopped ones)
        CONTAINER=$(docker ps -a --filter "name=resumix" --format "{{.Names}}" | head -1)
        if [ ! -z "$CONTAINER" ]; then
            echo -e "${YELLOW}Logs from stopped container: $CONTAINER${NC}"
            docker logs --tail 10 "$CONTAINER" 2>/dev/null || echo -e "${YELLOW}⚠️  Unable to fetch logs${NC}"
        else
            echo -e "${YELLOW}ℹ️  No containers found for log inspection${NC}"
        fi
    fi
    echo ""
}

# Function to show configuration
check_config() {
    echo -e "${BLUE}⚙️  Configuration:${NC}"
    echo "=================="
    
    # Check main config file
    if [ -f "resumix/config/config.yaml" ]; then
        echo -e "${GREEN}✅ Main config found: resumix/config/config.yaml${NC}"
        
        # Show LLM configuration
        LLM_MODEL=$(grep "use_model:" resumix/config/config.yaml | awk '{print $2}' | tr -d '"')
        if [ ! -z "$LLM_MODEL" ]; then
            echo -e "${BLUE}🤖 LLM Model: $LLM_MODEL${NC}"
        fi
    else
        echo -e "${YELLOW}⚠️  Main config not found${NC}"
    fi
    
    # Check .env file
    if [ -f ".env" ]; then
        echo -e "${GREEN}✅ Environment file found: .env${NC}"
        
        # Count configured API keys (without showing them)
        API_KEYS=$(grep -E "^[A-Z_]+_API_KEY=" .env 2>/dev/null | wc -l)
        if [ $API_KEYS -gt 0 ]; then
            echo -e "${GREEN}🔑 Configured API keys: $API_KEYS${NC}"
        fi
    else
        echo -e "${YELLOW}⚠️  No .env file found${NC}"
    fi
    echo ""
}

# Function to show quick actions
show_actions() {
    echo -e "${BLUE}🚀 Quick Actions:${NC}"
    echo "================="
    echo "📝 View logs:     docker logs resumix-container"
    echo "🔄 Restart:       ./restart.sh"
    echo "🛑 Stop:          ./stop.sh" 
    echo "▶️  Start:         ./start.sh"
    echo "🔧 Shell access:  docker exec -it resumix-container bash"
    echo "📊 Live stats:    docker stats resumix-container"
    echo ""
}

# Main execution function
main() {
    check_docker
    check_containers
    check_images
    check_compose
    check_services
    check_resources
    check_config
    
    # Only show logs if requested or if there are issues
    if [ "${1:-}" = "--logs" ] || [ "${1:-}" = "-l" ]; then
        check_logs
    fi
    
    show_actions
    
    echo -e "${GREEN}📊 Status check complete!${NC}"
}

# Handle command line arguments
case "${1:-}" in
    --help|-h)
        echo "RESUMIX Status Script"
        echo ""
        echo "Usage: $0 [options]"
        echo ""
        echo "Options:"
        echo "  --help, -h     Show this help message"
        echo "  --logs, -l     Include recent logs in status"
        echo "  --watch, -w    Watch status continuously"
        echo "  --services, -s Show only service status"
        echo ""
        echo "Examples:"
        echo "  $0              # Show full status"
        echo "  $0 --logs       # Show status with logs"
        echo "  $0 --watch      # Watch status continuously"
        echo "  $0 --services   # Show only services"
        exit 0
        ;;
    --logs|-l)
        main --logs
        ;;
    --watch|-w)
        echo "👀 Watching RESUMIX status (Ctrl+C to stop)..."
        while true; do
            clear
            main
            sleep 5
        done
        ;;
    --services|-s)
        check_docker
        check_services
        ;;
    "")
        main
        ;;
    *)
        echo -e "${RED}❌ Unknown option: $1${NC}"
        echo "Use --help for usage information"
        exit 1
        ;;
esac
