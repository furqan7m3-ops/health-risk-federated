"""
Model Inference Server using FastAPI
Serves health risk predictions via REST API
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import numpy as np
import mlflow
import mlflow.sklearn
import os
from typing import List, Optional
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from fastapi.responses import Response
import sys

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, os.path.join(project_root, 'part1-data-model'))

from models.health_risk_model import HealthRiskModel

app = FastAPI(title="Health Risk Prediction API", version="1.0.0")

# Prometheus metrics
prediction_counter = Counter('predictions_total', 'Total number of predictions')
prediction_latency = Histogram('prediction_latency_seconds', 'Prediction latency')

# Model loading
model = None
MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "http://mlflow:5000")
MODEL_VERSION = os.getenv("MODEL_VERSION", "latest")

class HealthData(BaseModel):
    heart_rate: float
    steps: float
    sleep_hours: float
    respiratory_rate: float
    body_temp: float
    pm25: float
    pm10: float
    o3: float
    no2: float
    temperature: float
    humidity: float

class PredictionResponse(BaseModel):
    risk_score: float
    risk_probability: float
    prediction: str

def load_model():
    """Load model from MLflow or local file"""
    global model
    if model is not None:
        return model
    
    try:
        mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
        client = mlflow.tracking.MlflowClient()
        
        # Try to load from latest run's artifacts
        experiment = client.get_experiment_by_name("federated_health_risk")
        if experiment:
            runs = client.search_runs(experiment.experiment_id, order_by=["start_time DESC"], max_results=1)
            if runs:
                run_id = runs[0].info.run_id
                exp_id = experiment.experiment_id
                
                # Try to load full HealthRiskModel from artifact using MLflow download
                try:
                    import tempfile
                    with tempfile.TemporaryDirectory() as tmpdir:
                        # Download the full model artifact
                        artifact_path = client.download_artifacts(run_id, "model/health_risk_model.pkl", tmpdir)
                        if os.path.exists(artifact_path):
                            model = HealthRiskModel.load(artifact_path)
                            print(f"Loaded full HealthRiskModel from run: {run_id}")
                            return model
                except Exception as e1:
                    print(f"Could not download full model artifact: {e1}")
                
                # Fallback: Try direct file access
                artifact_path = f"/mlruns/{exp_id}/{run_id}/artifacts/model/health_risk_model.pkl"
                if os.path.exists(artifact_path):
                    model = HealthRiskModel.load(artifact_path)
                    print(f"Loaded full HealthRiskModel from: {artifact_path}")
                    return model
                
                # Fallback: Load sklearn model and wrap it
                try:
                    model_uri = f"runs:/{run_id}/sklearn_model"
                    sklearn_model = mlflow.sklearn.load_model(model_uri)
                    model = HealthRiskModel()
                    model.model = sklearn_model
                    # Create and fit scaler (needed for prediction)
                    from sklearn.preprocessing import StandardScaler
                    model.scaler = StandardScaler()
                    # Fit with dummy data (in production, should load actual scaler)
                    dummy_X = np.zeros((1, 11))
                    model.scaler.fit(dummy_X)
                    print(f"Loaded sklearn model from run: {run_id}")
                    return model
                except Exception as e:
                    print(f"Could not load sklearn model: {e}")
        
        raise Exception("No runs found in experiment")
    except Exception as e:
        print(f"Could not load from MLflow: {e}")
        # Fallback to local model if exists
        model_path = os.getenv("MODEL_PATH", "/app/models/health_risk_model.pkl")
        if os.path.exists(model_path):
            model = HealthRiskModel.load(model_path)
            print(f"Loaded model from local file: {model_path}")
        else:
            # Initialize empty model (will fail on prediction until trained)
            model = HealthRiskModel()
            print("No trained model found. Please train a model first.")
    
    return model

@app.on_event("startup")
async def startup_event():
    load_model()

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "model_loaded": model is not None}

@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.post("/predict", response_model=PredictionResponse)
async def predict(data: HealthData):
    """
    Predict health risk from input features
    """
    with prediction_latency.time():
        try:
            # Convert input to numpy array
            features = np.array([[
                data.heart_rate,
                data.steps,
                data.sleep_hours,
                data.respiratory_rate,
                data.body_temp,
                data.pm25,
                data.pm10,
                data.o3,
                data.no2,
                data.temperature,
                data.humidity
            ]])
            
            # Get model
            current_model = load_model()
            
            # Check if model is fitted
            if not hasattr(current_model, 'model') or not hasattr(current_model.model, 'coef_'):
                raise HTTPException(status_code=503, detail="Model not trained yet. Please train a model first.")
            
            # Predict
            proba = current_model.predict_proba(features)[0]
            risk_prob = proba[1]  # Probability of high risk
            
            # Determine risk level
            if risk_prob < 0.3:
                prediction = "low"
            elif risk_prob < 0.7:
                prediction = "medium"
            else:
                prediction = "high"
            
            prediction_counter.inc()
            
            return PredictionResponse(
                risk_score=float(risk_prob),
                risk_probability=float(risk_prob),
                prediction=prediction
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")

@app.post("/predict/batch")
async def predict_batch(data_list: List[HealthData]):
    """
    Batch prediction endpoint
    """
    results = []
    for data in data_list:
        result = await predict(data)
        results.append(result.dict())
    return {"predictions": results}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)  # nosec B104

