# scripts/dev-watch.sh
# Alternative: Run all services with process monitoring
#!/bin/bash

trap 'kill 0' EXIT

# Start services in background
echo "Starting Python service..."
cd backend/services/python-services && py -3.13 main.py &

echo "Starting Go service..."
cd backend/services/go-orchestrator && go run main.go &

echo "Starting Frontend..."
cd frontend && npm run dev &

# Wait for any service to exit
wait