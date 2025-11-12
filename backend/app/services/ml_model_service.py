"""
ML Model Service - Integration with ML Model Server
"""
import httpx
from typing import Dict, Any, Optional
from app.core.config import settings
from app.utils.logger import setup_logging

logger = setup_logging()

ML_MODEL_SERVER_URL = getattr(settings, 'ML_MODEL_SERVER_URL', 'http://localhost:8001')


class MLModelService:
    """Service for interacting with ML Model Server"""
    
    def __init__(self, base_url: str = ML_MODEL_SERVER_URL):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def predict(
        self,
        well_id: str,
        model_type: str,
        features: Dict[str, float],
    ) -> Dict[str, Any]:
        """Make a prediction using ML model server"""
        try:
            response = await self.client.post(
                f"{self.base_url}/predict",
                json={
                    "well_id": well_id,
                    "model_type": model_type,
                    "features": features,
                },
            )
            response.raise_for_status()
            return response.json()
            
        except httpx.HTTPError as e:
            logger.error(f"Error calling ML model server: {e}")
            # Fallback to rule-based prediction
            return self._fallback_predict(model_type, features)
        except Exception as e:
            logger.error(f"Unexpected error in ML model service: {e}")
            return self._fallback_predict(model_type, features)
    
    def _fallback_predict(self, model_type: str, features: Dict[str, float]) -> Dict[str, Any]:
        """Fallback rule-based prediction if ML server is unavailable"""
        if model_type == "anomaly_detection":
            anomaly_score = 0.0
            if features.get('motor_temperature', 0) > 95:
                anomaly_score += 0.5
            if features.get('vibration', 0) > 4.0:
                anomaly_score += 0.4
            if features.get('current', 0) > 75:
                anomaly_score += 0.3
            
            return {
                "prediction": {
                    "is_anomaly": anomaly_score > 0.5,
                    "anomaly_score": min(1.0, anomaly_score),
                    "confidence": 0.7,
                }
            }
        
        elif model_type == "predictive_maintenance":
            failure_prob = 0.0
            if features.get('motor_temperature', 0) > 90:
                failure_prob += 0.4
            if features.get('vibration', 0) > 3.5:
                failure_prob += 0.3
            if features.get('intake_pressure', 0) < 400:
                failure_prob += 0.3
            
            return {
                "prediction": {
                    "failure_probability": min(1.0, failure_prob),
                    "confidence": 0.7,
                    "recommendation": (
                        "Immediate maintenance required" if failure_prob > 0.7
                        else "Schedule maintenance soon" if failure_prob > 0.5
                        else "Monitor closely" if failure_prob > 0.3
                        else "Normal operation"
                    ),
                }
            }
        
        return {"prediction": {}}
    
    async def get_model_info(self, model_type: str) -> Optional[Dict[str, Any]]:
        """Get model information"""
        try:
            response = await self.client.get(f"{self.base_url}/models/{model_type}")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error getting model info: {e}")
            return None
    
    async def list_models(self) -> list:
        """List all available models"""
        try:
            response = await self.client.get(f"{self.base_url}/models")
            response.raise_for_status()
            data = response.json()
            return data.get("models", [])
        except Exception as e:
            logger.error(f"Error listing models: {e}")
            return []
    
    async def train_model(
        self,
        model_type: str,
        data_path: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Train a model"""
        try:
            response = await self.client.post(
                f"{self.base_url}/train",
                json={
                    "model_type": model_type,
                    "data_path": data_path,
                    "parameters": parameters or {},
                },
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error training model: {e}")
            return {"success": False, "error": str(e)}
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()

