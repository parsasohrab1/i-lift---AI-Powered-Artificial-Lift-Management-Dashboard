"""
ML Pipeline Orchestrator
Manages training, evaluation, and serving of ML models
"""
import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    mean_squared_error,
    mean_absolute_error,
)

from anomaly_detection import AnomalyDetectionService
from predictive_maintenance import PredictiveMaintenanceService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MLPipeline:
    """ML Pipeline for training and managing models"""
    
    def __init__(self, models_dir: str = "./models", data_dir: str = "./data"):
        self.models_dir = Path(models_dir)
        self.data_dir = Path(data_dir)
        self.models_dir.mkdir(parents=True, exist_ok=True)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize model services
        self.anomaly_detector = AnomalyDetectionService(model_path=str(self.models_dir))
        self.maintenance_predictor = PredictiveMaintenanceService(model_path=str(self.models_dir))
        
        # Model registry
        self.model_registry = self._load_registry()
    
    def _load_registry(self) -> Dict[str, Any]:
        """Load model registry"""
        registry_path = self.models_dir / "registry.json"
        if registry_path.exists():
            with open(registry_path, 'r') as f:
                return json.load(f)
        return {}
    
    def _save_registry(self):
        """Save model registry"""
        registry_path = self.models_dir / "registry.json"
        with open(registry_path, 'w') as f:
            json.dump(self.model_registry, f, indent=2)
    
    def train_anomaly_detection(
        self,
        data: pd.DataFrame,
        contamination: float = 0.1,
        n_estimators: int = 100,
        random_state: int = 42,
    ) -> Dict[str, Any]:
        """Train anomaly detection model"""
        try:
            logger.info("Training anomaly detection model...")
            
            # Prepare features
            feature_columns = [
                'motor_temperature',
                'intake_pressure',
                'discharge_pressure',
                'vibration',
                'current',
                'flow_rate',
            ]
            
            # Filter available columns
            available_features = [col for col in feature_columns if col in data.columns]
            if not available_features:
                raise ValueError("No valid features found in data")
            
            X = data[available_features].values
            
            # Remove NaN values
            mask = ~np.isnan(X).any(axis=1)
            X = X[mask]
            
            if len(X) == 0:
                raise ValueError("No valid data after cleaning")
            
            # Update model parameters
            from sklearn.ensemble import IsolationForest
            self.anomaly_detector.model = IsolationForest(
                contamination=contamination,
                n_estimators=n_estimators,
                random_state=random_state,
            )
            
            # Train model
            self.anomaly_detector.train(X)
            
            # Evaluate on training data
            predictions = self.anomaly_detector.predict(X)
            anomaly_rate = predictions.mean()
            
            # Save model info
            model_info = {
                'model_type': 'anomaly_detection',
                'version': '1.0.0',
                'trained_at': datetime.utcnow().isoformat(),
                'features': available_features,
                'n_samples': len(X),
                'contamination': contamination,
                'n_estimators': n_estimators,
                'anomaly_rate': float(anomaly_rate),
                'status': 'active',
            }
            
            self.model_registry['anomaly_detection'] = model_info
            self._save_registry()
            
            logger.info(f"Anomaly detection model trained successfully. Anomaly rate: {anomaly_rate:.2%}")
            
            return {
                'success': True,
                'model_info': model_info,
                'metrics': {
                    'anomaly_rate': float(anomaly_rate),
                    'n_samples': len(X),
                },
            }
            
        except Exception as e:
            logger.error(f"Error training anomaly detection model: {e}")
            return {
                'success': False,
                'error': str(e),
            }
    
    def train_predictive_maintenance(
        self,
        data: pd.DataFrame,
        target_column: str = 'failure_probability',
        n_estimators: int = 100,
        max_depth: int = 10,
        random_state: int = 42,
    ) -> Dict[str, Any]:
        """Train predictive maintenance model"""
        try:
            logger.info("Training predictive maintenance model...")
            
            # Prepare features
            feature_columns = [
                'motor_temperature',
                'intake_pressure',
                'discharge_pressure',
                'vibration',
                'current',
                'flow_rate',
            ]
            
            available_features = [col for col in feature_columns if col in data.columns]
            if not available_features:
                raise ValueError("No valid features found in data")
            
            X = data[available_features].values
            
            # Prepare target (if not exists, create synthetic)
            if target_column not in data.columns:
                logger.warning(f"Target column {target_column} not found. Creating synthetic target.")
                # Create synthetic target based on conditions
                y = np.zeros(len(data))
                # High temperature -> higher failure probability
                if 'motor_temperature' in data.columns:
                    y += (data['motor_temperature'] > 90).astype(int) * 0.3
                # High vibration -> higher failure probability
                if 'vibration' in data.columns:
                    y += (data['vibration'] > 3.5).astype(int) * 0.3
                # Low pressure -> higher failure probability
                if 'intake_pressure' in data.columns:
                    y += (data['intake_pressure'] < 400).astype(int) * 0.2
                # High current -> higher failure probability
                if 'current' in data.columns:
                    y += (data['current'] > 70).astype(int) * 0.2
                y = np.clip(y, 0, 1)
            else:
                y = data[target_column].values
            
            # Remove NaN values
            mask = ~(np.isnan(X).any(axis=1) | np.isnan(y))
            X = X[mask]
            y = y[mask]
            
            if len(X) == 0:
                raise ValueError("No valid data after cleaning")
            
            # Split data
            split_idx = int(len(X) * 0.8)
            X_train, X_test = X[:split_idx], X[split_idx:]
            y_train, y_test = y[:split_idx], y[split_idx:]
            
            # Update model parameters
            from sklearn.ensemble import RandomForestRegressor
            self.maintenance_predictor.model = RandomForestRegressor(
                n_estimators=n_estimators,
                max_depth=max_depth,
                random_state=random_state,
            )
            
            # Train model
            self.maintenance_predictor.train(X_train, y_train)
            
            # Evaluate
            y_pred = self.maintenance_predictor.model.predict(X_test)
            mse = mean_squared_error(y_test, y_pred)
            mae = mean_absolute_error(y_test, y_pred)
            rmse = np.sqrt(mse)
            
            # Save model info
            model_info = {
                'model_type': 'predictive_maintenance',
                'version': '1.0.0',
                'trained_at': datetime.utcnow().isoformat(),
                'features': available_features,
                'n_samples': len(X_train),
                'n_estimators': n_estimators,
                'max_depth': max_depth,
                'metrics': {
                    'mse': float(mse),
                    'mae': float(mae),
                    'rmse': float(rmse),
                },
                'status': 'active',
            }
            
            self.model_registry['predictive_maintenance'] = model_info
            self._save_registry()
            
            logger.info(f"Predictive maintenance model trained successfully. RMSE: {rmse:.4f}")
            
            return {
                'success': True,
                'model_info': model_info,
                'metrics': {
                    'mse': float(mse),
                    'mae': float(mae),
                    'rmse': float(rmse),
                },
            }
            
        except Exception as e:
            logger.error(f"Error training predictive maintenance model: {e}")
            return {
                'success': False,
                'error': str(e),
            }
    
    def predict_anomaly(self, features: Dict[str, float]) -> Dict[str, Any]:
        """Predict anomaly for given features"""
        try:
            if not self.anomaly_detector.is_trained:
                self.anomaly_detector.load_model()
            
            # Convert features to array
            feature_array = np.array([
                features.get('motor_temperature', 0),
                features.get('intake_pressure', 0),
                features.get('discharge_pressure', 0),
                features.get('vibration', 0),
                features.get('current', 0),
                features.get('flow_rate', 0),
            ]).reshape(1, -1)
            
            prediction = self.anomaly_detector.predict(feature_array)[0]
            anomaly_score = float(prediction)
            
            return {
                'is_anomaly': bool(anomaly_score),
                'anomaly_score': anomaly_score,
                'confidence': 0.85 if anomaly_score else 0.15,
            }
            
        except Exception as e:
            logger.error(f"Error predicting anomaly: {e}")
            return {
                'is_anomaly': False,
                'anomaly_score': 0.0,
                'confidence': 0.0,
                'error': str(e),
            }
    
    def predict_failure(self, features: Dict[str, float]) -> Dict[str, Any]:
        """Predict failure probability for given features"""
        try:
            if not self.maintenance_predictor.is_trained:
                self.maintenance_predictor.load_model()
            
            failure_probability = self.maintenance_predictor.predict_failure_probability(features)
            
            return {
                'failure_probability': float(failure_probability),
                'confidence': 0.88,
                'recommendation': self._get_recommendation(failure_probability),
            }
            
        except Exception as e:
            logger.error(f"Error predicting failure: {e}")
            return {
                'failure_probability': 0.0,
                'confidence': 0.0,
                'error': str(e),
            }
    
    def _get_recommendation(self, failure_probability: float) -> str:
        """Get maintenance recommendation based on failure probability"""
        if failure_probability > 0.7:
            return "Immediate maintenance required"
        elif failure_probability > 0.5:
            return "Schedule maintenance soon"
        elif failure_probability > 0.3:
            return "Monitor closely"
        else:
            return "Normal operation"
    
    def get_model_info(self, model_type: str) -> Optional[Dict[str, Any]]:
        """Get information about a model"""
        return self.model_registry.get(model_type)
    
    def list_models(self) -> List[Dict[str, Any]]:
        """List all registered models"""
        return list(self.model_registry.values())
    
    def evaluate_model(
        self,
        model_type: str,
        X_test: np.ndarray,
        y_test: np.ndarray,
    ) -> Dict[str, Any]:
        """Evaluate a model on test data"""
        try:
            if model_type == 'anomaly_detection':
                if not self.anomaly_detector.is_trained:
                    self.anomaly_detector.load_model()
                
                predictions = self.anomaly_detector.predict(X_test)
                
                return {
                    'model_type': model_type,
                    'anomaly_rate': float(predictions.mean()),
                    'n_anomalies': int(predictions.sum()),
                    'n_samples': len(predictions),
                }
            
            elif model_type == 'predictive_maintenance':
                if not self.maintenance_predictor.is_trained:
                    self.maintenance_predictor.load_model()
                
                y_pred = self.maintenance_predictor.model.predict(X_test)
                mse = mean_squared_error(y_test, y_pred)
                mae = mean_absolute_error(y_test, y_pred)
                rmse = np.sqrt(mse)
                
                return {
                    'model_type': model_type,
                    'mse': float(mse),
                    'mae': float(mae),
                    'rmse': float(rmse),
                    'n_samples': len(y_test),
                }
            
            else:
                raise ValueError(f"Unknown model type: {model_type}")
                
        except Exception as e:
            logger.error(f"Error evaluating model: {e}")
            return {
                'error': str(e),
            }

