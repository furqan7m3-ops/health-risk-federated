"""
Automated Re-training Pipeline
Triggers re-training when drift is detected or on schedule
"""
import os
import sys
import mlflow
import mlflow.sklearn
from datetime import datetime
import argparse
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../part1-data-model'))
from federated_learning.drift_detector import DriftMonitor
from data_simulation.wearables import WearableSimulator
from data_simulation.air_quality import EnvironmentalSimulator
import pandas as pd

MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000")
DRIFT_THRESHOLD = float(os.getenv("DRIFT_THRESHOLD", "0.5"))

def check_drift_and_retrain(
    reference_date: str,
    current_date: str,
    node_id: str = "hospital_01",
    trigger_retraining: bool = True
):
    """
    Check for data drift and trigger re-training if needed
    
    Args:
        reference_date: Reference data date (YYYY-MM-DD)
        current_date: Current data date (YYYY-MM-DD)
        node_id: Node identifier
        trigger_retraining: Whether to trigger retraining if drift detected
    """
    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
    mlflow.set_experiment("federated_health_risk")
    
    with mlflow.start_run(run_name=f"drift_check_{datetime.now().strftime('%Y%m%d_%H%M%S')}"):
        # Generate reference data
        print(f"📊 Generating reference data for {reference_date}...")
        wear_sim = WearableSimulator(num_patients=500)
        env_sim = EnvironmentalSimulator(num_sensors=20)
        
        ref_health = wear_sim.generate_daily_data(reference_date, node_id)
        ref_env = env_sim.generate_sensor_data(node_id)
        ref_merged = ref_health.merge(
            ref_env.groupby('node_id').mean().reset_index(),
            on='node_id',
            how='left'
        ).fillna(0)
        
        # Generate current data
        print(f"📊 Generating current data for {current_date}...")
        curr_health = wear_sim.generate_daily_data(current_date, node_id)
        curr_env = env_sim.generate_sensor_data(node_id)
        curr_merged = curr_health.merge(
            curr_env.groupby('node_id').mean().reset_index(),
            on='node_id',
            how='left'
        ).fillna(0)
        
        # Check drift
        print("🔍 Checking for data drift...")
        monitor = DriftMonitor(ref_merged)
        drift_detected = monitor.check_drift(curr_merged, threshold=DRIFT_THRESHOLD)
        
        mlflow.log_param("drift_threshold", DRIFT_THRESHOLD)
        mlflow.log_param("drift_detected", drift_detected)
        mlflow.log_param("reference_date", reference_date)
        mlflow.log_param("current_date", current_date)
        
        if drift_detected and trigger_retraining:
            print("🚀 Drift detected! Triggering re-training...")
            trigger_retraining_pipeline()
        else:
            print("✅ No drift detected or retraining disabled")
        
        return drift_detected

def trigger_retraining_pipeline():
    """Trigger the federated learning training pipeline"""
    print("🔄 Starting federated learning re-training...")
    
    # This would typically trigger a Kubernetes job or CI/CD pipeline
    # For now, we'll log it and provide instructions
    mlflow.log_param("retraining_triggered", True)
    mlflow.log_param("retraining_timestamp", datetime.now().isoformat())
    
    # In a production setup, this would:
    # 1. Create a Kubernetes Job for training
    # 2. Or trigger a CI/CD pipeline
    # 3. Or call the training script directly
    
    print("📝 To trigger training, run:")
    print("   python part1-data-model/run_federated.py server")
    print("   python part1-data-model/run_federated.py client 01")
    print("   python part1-data-model/run_federated.py client 02")

def scheduled_retraining():
    """Scheduled retraining (e.g., weekly)"""
    print("⏰ Running scheduled re-training...")
    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
    mlflow.set_experiment("federated_health_risk")
    
    with mlflow.start_run(run_name=f"scheduled_retraining_{datetime.now().strftime('%Y%m%d_%H%M%S')}"):
        mlflow.log_param("retraining_type", "scheduled")
        mlflow.log_param("retraining_timestamp", datetime.now().isoformat())
        
        # Trigger training
        trigger_retraining_pipeline()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Re-training Pipeline")
    parser.add_argument("--mode", choices=["drift", "scheduled"], default="drift",
                       help="Retraining mode")
    parser.add_argument("--reference-date", type=str, default="2024-01-14",
                       help="Reference data date (YYYY-MM-DD)")
    parser.add_argument("--current-date", type=str, default=None,
                       help="Current data date (YYYY-MM-DD). Defaults to today.")
    parser.add_argument("--node-id", type=str, default="hospital_01",
                       help="Node identifier")
    parser.add_argument("--no-retrain", action="store_true",
                       help="Check drift but don't trigger retraining")
    
    args = parser.parse_args()
    
    if args.current_date is None:
        args.current_date = datetime.now().strftime("%Y-%m-%d")
    
    if args.mode == "drift":
        check_drift_and_retrain(
            args.reference_date,
            args.current_date,
            args.node_id,
            trigger_retraining=not args.no_retrain
        )
    elif args.mode == "scheduled":
        scheduled_retraining()

