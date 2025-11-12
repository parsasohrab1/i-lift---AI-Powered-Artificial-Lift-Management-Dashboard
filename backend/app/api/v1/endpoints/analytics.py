"""
Analytics endpoints
"""
from fastapi import APIRouter, Depends, Query, HTTPException, status
from typing import Optional, List
from datetime import datetime

from app.core.dependencies import get_current_active_user
from app.core.permissions import Permission, has_permission
from app.models.user import User
from app.schemas.analytics import (
    AnalyticsResponse,
    TrendResponse,
    ComparisonResponse,
    PerformanceMetricsResponse,
    TimeSeriesResponse,
)
from app.services.analytics_service import AnalyticsService
from app.core.database import get_db
from sqlalchemy.orm import Session

router = APIRouter()


@router.get("/kpi", response_model=AnalyticsResponse)
async def get_kpis(
    well_id: Optional[str] = Query(None, description="Filter by well ID"),
    start_time: Optional[datetime] = Query(None, description="Start time filter"),
    end_time: Optional[datetime] = Query(None, description="End time filter"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get KPI analytics"""
    if not has_permission(current_user.role, Permission.VIEW_ANALYTICS):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied: VIEW_ANALYTICS required"
        )
    
    service = AnalyticsService(db=db)
    kpis = await service.get_kpis(
        well_id=well_id,
        start_time=start_time,
        end_time=end_time,
    )
    
    return AnalyticsResponse(kpis=kpis)


@router.get("/trends", response_model=TrendResponse)
async def get_trends(
    well_id: str = Query(..., description="Well ID"),
    metric: str = Query(..., description="Metric name (temperature, pressure, flow, vibration, current)"),
    days: int = Query(30, ge=1, le=365, description="Number of days for trend analysis"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get trend analysis for a metric"""
    if not has_permission(current_user.role, Permission.VIEW_ANALYTICS):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied"
        )
    
    service = AnalyticsService(db=db)
    trend_data = await service.get_trends(
        well_id=well_id,
        metric=metric,
        days=days,
    )
    
    return TrendResponse(**trend_data)


@router.get("/comparison", response_model=ComparisonResponse)
async def get_comparison(
    well_ids: List[str] = Query(..., description="List of well IDs to compare"),
    metric: str = Query(..., description="Metric to compare"),
    start_time: Optional[datetime] = Query(None, description="Start time"),
    end_time: Optional[datetime] = Query(None, description="End time"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Compare multiple wells for a metric"""
    if not has_permission(current_user.role, Permission.VIEW_ANALYTICS):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied"
        )
    
    if len(well_ids) < 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least 2 well IDs required for comparison"
        )
    
    if len(well_ids) > 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum 10 wells can be compared at once"
        )
    
    service = AnalyticsService(db=db)
    comparison_data = await service.get_comparison(
        well_ids=well_ids,
        metric=metric,
        start_time=start_time,
        end_time=end_time,
    )
    
    return ComparisonResponse(**comparison_data)


@router.get("/performance", response_model=PerformanceMetricsResponse)
async def get_performance_metrics(
    well_id: Optional[str] = Query(None, description="Filter by well ID"),
    start_time: Optional[datetime] = Query(None, description="Start time"),
    end_time: Optional[datetime] = Query(None, description="End time"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get performance metrics"""
    if not has_permission(current_user.role, Permission.VIEW_ANALYTICS):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied"
        )
    
    service = AnalyticsService(db=db)
    metrics = await service.get_performance_metrics(
        well_id=well_id,
        start_time=start_time,
        end_time=end_time,
    )
    
    return PerformanceMetricsResponse(**metrics)


@router.get("/timeseries", response_model=TimeSeriesResponse)
async def get_timeseries(
    well_id: str = Query(..., description="Well ID"),
    sensor_type: str = Query(..., description="Sensor type"),
    start_time: datetime = Query(..., description="Start time"),
    end_time: datetime = Query(..., description="End time"),
    aggregation: str = Query("hourly", regex="^(raw|hourly|daily)$", description="Aggregation level"),
    limit: int = Query(1000, ge=1, le=10000, description="Maximum number of data points"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get time series data for visualization"""
    if not has_permission(current_user.role, Permission.VIEW_ANALYTICS):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied"
        )
    
    if end_time <= start_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="End time must be after start time"
        )
    
    # Import sensor service for aggregated data
    from app.services.sensor_service import SensorService
    
    sensor_service = SensorService(db=db)
    
    if aggregation == "raw":
        # Get raw data points
        readings = await sensor_service.get_readings(
            well_id=well_id,
            sensor_type=sensor_type,
            start_time=start_time,
            end_time=end_time,
            limit=limit,
        )
        
        data_points = [
            {
                "timestamp": r.timestamp.isoformat(),
                "value": r.sensor_value,
                "well_id": r.well_id,
            }
            for r in readings
        ]
    else:
        # Get aggregated data
        aggregated = await sensor_service.get_aggregated_data(
            well_id=well_id,
            sensor_type=sensor_type,
            start_time=start_time,
            end_time=end_time,
            aggregation=aggregation,
        )
        
        data_points = [
            {
                "timestamp": item["timestamp"],
                "value": item["avg_value"],
                "well_id": well_id,
            }
            for item in aggregated[:limit]
        ]
    
    return TimeSeriesResponse(
        metric=sensor_type,
        sensor_type=sensor_type,
        data_points=data_points,
        time_range={
            "start": start_time.isoformat(),
            "end": end_time.isoformat(),
        },
    )


@router.get("/summary")
async def get_analytics_summary(
    well_id: Optional[str] = Query(None, description="Filter by well ID"),
    days: int = Query(30, ge=1, le=365, description="Number of days"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get comprehensive analytics summary"""
    if not has_permission(current_user.role, Permission.VIEW_ANALYTICS):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied"
        )
    
    from datetime import timedelta
    
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(days=days)
    
    service = AnalyticsService(db=db)
    
    # Get all analytics
    kpis = await service.get_kpis(
        well_id=well_id,
        start_time=start_time,
        end_time=end_time,
    )
    
    performance = await service.get_performance_metrics(
        well_id=well_id,
        start_time=start_time,
        end_time=end_time,
    )
    
    return {
        "kpis": kpis,
        "performance": performance,
        "time_range": {
            "start": start_time.isoformat(),
            "end": end_time.isoformat(),
            "days": days,
        },
    }
