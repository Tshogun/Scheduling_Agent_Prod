#!/bin/bash
# scripts/generate-proto.sh

set -e

PROTO_DIR="shared/proto"
GO_OUT_DIR="backend/services/go-orchestrator/internal/proto"
PYTHON_OUT_DIR="backend/services/python-services/proto"

echo "Generating protobuf files..."

# Create output directories
mkdir -p $GO_OUT_DIR
mkdir -p $PYTHON_OUT_DIR

# Generate Go files
echo "Generating Go protobuf files..."
protoc \
    --go_out=$GO_OUT_DIR \
    --go_opt=paths=source_relative \
    --go-grpc_out=$GO_OUT_DIR \
    --go-grpc_opt=paths=source_relative \
    --proto_path=$PROTO_DIR \
    $PROTO_DIR/*.proto

# Generate Python files
echo "Generating Python protobuf files..."
python -m grpc_tools.protoc \
    --python_out=$PYTHON_OUT_DIR \
    --grpc_python_out=$PYTHON_OUT_DIR \
    --proto_path=$PROTO_DIR \
    $PROTO_DIR/*.proto

echo "Proto generation complete!"
