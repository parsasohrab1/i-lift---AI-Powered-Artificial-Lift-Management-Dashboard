"""
Anomaly Detection Service for Artificial Lift Systems
"""
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import joblib
from pathlib import Path


class AnomalyDetectionService:
    """Service for detecting anomalies in sensor data"""
    
    def __init__(self, model_path: str = "./models"):
        self.model_path = Path(model_path)
        self.model_path.mkdir(parents=True, exist_ok=True)
        self.model = IsolationForest(contamination=0.1, random_state=42)
        self.scaler = StandardScaler()
        self.is_trained = False
    
    def train(self, data: np.ndarray):
        """Train the anomaly detection model"""
        # Scale the data
        data_scaled = self.scaler.fit_transform(data)
        
        # Train the model
        self.model.fit(data_scaled)
        self.is_trained = True
        
        # Save the model
        self.save_model()
    
    def predict(self, data: np.ndarray) -> np.ndarray:
        """Predict anomalies in data"""
        if not self.is_trained:
            raise ValueError("Model not trained. Call train() first.")
        
        data_scaled = self.scaler.transform(data)
        predictions = self.model.predict(data_scaled)
        
        # Convert -1 (anomaly) to 1, 1 (normal) to 0
        return (predictions == -1).astype(int)
    
    def save_model(self):
        """Save the trained model"""
        joblib.dump(self.model, self.model_path / "anomaly_detector.pkl")
        joblib.dump(self.scaler, self.model_path / "scaler.pkl")
    
    def load_model(self):
        """Load a trained model"""
        model_file = self.model_path / "anomaly_detector.pkl"
        scaler_file = self.model_path / "scaler.pkl"
        
        if model_file.exists() and scaler_file.exists():
            self.model = joblib.load(model_file)
            self.scaler = joblib.load(scaler_file)
            self.is_trained = True

