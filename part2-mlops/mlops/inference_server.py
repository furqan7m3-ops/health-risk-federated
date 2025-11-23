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
        # Try to load from MLflow
        if MODEL_VERSION != "latest":
            model = mlflow.sklearn.load_model(f"models:/health_risk_model/{MODEL_VERSION}")
        else:
            # Load latest model from MLflow
            client = mlflow.tracking.MlflowClient()
            latest_version = client.get_latest_versions("health_risk_model", stages=["None"])[0]
            model = mlflow.sklearn.load_model(f"models:/health_risk_model/{latest_version.version}")
        print(f"✅ Loaded model from MLflow: {MODEL_VERSION}")
    except Exception as e:
        print(f"⚠️ Could not load from MLflow: {e}")
        # Fallback to local model if exists
        model_path = os.getenv("MODEL_PATH", "/app/models/health_risk_model.pkl")
        if os.path.exists(model_path):
            model = HealthRiskModel.load(model_path)
            print(f"✅ Loaded model from local file: {model_path}")
        else:
            # Initialize empty model (will fail on prediction until trained)
            model = HealthRiskModel()
            print("⚠️ No trained model found. Please train a model first.")
    
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
    uvicorn.run(app, host="0.0.0.0", port=8080)

