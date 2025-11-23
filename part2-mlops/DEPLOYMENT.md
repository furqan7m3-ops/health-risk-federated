# Deployment Guide

This guide covers deploying the MLOps pipeline to different environments.

## Prerequisites

- Docker and Docker Compose installed
- Kubernetes cluster (for K8s deployment)
- kubectl configured (for K8s deployment)
- Python 3.10+ (for local development)

## Local Deployment (Docker Compose)

### Quick Start

```bash
cd part2-mlops/scripts
chmod +x *.sh  # On Unix/Mac
./run-local.sh
```

This will:
1. Build all Docker images
2. Start MLflow, server, clients, inference service, and Prometheus
3. Expose services on localhost

### Access Services

- **MLflow UI**: http://localhost:5000
- **Inference API**: http://localhost:8080
- **Prometheus**: http://localhost:9090
- **Federated Server**: localhost:5050 (internal)

### Stop Services

```bash
docker-compose -f part2-mlops/docker-compose.yml down
```

## Kubernetes Deployment

### Step 1: Build Images

```bash
./part2-mlops/scripts/build-images.sh
```

Or build individually:

```bash
# Server
docker build -t health-risk-federated:latest \
  -f part2-mlops/docker/Dockerfile.server .

# Client
docker build -t health-risk-federated-client:latest \
  -f part2-mlops/docker/Dockerfile.client .

# Inference
docker build -t health-risk-federated-inference:latest \
  -f part2-mlops/docker/Dockerfile.inference .
```

### Step 2: Push to Registry (Optional)

If using a container registry:

```bash
# Tag images
docker tag health-risk-federated:latest your-registry/health-risk-federated:latest
docker tag health-risk-federated-inference:latest your-registry/health-risk-federated-inference:latest

# Push
docker push your-registry/health-risk-federated:latest
docker push your-registry/health-risk-federated-inference:latest
```

Update Kubernetes manifests to use registry images.

### Step 3: Deploy to Kubernetes

```bash
./part2-mlops/scripts/deploy-k8s.sh
```

Or manually:

```bash
# Create namespace
kubectl apply -f part2-mlops/k8s/namespace.yaml

# Apply configuration
kubectl apply -f part2-mlops/k8s/configmap.yaml

# Deploy services
kubectl apply -f part2-mlops/k8s/mlflow-deployment.yaml
kubectl apply -f part2-mlops/k8s/federated-server-deployment.yaml
kubectl apply -f part2-mlops/k8s/federated-client-deployment.yaml
kubectl apply -f part2-mlops/k8s/inference-deployment.yaml
kubectl apply -f part2-mlops/k8s/prometheus-deployment.yaml

# Deploy scheduled retraining
kubectl apply -f part2-mlops/k8s/cronjob-retraining.yaml
```

### Step 4: Verify Deployment

```bash
# Check all resources
kubectl get all -n health-risk-mlops

# Check pod status
kubectl get pods -n health-risk-mlops

# View logs
kubectl logs -f deployment/federated-server -n health-risk-mlops
kubectl logs -f deployment/inference-service -n health-risk-mlops
```

### Step 5: Access Services

Get service endpoints:

```bash
# MLflow
kubectl port-forward svc/mlflow-service 5000:5000 -n health-risk-mlops

# Inference Service (if LoadBalancer)
kubectl get svc inference-service -n health-risk-mlops

# Prometheus
kubectl port-forward svc/prometheus-service 9090:9090 -n health-risk-mlops
```

## CI/CD Deployment

The GitHub Actions workflow (`.github/workflows/mlops-ci-cd.yml`) automatically:

1. **On Push to `develop`**: Deploys to staging
2. **On Push to `main`**: Builds images (manual deployment)
3. **Scheduled**: Monitors for data drift every 6 hours

### Manual Training Trigger

In GitHub Actions, use "Run workflow" and select "Trigger training pipeline".

## Environment Configuration

### ConfigMap Values

Edit `part2-mlops/k8s/configmap.yaml` to change:

- `MLFLOW_TRACKING_URI`: MLflow server URL
- `DRIFT_THRESHOLD`: Drift detection threshold (0.0-1.0)
- `NUM_ROUNDS`: Federated learning rounds
- `MIN_CLIENTS`: Minimum clients required

### Environment Variables

Key variables for containers:

- `MLFLOW_TRACKING_URI`: MLflow tracking server
- `SERVER_ADDRESS`: Federated server address (for clients)
- `MODEL_VERSION`: Model version to load
- `DRIFT_THRESHOLD`: Drift detection threshold

## Scaling

### Scale Inference Service

```bash
kubectl scale deployment/inference-service --replicas=5 -n health-risk-mlops
```

### Scale Clients

```bash
kubectl scale deployment/federated-client-01 --replicas=3 -n health-risk-mlops
```

## Monitoring

### View MLflow Experiments

1. Port-forward MLflow: `kubectl port-forward svc/mlflow-service 5000:5000 -n health-risk-mlops`
2. Open http://localhost:5000
3. Navigate to experiments and models

### Prometheus Metrics

1. Port-forward Prometheus: `kubectl port-forward svc/prometheus-service 9090:9090 -n health-risk-mlops`
2. Open http://localhost:9090
3. Query metrics (e.g., `predictions_total`)

### Application Logs

```bash
# Server logs
kubectl logs -f deployment/federated-server -n health-risk-mlops

# Client logs
kubectl logs -f deployment/federated-client-01 -n health-risk-mlops

# Inference logs
kubectl logs -f deployment/inference-service -n health-risk-mlops
```

## Troubleshooting

### Pods Not Starting

```bash
# Check pod status
kubectl describe pod <pod-name> -n health-risk-mlops

# Check events
kubectl get events -n health-risk-mlops --sort-by='.lastTimestamp'
```

### Image Pull Errors

- Ensure images are built: `./part2-mlops/scripts/build-images.sh`
- For local development, use `imagePullPolicy: Never` in manifests
- For production, push to registry and update image names

### Connection Issues

- Verify services are running: `kubectl get svc -n health-risk-mlops`
- Check ConfigMap values match service names
- Verify network policies allow communication

### Model Loading Issues

- Ensure MLflow is accessible
- Check `MLFLOW_TRACKING_URI` environment variable
- Verify model is registered in MLflow

## Updating Deployment

### Update Code

1. Make code changes
2. Rebuild images: `./part2-mlops/scripts/build-images.sh`
3. Update deployment:

```bash
# Update image in deployment
kubectl set image deployment/inference-service \
  inference=health-risk-federated-inference:latest \
  -n health-risk-mlops

# Rollout update
kubectl rollout status deployment/inference-service -n health-risk-mlops
```

### Update Configuration

1. Edit `part2-mlops/k8s/configmap.yaml`
2. Apply: `kubectl apply -f part2-mlops/k8s/configmap.yaml`
3. Restart pods: `kubectl rollout restart deployment/<deployment-name> -n health-risk-mlops`

## Cleanup

### Remove Kubernetes Deployment

```bash
kubectl delete namespace health-risk-mlops
```

### Remove Docker Containers

```bash
docker-compose -f part2-mlops/docker-compose.yml down -v
```

## Production Considerations

1. **Use Container Registry**: Push images to registry (Docker Hub, GCR, ECR, etc.)
2. **Update Image Pull Policy**: Change to `Always` or `IfNotPresent`
3. **Resource Limits**: Adjust based on workload
4. **Persistent Storage**: Ensure MLflow PVC has adequate storage
5. **Network Policies**: Implement network policies for security
6. **Secrets Management**: Use Kubernetes Secrets for sensitive data
7. **Monitoring**: Set up alerting in Prometheus
8. **Backup**: Regular backups of MLflow data and models

