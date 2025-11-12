"""
ML prediction schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime


class PredictionRequest(BaseModel):
    """Prediction request schema"""
    well_id: str = Field(..., description="Well ID")
    model_type: str = Field(..., description="Model type (anomaly_detection, predictive_maintenance, production_optimization)")
    features: Optional[Dict[str, Any]] = Field(None, description="Additional features (optional, will be extracted from sensor data)")


class PredictionResponse(BaseModel):
    """Prediction response schema"""
    prediction_id: str
    well_id: str
    model_type: str
    prediction_value: Optional[float] = None
    confidence_score: Optional[float] = Field(None, ge=0, le=1, description="Confidence score 0-1")
    prediction_type: str
    timestamp: datetime
    features: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True


class AnomalyResponse(BaseModel):
    """Anomaly detection response"""
    prediction_id: str
    well_id: str
    anomaly_score: float = Field(..., ge=0, le=1)
    confidence: float = Field(..., ge=0, le=1)
    timestamp: str
    features: Optional[Dict[str, Any]] = None


class ModelPerformanceResponse(BaseModel):
    """Model performance metrics response"""
    model_type: str
    total_predictions: int
    average_confidence: float
    predictions_by_well: Dict[str, int]
    time_range: Dict[str, str]


class ModelInfoResponse(BaseModel):
    """Model information response"""
    model_type: str
    model_name: str
    version: str
    status: str  # active, training, deprecated
    accuracy: Optional[float] = None
    last_trained: Optional[str] = None
    description: Optional[str] = None


class TrainingRequest(BaseModel):
    """Model training request schema"""
    model_type: str = Field(..., description="Model type to train")
    well_ids: Optional[List[str]] = Field(None, description="Specific wells to use for training")
    start_date: Optional[datetime] = Field(None, description="Start date for training data")
    end_date: Optional[datetime] = Field(None, description="End date for training data")
    parameters: Optional[Dict[str, Any]] = Field(None, description="Training parameters")


class TrainingResponse(BaseModel):
    """Training response schema"""
    training_id: str
    model_type: str
    status: str  # started, completed, failed
    message: str
    started_at: str
    completed_at: Optional[str] = None
    metrics: Optional[Dict[str, Any]] = None
