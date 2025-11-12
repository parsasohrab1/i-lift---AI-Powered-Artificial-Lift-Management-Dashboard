"""
ML prediction service with model integration
"""
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
import uuid

from app.schemas.ml import PredictionRequest, PredictionResponse
from app.models.ml_prediction import MLPrediction
from app.models.sensor import SensorReading as SensorReadingModel
from app.core.database import get_db
from app.core.redis_client import redis_client
from app.utils.logger import setup_logging

logger = setup_logging()


class MLService:
    """Service for ML operations"""
    
    def __init__(self, db: Session = None):
        if db:
            self.db = db
        else:
            self.db = next(get_db())
    
    async def get_predictions(
        self,
        well_id: Optional[str] = None,
        model_type: Optional[str] = None,
        limit: int = 100,
    ) -> List[PredictionResponse]:
        """Get ML predictions"""
        try:
            query = self.db.query(MLPrediction)
            
            if well_id:
                query = query.filter(MLPrediction.well_id == well_id)
            if model_type:
                query = query.filter(MLPrediction.model_type == model_type)
            
            query = query.order_by(desc(MLPrediction.timestamp))
            predictions = query.limit(limit).all()
            
            return [PredictionResponse.model_validate(p) for p in predictions]
            
        except Exception as e:
            logger.error("Error getting predictions", error=str(e))
            raise
    
    async def predict(
        self,
        request: PredictionRequest,
    ) -> PredictionResponse:
        """Create a new prediction"""
        try:
            # Get latest sensor data for the well
            latest_readings = self.db.query(SensorReadingModel).filter(
                SensorReadingModel.well_id == request.well_id
            ).order_by(desc(SensorReadingModel.timestamp)).limit(10).all()
            
            if not latest_readings:
                raise ValueError(f"No sensor data found for well {request.well_id}")
            
            # Prepare features from sensor data
            features = self._extract_features(latest_readings, request.features)
            
            # Get prediction based on model type
            prediction_value, confidence_score = await self._get_prediction(
                model_type=request.model_type,
                features=features,
                well_id=request.well_id,
            )
            
            # Create prediction record
            prediction = MLPrediction(
                prediction_id=uuid.uuid4(),
                well_id=request.well_id,
                model_type=request.model_type,
                prediction_value=prediction_value,
                confidence_score=confidence_score,
                prediction_type=self._get_prediction_type(request.model_type),
                features=features,
                timestamp=datetime.utcnow(),
            )
            
            self.db.add(prediction)
            self.db.commit()
            self.db.refresh(prediction)
            
            return PredictionResponse.model_validate(prediction)
            
        except Exception as e:
            self.db.rollback()
            logger.error("Error creating prediction", error=str(e))
            raise
    
    def _extract_features(
        self,
        readings: List[SensorReadingModel],
        provided_features: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Extract features from sensor readings"""
        features = provided_features.copy()
        
        # Organize readings by sensor type
        sensor_data = {}
        for reading in readings:
            if reading.sensor_type not in sensor_data:
                sensor_data[reading.sensor_type] = []
            sensor_data[reading.sensor_type].append(reading.sensor_value)
        
        # Calculate statistical features
        for sensor_type, values in sensor_data.items():
            if values:
                features[f'{sensor_type}_mean'] = sum(values) / len(values)
                features[f'{sensor_type}_min'] = min(values)
                features[f'{sensor_type}_max'] = max(values)
                if len(values) > 1:
                    import statistics
                    features[f'{sensor_type}_std'] = statistics.stdev(values)
        
        # Add latest values
        for reading in readings[:6]:  # Latest 6 readings
            features[f'latest_{reading.sensor_type}'] = reading.sensor_value
        
        return features
    
    async def _get_prediction(
        self,
        model_type: str,
        features: Dict[str, Any],
        well_id: str,
    ) -> tuple[Optional[float], Optional[float]]:
        """Get prediction from ML model"""
        try:
            # Try to use ML Model Server
            from app.services.ml_model_service import MLModelService
            ml_model_service = MLModelService()
            
            try:
                result = await ml_model_service.predict(well_id, model_type, features)
                prediction_data = result.get("prediction", {})
                
                if model_type == "anomaly_detection":
                    anomaly_score = prediction_data.get("anomaly_score", 0.0)
                    confidence = prediction_data.get("confidence", 0.0)
                    return anomaly_score, confidence
                elif model_type == "predictive_maintenance":
                    failure_prob = prediction_data.get("failure_probability", 0.0)
                    confidence = prediction_data.get("confidence", 0.0)
                    return failure_prob, confidence
                elif model_type == "production_optimization":
                    return self._predict_optimization(features)
            except Exception as e:
                logger.warning(f"ML Model Server unavailable, using fallback: {e}")
            
            # Fallback to rule-based predictions
            if model_type == "anomaly_detection":
                return self._predict_anomaly(features)
            elif model_type == "predictive_maintenance":
                return self._predict_failure(features)
            elif model_type == "production_optimization":
                return self._predict_optimization(features)
            else:
                # Default: return None
                return None, None
                
        except Exception as e:
            logger.error("Error getting prediction from model", error=str(e))
            return None, None
    
    def _predict_anomaly(self, features: Dict[str, Any]) -> tuple[float, float]:
        """Simple anomaly detection prediction"""
        # Simple rule-based: check if values are outside normal ranges
        anomaly_score = 0.0
        
        if 'latest_motor_temperature' in features:
            temp = features['latest_motor_temperature']
            if temp > 95:
                anomaly_score += 0.5
            if temp < 65:
                anomaly_score += 0.3
        
        if 'latest_vibration' in features:
            vib = features['latest_vibration']
            if vib > 4.0:
                anomaly_score += 0.4
        
        if 'latest_current' in features:
            current = features['latest_current']
            if current > 75:
                anomaly_score += 0.3
        
        confidence = min(1.0, anomaly_score)
        return anomaly_score, confidence
    
    def _predict_failure(self, features: Dict[str, Any]) -> tuple[float, float]:
        """Simple failure prediction"""
        # Calculate failure probability based on trends
        failure_probability = 0.0
        
        # Check temperature trend
        if 'motor_temperature_mean' in features and 'latest_motor_temperature' in features:
            temp_trend = features['latest_motor_temperature'] - features['motor_temperature_mean']
            if temp_trend > 10:
                failure_probability += 0.4
        
        # Check vibration trend
        if 'vibration_mean' in features and 'latest_vibration' in features:
            vib_trend = features['latest_vibration'] - features['vibration_mean']
            if vib_trend > 1.0:
                failure_probability += 0.3
        
        # Check pressure drop
        if 'intake_pressure_mean' in features and 'latest_intake_pressure' in features:
            pressure_drop = features['intake_pressure_mean'] - features['latest_intake_pressure']
            if pressure_drop > 50:
                failure_probability += 0.3
        
        confidence = min(1.0, failure_probability)
        return failure_probability, confidence
    
    def _predict_optimization(self, features: Dict[str, Any]) -> tuple[float, float]:
        """Simple production optimization prediction"""
        # Predict optimal flow rate
        if 'latest_flow_rate' in features and 'latest_current' in features:
            current_flow = features['latest_flow_rate']
            current = features['latest_current']
            
            # Simple optimization: increase flow if efficiency is good
            if current > 0:
                efficiency = current_flow / current
                if efficiency > 35:
                    optimal_flow = current_flow * 1.1  # 10% increase
                else:
                    optimal_flow = current_flow * 0.95  # 5% decrease
                
                confidence = 0.7
                return optimal_flow, confidence
        
        return None, None
    
    def _get_prediction_type(self, model_type: str) -> str:
        """Get prediction type from model type"""
        type_map = {
            "anomaly_detection": "anomaly_score",
            "predictive_maintenance": "failure_probability",
            "production_optimization": "optimal_value",
        }
        return type_map.get(model_type, "prediction")
    
    async def get_anomalies(
        self,
        well_id: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        threshold: float = 0.5,
    ) -> List[Dict[str, Any]]:
        """Get detected anomalies"""
        try:
            if not end_time:
                end_time = datetime.utcnow()
            if not start_time:
                start_time = end_time - timedelta(days=7)
            
            # Get anomaly predictions
            query = self.db.query(MLPrediction).filter(
                MLPrediction.model_type == "anomaly_detection",
                MLPrediction.prediction_value >= threshold,
                MLPrediction.timestamp >= start_time,
                MLPrediction.timestamp <= end_time,
            )
            
            if well_id:
                query = query.filter(MLPrediction.well_id == well_id)
            
            query = query.order_by(desc(MLPrediction.timestamp))
            anomalies = query.limit(100).all()
            
            result = []
            for anomaly in anomalies:
                result.append({
                    'prediction_id': str(anomaly.prediction_id),
                    'well_id': anomaly.well_id,
                    'anomaly_score': float(anomaly.prediction_value) if anomaly.prediction_value else 0,
                    'confidence': float(anomaly.confidence_score) if anomaly.confidence_score else 0,
                    'timestamp': anomaly.timestamp.isoformat(),
                    'features': anomaly.features,
                })
            
            return result
            
        except Exception as e:
            logger.error("Error getting anomalies", error=str(e))
            raise
    
    async def get_model_performance(
        self,
        model_type: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """Get model performance metrics"""
        try:
            if not end_time:
                end_time = datetime.utcnow()
            if not start_time:
                start_time = end_time - timedelta(days=30)
            
            # Get predictions for model
            predictions = self.db.query(MLPrediction).filter(
                MLPrediction.model_type == model_type,
                MLPrediction.timestamp >= start_time,
                MLPrediction.timestamp <= end_time,
            ).all()
            
            if not predictions:
                return {
                    'model_type': model_type,
                    'total_predictions': 0,
                    'average_confidence': 0,
                    'time_range': {
                        'start': start_time.isoformat(),
                        'end': end_time.isoformat(),
                    },
                }
            
            # Calculate metrics
            confidences = [p.confidence_score for p in predictions if p.confidence_score]
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0
            
            # Count by well
            well_counts = {}
            for p in predictions:
                well_counts[p.well_id] = well_counts.get(p.well_id, 0) + 1
            
            return {
                'model_type': model_type,
                'total_predictions': len(predictions),
                'average_confidence': avg_confidence,
                'predictions_by_well': well_counts,
                'time_range': {
                    'start': start_time.isoformat(),
                    'end': end_time.isoformat(),
                },
            }
            
        except Exception as e:
            logger.error("Error getting model performance", error=str(e))
            raise
