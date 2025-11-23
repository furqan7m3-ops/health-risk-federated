#!/bin/bash
# Build Docker images for MLOps pipeline

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

echo "🔨 Building Docker images..."

# Build server image
echo "📦 Building federated server image..."
docker build -t health-risk-federated:latest \
  -f "$PROJECT_ROOT/part2-mlops/docker/Dockerfile.server" \
  "$PROJECT_ROOT"

# Build client image
echo "📦 Building federated client image..."
docker build -t health-risk-federated-client:latest \
  -f "$PROJECT_ROOT/part2-mlops/docker/Dockerfile.client" \
  "$PROJECT_ROOT"

# Build inference image
echo "📦 Building inference service image..."
docker build -t health-risk-federated-inference:latest \
  -f "$PROJECT_ROOT/part2-mlops/docker/Dockerfile.inference" \
  "$PROJECT_ROOT"

echo "✅ All images built successfully!"
docker images | grep health-risk-federated

