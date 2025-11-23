# MLOps Scripts

Helper scripts for building, deploying, and managing the MLOps pipeline.

## Scripts

### `build-images.sh`
Builds all Docker images for the MLOps pipeline.

**Usage:**
```bash
./build-images.sh
```

### `deploy-k8s.sh`
Deploys the entire MLOps pipeline to Kubernetes.

**Prerequisites:**
- kubectl configured
- Kubernetes cluster running

**Usage:**
```bash
./deploy-k8s.sh
```

### `run-local.sh`
Runs the MLOps pipeline locally using Docker Compose.

**Usage:**
```bash
./run-local.sh
```

### `trigger-retraining.sh`
Triggers the re-training pipeline with drift detection.

**Usage:**
```bash
# Drift detection mode
./trigger-retraining.sh drift [reference_date] [current_date] [node_id]

# Scheduled retraining
./trigger-retraining.sh scheduled
```

**Examples:**
```bash
# Check drift and retrain if needed
./trigger-retraining.sh drift 2024-01-14 2024-01-15 hospital_01

# Scheduled retraining
./trigger-retraining.sh scheduled
```

## Making Scripts Executable

On Unix-like systems, make scripts executable:

```bash
chmod +x part2-mlops/scripts/*.sh
```

On Windows, use Git Bash or WSL to run these scripts.

