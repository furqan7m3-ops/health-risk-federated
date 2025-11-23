#!/bin/bash
# Run MLOps pipeline locally with Docker Compose

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COMPOSE_FILE="$SCRIPT_DIR/../docker-compose.yml"

echo "🚀 Starting MLOps pipeline locally..."

# Build images first
echo "🔨 Building images..."
"$SCRIPT_DIR/build-images.sh"

# Start services
echo "📦 Starting services with Docker Compose..."
cd "$SCRIPT_DIR/../.."
docker-compose -f "$COMPOSE_FILE" up -d

echo "✅ Services started!"
echo ""
echo "📋 Services available at:"
echo "   MLflow UI: http://localhost:5000"
echo "   Inference API: http://localhost:8080"
echo "   Prometheus: http://localhost:9090"
echo ""
echo "🔍 View logs with:"
echo "   docker-compose -f $COMPOSE_FILE logs -f"
echo ""
echo "🛑 Stop services with:"
echo "   docker-compose -f $COMPOSE_FILE down"

