import flwr as fl
import numpy as np
from sklearn.metrics import roc_auc_score
import mlflow
from models.health_risk_model import HealthRiskModel
from flwr.common import Code, Status, ndarrays_to_parameters, parameters_to_ndarrays

class HealthRiskClient(fl.client.Client):
    def __init__(self, cid, train_loader, val_loader):
        self.cid = cid
        self.train_loader = train_loader
        self.val_loader = val_loader
        self.model = None
        print(f"🟢 Client {cid} initialized with {len(train_loader)} batches")
    
    def fit(self, ins):
        """Train on local data"""
        print(f"🔄 Client {self.cid} starting fit...")
        
        # Initialize model if needed
        if self.model is None:
            self.model = HealthRiskModel()
        
        # If server sent parameters, load them into local model
        try:
            recv_params = parameters_to_ndarrays(ins.parameters)
            if recv_params is not None and len(recv_params) > 0:
                print(f"⬇️ Client {self.cid} received {len(recv_params)} parameter arrays from server")
                self.model.set_parameters(recv_params)
        except Exception:  # nosec B110
            # If ins.parameters is None or malformed, ignore and continue training from local state
            pass
        
        # Check if data exists
        print(f"📊 Client {self.cid} train_loader has {len(self.train_loader)} batches")
        
        X_train, y_train = [], []
        for i, (X_batch, y_batch) in enumerate(self.train_loader):
            if i == 0:  # Print first batch
                print(f"  Batch {i}: X shape={X_batch.shape}, y shape={y_batch.shape}")
            X_train.append(X_batch.numpy().reshape(X_batch.shape[0], -1))
            y_batch_np = y_batch.numpy()
            y_train.append(y_batch_np)
        
        X_train = np.vstack(X_train)
        y_train = np.concatenate(y_train)
        
        print(f"✅ Client {self.cid} data loaded: X={X_train.shape}, y={y_train.shape}")
        
        # Train locally
        print(f"🏋️ Client {self.cid} training...")
        self.model.fit(X_train, y_train)
        print(f"✅ Client {self.cid} training complete")
        
        # Log to MLflow
        mlflow.log_metric(f"client_{self.cid}_samples", len(X_train))
        # Return updated parameters to server
        params = self.model.get_parameters()
        return fl.common.FitRes(
            status=Status(code=Code.OK, message="Success"),
            parameters=ndarrays_to_parameters(params),
            num_examples=len(X_train),
            metrics={}
        )
    
    def evaluate(self, ins):
        """Validate model"""
        print(f"📈 Client {self.cid} evaluating...")
        
        if self.model is None:
            self.model = HealthRiskModel()
        # If server sent parameters before evaluation, set them
        try:
            recv_params = parameters_to_ndarrays(ins.parameters)
            if recv_params is not None and len(recv_params) > 0:
                self.model.set_parameters(recv_params)
        except Exception:  # nosec B110
            pass
        
        X_val, y_val = [], []
        for X_batch, y_batch in self.val_loader:
            X_val.append(X_batch.numpy().reshape(X_batch.shape[0], -1))
            y_val.append(y_batch.numpy())
        
        X_val = np.vstack(X_val)
        y_val = np.concatenate(y_val)
        
        y_pred = self.model.predict_proba(X_val)[:, 1]
        auc = roc_auc_score(y_val, y_pred)
        
        print(f"🏆 Client {self.cid} AUC: {auc:.3f}")
        
        return fl.common.EvaluateRes(
            status=Status(code=Code.OK, message="Success"),
            loss=0.0,
            num_examples=len(X_val),
            metrics={"auc": float(auc)}
        )