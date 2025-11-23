#!/bin/bash
# Deploy MLOps pipeline to Kubernetes

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
K8S_DIR="$SCRIPT_DIR/../k8s"

echo "🚀 Deploying MLOps pipeline to Kubernetes..."

# Create namespace
echo "📦 Creating namespace..."
kubectl apply -f "$K8S_DIR/namespace.yaml"

# Apply ConfigMap
echo "⚙️  Applying configuration..."
kubectl apply -f "$K8S_DIR/configmap.yaml"

# Deploy MLflow
echo "📊 Deploying MLflow..."
kubectl apply -f "$K8S_DIR/mlflow-deployment.yaml"

# Wait for MLflow to be ready
echo "⏳ Waiting for MLflow to be ready..."
kubectl wait --for=condition=available --timeout=300s deployment/mlflow -n health-risk-mlops

# Deploy federated server
echo "🖥️  Deploying federated server..."
kubectl apply -f "$K8S_DIR/federated-server-deployment.yaml"

# Deploy federated clients
echo "👥 Deploying federated clients..."
kubectl apply -f "$K8S_DIR/federated-client-deployment.yaml"

# Deploy inference service
echo "🔮 Deploying inference service..."
kubectl apply -f "$K8S_DIR/inference-deployment.yaml"

# Deploy Prometheus
echo "📈 Deploying Prometheus..."
kubectl apply -f "$K8S_DIR/prometheus-deployment.yaml"

# Deploy CronJob for scheduled retraining
echo "⏰ Deploying scheduled retraining job..."
kubectl apply -f "$K8S_DIR/cronjob-retraining.yaml"

echo "✅ Deployment complete!"
echo ""
echo "📋 Check status with:"
echo "   kubectl get all -n health-risk-mlops"
echo ""
echo "🔍 View logs with:"
echo "   kubectl logs -f deployment/federated-server -n health-risk-mlops"
echo "   kubectl logs -f deployment/inference-service -n health-risk-mlops"

