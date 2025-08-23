#!/bin/bash
# scripts/dev-start.sh

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🚀 Starting Local Development Environment${NC}"

# Check if .env exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠️  Creating .env file from template...${NC}"
    cp .env.example .env
    echo -e "${YELLOW}📝 Please edit .env with your actual values${NC}"
fi

# Load environment variables
set -a
source .env
set +a

# Function to check if a service is running
check_service() {
    local url=$1
    local name=$2
    if curl -s -f "$url" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ $name is running${NC}"
        return 0
    else
        echo -e "${RED}✗ $name is not running${NC}"
        return 1
    fi
}

# Check RabbitMQ
echo -e "\n${YELLOW}🐰 Checking RabbitMQ...${NC}"
if ! check_service "http://localhost:15672" "RabbitMQ Management UI"; then
    echo -e "${YELLOW}Starting RabbitMQ...${NC}"
    if command -v brew &> /dev/null; then
        brew services start rabbitmq
    elif command -v systemctl &> /dev/null; then
        sudo systemctl start rabbitmq-server
    else
        echo -e "${RED}Please start RabbitMQ manually${NC}"
        echo "Visit: https://www.rabbitmq.com/download.html"
    fi
    sleep 3
fi

# Generate protobuf files
echo -e "\n${YELLOW}🔧 Generating protobuf files...${NC}"
if [ -f "scripts/generate-proto.sh" ]; then
    bash scripts/generate-proto.sh
else
    echo -e "${RED}Proto generation script not found${NC}"
fi

# Install dependencies
echo -e "\n${YELLOW}📦 Installing dependencies...${NC}"

# Go dependencies
if [ -d "backend/services/go-orchestrator" ]; then
    echo "Installing Go dependencies..."
    cd backend/services/go-orchestrator
    go mod tidy
    cd ../../..
fi

# Python dependencies
if [ -d "backend/services/python-services" ]; then
    echo "Installing Python dependencies..."
    cd backend/services/python-services
    pip install -r requirements.txt
    cd ../../..
fi

# Frontend dependencies
if [ -d "frontend" ]; then
    echo "Installing Frontend dependencies..."
    cd frontend
    npm install
    cd ..
fi

echo -e "\n${GREEN}✅ Setup complete!${NC}"
echo -e "\n${BLUE}🎯 To start development, run these commands in separate terminals:${NC}"
echo -e "  ${YELLOW}Terminal 1:${NC} make dev-python"
echo -e "  ${YELLOW}Terminal 2:${NC} make dev-go" 
echo -e "  ${YELLOW}Terminal 3:${NC} make dev-frontend"
echo -e "\n${BLUE}🔗 Service URLs:${NC}"
echo -e "  Frontend: ${GREEN}http://localhost:3000${NC}"
echo -e "  Go API: ${GREEN}http://localhost:8080${NC}"
echo -e "  Python API: ${GREEN}http://localhost:8000${NC}"
echo -e "  RabbitMQ UI: ${GREEN}http://localhost:15672${NC} (guest/guest)"
echo -e "\n${BLUE}🧪 Test the setup:${NC}"
echo -e "  ${YELLOW}bash scripts/test-services.sh${NC}"
