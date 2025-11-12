"""
Predictive Maintenance Service
"""
import numpy as np
from sklearn.ensemble import RandomForestRegressor
import joblib
from pathlib import Path
from typing import Dict, Any


class PredictiveMaintenanceService:
    """Service for predicting equipment failures"""
    
    def __init__(self, model_path: str = "./models"):
        self.model_path = Path(model_path)
        self.model_path.mkdir(parents=True, exist_ok=True)
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.is_trained = False
    
    def train(self, X: np.ndarray, y: np.ndarray):
        """Train the predictive maintenance model"""
        self.model.fit(X, y)
        self.is_trained = True
        self.save_model()
    
    def predict_failure_probability(self, features: Dict[str, float]) -> float:
        """Predict failure probability"""
        if not self.is_trained:
            raise ValueError("Model not trained. Call train() first.")
        
        # Convert features to array (order matters)
        feature_array = np.array([
            features.get('motor_temperature', 0),
            features.get('vibration', 0),
            features.get('current', 0),
            features.get('intake_pressure', 0),
            features.get('discharge_pressure', 0),
        ]).reshape(1, -1)
        
        prediction = self.model.predict(feature_array)[0]
        return float(prediction)
    
    def save_model(self):
        """Save the trained model"""
        joblib.dump(self.model, self.model_path / "predictive_maintenance.pkl")
    
    def load_model(self):
        """Load a trained model"""
        model_file = self.model_path / "predictive_maintenance.pkl"
        if model_file.exists():
            self.model = joblib.load(model_file)
            self.is_trained = True

