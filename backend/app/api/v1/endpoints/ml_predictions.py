"""
ML prediction endpoints
"""
from typing import List, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_active_user, get_current_admin_user
from app.core.permissions import Permission, has_permission
from app.models.user import User
from app.schemas.ml import (
    PredictionRequest,
    PredictionResponse,
    AnomalyResponse,
    ModelPerformanceResponse,
    ModelInfoResponse,
    TrainingRequest,
    TrainingResponse,
)
from app.services.ml_service import MLService

router = APIRouter()


@router.get("/predictions", response_model=List[PredictionResponse])
async def get_predictions(
    well_id: Optional[str] = Query(None, description="Filter by well ID"),
    model_type: Optional[str] = Query(None, description="Filter by model type"),
    limit: int = Query(100, ge=1, le=1000, description="Number of predictions to return"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get ML predictions"""
    if not has_permission(current_user.role, Permission.VIEW_ML_PREDICTIONS):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied: VIEW_ML_PREDICTIONS required"
        )
    
    service = MLService(db=db)
    predictions = await service.get_predictions(
        well_id=well_id,
        model_type=model_type,
        limit=limit,
    )
    
    return predictions


@router.post("/predict", response_model=PredictionResponse)
async def create_prediction(
    request: PredictionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Create a new prediction"""
    if not has_permission(current_user.role, Permission.CREATE_ML_PREDICTIONS):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied: CREATE_ML_PREDICTIONS required"
        )
    
    # Validate model type
    valid_model_types = ["anomaly_detection", "predictive_maintenance", "production_optimization"]
    if request.model_type not in valid_model_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid model_type. Must be one of: {', '.join(valid_model_types)}"
        )
    
    service = MLService(db=db)
    prediction = await service.predict(request)
    
    return prediction


@router.get("/anomalies", response_model=List[AnomalyResponse])
async def get_anomalies(
    well_id: Optional[str] = Query(None, description="Filter by well ID"),
    start_time: Optional[datetime] = Query(None, description="Start time"),
    end_time: Optional[datetime] = Query(None, description="End time"),
    threshold: float = Query(0.5, ge=0, le=1, description="Anomaly score threshold"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get detected anomalies"""
    if not has_permission(current_user.role, Permission.VIEW_ML_PREDICTIONS):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied"
        )
    
    service = MLService(db=db)
    anomalies = await service.get_anomalies(
        well_id=well_id,
        start_time=start_time,
        end_time=end_time,
        threshold=threshold,
    )
    
    return [AnomalyResponse(**a) for a in anomalies]


@router.get("/anomalies/realtime")
async def get_realtime_anomalies(
    well_id: Optional[str] = Query(None, description="Filter by well ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get real-time anomalies (last hour)"""
    if not has_permission(current_user.role, Permission.VIEW_ML_PREDICTIONS):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied"
        )
    
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(hours=1)
    
    service = MLService(db=db)
    anomalies = await service.get_anomalies(
        well_id=well_id,
        start_time=start_time,
        end_time=end_time,
        threshold=0.5,
    )
    
    return {
        "anomalies": anomalies,
        "count": len(anomalies),
        "time_range": {
            "start": start_time.isoformat(),
            "end": end_time.isoformat(),
        },
    }


@router.get("/models", response_model=List[ModelInfoResponse])
async def get_models(
    current_user: User = Depends(get_current_active_user),
):
    """Get list of available ML models"""
    if not has_permission(current_user.role, Permission.VIEW_ML_PREDICTIONS):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied"
        )
    
    models = [
        ModelInfoResponse(
            model_type="anomaly_detection",
            model_name="Anomaly Detection Model",
            version="1.0.0",
            status="active",
            accuracy=0.92,
            last_trained="2024-01-01T00:00:00Z",
            description="Detects anomalies in sensor data using isolation forest",
        ),
        ModelInfoResponse(
            model_type="predictive_maintenance",
            model_name="Predictive Maintenance Model",
            version="1.0.0",
            status="active",
            accuracy=0.88,
            last_trained="2024-01-01T00:00:00Z",
            description="Predicts equipment failure probability",
        ),
        ModelInfoResponse(
            model_type="production_optimization",
            model_name="Production Optimization Model",
            version="1.0.0",
            status="active",
            accuracy=0.85,
            last_trained="2024-01-01T00:00:00Z",
            description="Optimizes production parameters for maximum efficiency",
        ),
    ]
    
    return models


@router.get("/models/{model_type}/performance", response_model=ModelPerformanceResponse)
async def get_model_performance(
    model_type: str,
    start_time: Optional[datetime] = Query(None, description="Start time"),
    end_time: Optional[datetime] = Query(None, description="End time"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get model performance metrics"""
    if not has_permission(current_user.role, Permission.VIEW_ML_PREDICTIONS):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied"
        )
    
    service = MLService(db=db)
    performance = await service.get_model_performance(
        model_type=model_type,
        start_time=start_time,
        end_time=end_time,
    )
    
    return ModelPerformanceResponse(**performance)


@router.post("/models/train", response_model=TrainingResponse)
async def train_model(
    request: TrainingRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    """Train a new ML model (admin only)"""
    if not has_permission(current_user.role, Permission.TRAIN_MODELS):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied: TRAIN_MODELS required"
        )
    
    # Validate model type
    valid_model_types = ["anomaly_detection", "predictive_maintenance", "production_optimization"]
    if request.model_type not in valid_model_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid model_type. Must be one of: {', '.join(valid_model_types)}"
        )
    
    import uuid
    
    training_id = str(uuid.uuid4())
    started_at = datetime.utcnow().isoformat()
    
    # TODO: Implement actual training logic
    # For now, return a mock response
    return TrainingResponse(
        training_id=training_id,
        model_type=request.model_type,
        status="started",
        message=f"Training started for {request.model_type} model",
        started_at=started_at,
        completed_at=None,
        metrics=None,
    )


@router.get("/predictions/latest")
async def get_latest_predictions(
    well_id: Optional[str] = Query(None, description="Filter by well ID"),
    model_type: Optional[str] = Query(None, description="Filter by model type"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get latest predictions for each well/model combination"""
    if not has_permission(current_user.role, Permission.VIEW_ML_PREDICTIONS):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied"
        )
    
    service = MLService(db=db)
    
    # Get latest prediction for each well/model
    from app.models.ml_prediction import MLPrediction
    from sqlalchemy import and_, func
    
    # Get latest for each well_id + model_type combination
    subquery = (
        db.query(
            MLPrediction.well_id,
            MLPrediction.model_type,
            func.max(MLPrediction.timestamp).label('max_timestamp')
        )
        .group_by(MLPrediction.well_id, MLPrediction.model_type)
        .subquery()
    )
    
    latest = (
        db.query(MLPrediction)
        .join(
            subquery,
            and_(
                MLPrediction.well_id == subquery.c.well_id,
                MLPrediction.model_type == subquery.c.model_type,
                MLPrediction.timestamp == subquery.c.max_timestamp
            )
        )
    )
    
    if well_id:
        latest = latest.filter(MLPrediction.well_id == well_id)
    if model_type:
        latest = latest.filter(MLPrediction.model_type == model_type)
    
    predictions = latest.all()
    
    return [PredictionResponse.model_validate(p) for p in predictions]
