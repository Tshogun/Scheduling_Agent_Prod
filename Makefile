# Makefile for easier development
# Place this in your project root as 'Makefile'

.PHONY: proto dev-go dev-python dev-frontend install-deps

# Generate protobuf files
proto:
	@echo "Generating protobuf files..."
	@bash scripts/generate-proto.sh

# Install development dependencies
install-deps:
	@echo "Installing Go dependencies..."
	cd backend/services/go-orchestrator && go mod tidy
	@echo "Installing Python dependencies..."
	cd backend/services/python-services && pip install -r requirements.txt
	@echo "Installing Frontend dependencies..."
	cd frontend && npm install

# Run services individually
dev-go:
	cd backend/services/go-orchestrator && go run main.go

dev-python:
	cd backend/services/python-services && uvicorn main:app --reload --port 8000

dev-frontend:
	cd frontend && npm run dev

# Run all services (requires terminal multiplexer or separate terminals)
dev-all:
	@echo "Run these commands in separate terminals:"
	@echo "make dev-go"
	@echo "make dev-python" 
	@echo "make dev-frontend"