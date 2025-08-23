#!/bin/bash
# scripts/test-services.sh

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Testing Local Services${NC}"

# Test Go Orchestrator Health
echo -e "\n${YELLOW}1. Testing Go Orchestrator Health...${NC}"
response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8080/health)
if [ "$response" = "200" ]; then
    echo -e "${GREEN}✓ Go Orchestrator is healthy${NC}"
    curl -s http://localhost:8080/health | jq .
else
    echo -e "${RED}✗ Go Orchestrator health check failed (HTTP $response)${NC}"
fi

# Test Python Service Health
echo -e "\n${YELLOW}2. Testing Python Service Health...${NC}"
response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health)
if [ "$response" = "200" ]; then
    echo -e "${GREEN}✓ Python Service is healthy${NC}"
    curl -s http://localhost:8000/health | jq .
else
    echo -e "${RED}✗ Python Service health check failed (HTTP $response)${NC}"
fi

# Test gRPC Communication via Go Orchestrator
echo -e "\n${YELLOW}3. Testing gRPC Communication (Go -> Python)...${NC}"
completion_response=$(curl -s -X POST http://localhost:8080/api/v1/completion \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Hello, how are you?",
    "model": "test-model",
    "max_tokens": 50
  }')

if echo "$completion_response" | jq -e .completion > /dev/null 2>&1; then
    echo -e "${GREEN}✓ gRPC completion working${NC}"
    echo "$completion_response" | jq .
else
    echo -e "${RED}✗ gRPC completion failed${NC}"
    echo "$completion_response"
fi

# Test Optimization (async job)
echo -e "\n${YELLOW}4. Testing Optimization Job...${NC}"
opt_response=$(curl -s -X POST http://localhost:8080/api/v1/optimize \
  -H "Content-Type: application/json" \
  -d '{
    "problem_type": "linear_programming",
    "constraints_json": "{\"constraint1\": \"x + y <= 10\"}",
    "objectives_json": "{\"maximize\": \"2x + 3y\"}",
    "timeout_seconds": 30
  }')

if echo "$opt_response" | jq -e .job_id > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Optimization job created${NC}"
    job_id=$(echo "$opt_response" | jq -r .job_id)
    echo "Job ID: $job_id"
    
    # Wait and check job status
    echo -e "\n${YELLOW}5. Checking job status...${NC}"
    sleep 3
    status_response=$(curl -s http://localhost:8080/api/v1/job/$job_id)
    echo "$status_response" | jq .
else
    echo -e "${RED}✗ Optimization job creation failed${NC}"
    echo "$opt_response"
fi

# Test RabbitMQ Management UI
echo -e "\n${YELLOW}6. Testing RabbitMQ Management UI...${NC}"
management_response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:15672)
if [ "$management_response" = "200" ]; then
    echo -e "${GREEN}✓ RabbitMQ Management UI accessible at http://localhost:15672${NC}"
    echo "  Login: guest/guest"
else
    echo -e "${RED}✗ RabbitMQ Management UI not accessible${NC}"
fi

echo -e "\n${YELLOW}Testing Complete!${NC}"
