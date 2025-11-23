# Part 2: MLOps Pipeline

This directory contains the complete MLOps infrastructure for the Health Risk Federated Learning project.

## 🏗️ Architecture

The MLOps pipeline includes:

- **Docker Containers**: Server, clients, and inference service
- **Kubernetes Deployments**: Production-ready orchestration
- **CI/CD Pipeline**: Automated testing, building, and deployment
- **Monitoring**: Prometheus metrics and MLflow tracking
- **Automated Re-training**: Drift detection and scheduled retraining

## 📁 Directory Structure

```
part2-mlops/
├── docker/              # Dockerfiles and configurations
│   ├── Dockerfile.server
│   ├── Dockerfile.client
│   ├── Dockerfile.inference
│   └── prometheus/
│       └── prometheus.yml
├── k8s/                 # Kubernetes manifests
│   ├── namespace.yaml
│   ├── configmap.yaml
│   ├── mlflow-deployment.yaml
│   ├── federated-server-deployment.yaml
│   ├── federated-client-deployment.yaml
│   ├── inference-deployment.yaml
│   ├── prometheus-deployment.yaml
│   ├── retraining-job.yaml
│   └── cronjob-retraining.yaml
├── mlops/               # MLOps utilities
│   ├── inference_server.py
│   └── retraining_pipeline.py
├── scripts/             # Helper scripts
│   ├── build-images.sh
│   ├── deploy-k8s.sh
│   ├── run-local.sh
│   └── trigger-retraining.sh
├── docker-compose.yml   # Local development setup
└── README.md
```

## 🚀 Quick Start

### Local Development with Docker Compose

1. **Build and start all services:**
   ```bash
   cd part2-mlops/scripts
   chmod +x *.sh
   ./run-local.sh
   ```

2. **Access services:**
   - MLflow UI: http://localhost:5000
   - Inference API: http://localhost:8080
   - Prometheus: http://localhost:9090

3. **Stop services:**
   ```bash
   docker-compose -f part2-mlops/docker-compose.yml down
   ```

### Kubernetes Deployment

1. **Build Docker images:**
   ```bash
   ./part2-mlops/scripts/build-images.sh
   ```

2. **Deploy to Kubernetes:**
   ```bash
   ./part2-mlops/scripts/deploy-k8s.sh
   ```

3. **Check deployment status:**
   ```bash
   kubectl get all -n health-risk-mlops
   ```

4. **View logs:**
   ```bash
   kubectl logs -f deployment/federated-server -n health-risk-mlops
   kubectl logs -f deployment/inference-service -n health-risk-mlops
   ```

## 🔧 Components

### 1. Docker Images

- **Server**: Federated learning server (Flower)
- **Client**: Federated learning clients
- **Inference**: FastAPI service for model predictions

### 2. Kubernetes Resources

- **Namespace**: `health-risk-mlops`
- **ConfigMap**: Configuration for all services
- **Deployments**: Server, clients, MLflow, inference, Prometheus
- **Services**: ClusterIP and LoadBalancer services
- **CronJob**: Scheduled retraining (weekly)

### 3. CI/CD Pipeline

GitHub Actions workflow (`.github/workflows/mlops-ci-cd.yml`) includes:

- **Lint and Test**: Code quality checks
- **Build Images**: Docker image building
- **Deploy Staging**: Automatic deployment to staging
- **Trigger Training**: Manual training trigger
- **Monitor Drift**: Scheduled drift detection (every 6 hours)

### 4. Monitoring

- **MLflow**: Experiment tracking and model registry
- **Prometheus**: Metrics collection
- **Health Checks**: Liveness and readiness probes

### 5. Automated Re-training

The retraining pipeline (`mlops/retraining_pipeline.py`) supports:

- **Drift Detection**: Automatic retraining when drift is detected
- **Scheduled Retraining**: Weekly retraining via CronJob
- **Manual Trigger**: On-demand retraining

## 📊 Usage Examples

### Trigger Re-training

```bash
# Check for drift and retrain if needed
./part2-mlops/scripts/trigger-retraining.sh drift 2024-01-14 2024-01-15 hospital_01

# Scheduled retraining
./part2-mlops/scripts/trigger-retraining.sh scheduled
```

### Make Predictions

```bash
# Single prediction
curl -X POST http://localhost:8080/predict \
  -H "Content-Type: application/json" \
  -d '{
    "heart_rate": 75,
    "steps": 8000,
    "sleep_hours": 7.5,
    "respiratory_rate": 16,
    "body_temp": 98.6,
    "pm25": 15,
    "pm10": 25,
    "o3": 0.05,
    "no2": 0.02,
    "temperature": 72,
    "humidity": 50
  }'

# Health check
curl http://localhost:8080/health

# Metrics
curl http://localhost:8080/metrics
```

### View MLflow Experiments

1. Open MLflow UI: http://localhost:5000
2. Navigate to experiments
3. View metrics, parameters, and artifacts

## 🔐 Environment Variables

Key environment variables:

- `MLFLOW_TRACKING_URI`: MLflow server URL
- `DRIFT_THRESHOLD`: Drift detection threshold (default: 0.5)
- `SERVER_ADDRESS`: Federated server address
- `MODEL_VERSION`: Model version to load (default: "latest")

## 🛠️ Development

### Building Individual Images

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

### Testing Locally

```bash
# Run inference server locally
cd part2-mlops
python -m mlops.inference_server

# Run retraining pipeline
python -m mlops.retraining_pipeline --mode drift
```

## 📈 Monitoring and Observability

### Prometheus Metrics

- `predictions_total`: Total number of predictions
- `prediction_latency_seconds`: Prediction latency histogram
- Custom federated learning metrics via MLflow

### MLflow Tracking

- Experiment runs
- Model versions
- Metrics and parameters
- Model artifacts

## 🔄 Re-training Workflow

1. **Drift Detection**: Runs every 6 hours (via GitHub Actions)
2. **Drift Check**: Compares current data with reference data
3. **Threshold Check**: If drift score > threshold, trigger retraining
4. **Federated Training**: Start server and clients
5. **Model Registration**: Save new model to MLflow
6. **Model Deployment**: Update inference service with new model

## 🐛 Troubleshooting

### Docker Compose Issues

```bash
# Check logs
docker-compose -f part2-mlops/docker-compose.yml logs

# Restart services
docker-compose -f part2-mlops/docker-compose.yml restart
```

### Kubernetes Issues

```bash
# Check pod status
kubectl get pods -n health-risk-mlops

# Describe pod for details
kubectl describe pod <pod-name> -n health-risk-mlops

# Check events
kubectl get events -n health-risk-mlops --sort-by='.lastTimestamp'
```

### Model Loading Issues

- Ensure MLflow is running and accessible
- Check `MLFLOW_TRACKING_URI` environment variable
- Verify model is registered in MLflow model registry

## 📚 Additional Resources

- [Flower Documentation](https://flower.dev/)
- [MLflow Documentation](https://www.mlflow.org/docs/latest/index.html)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Prometheus Documentation](https://prometheus.io/docs/)

## 🤝 Contributing

When adding new features:

1. Update Dockerfiles if new dependencies are needed
2. Update Kubernetes manifests for new services
3. Add tests to CI/CD pipeline
4. Update this README

## 📝 License

See main project LICENSE file.

