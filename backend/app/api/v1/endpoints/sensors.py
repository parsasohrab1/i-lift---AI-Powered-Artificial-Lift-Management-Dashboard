"""
Sensor data endpoints
"""
from fastapi import APIRouter, Depends, Query, HTTPException, status
from typing import List, Optional
from datetime import datetime, timedelta

from app.core.dependencies import get_current_active_user
from app.core.permissions import Permission, has_permission
from app.models.user import User
from app.schemas.sensor import (
    SensorReading,
    SensorReadingResponse,
    SensorReadingsListResponse,
    AggregatedDataResponse,
    RealtimeDataResponse,
    SensorStatisticsResponse,
)
from app.services.sensor_service import SensorService
from app.core.database import get_db
from sqlalchemy.orm import Session

router = APIRouter()


@router.get("/", response_model=SensorReadingsListResponse)
async def get_sensor_readings(
    well_id: Optional[str] = Query(None, description="Filter by well ID"),
    sensor_type: Optional[str] = Query(None, description="Filter by sensor type"),
    start_time: Optional[datetime] = Query(None, description="Start time filter"),
    end_time: Optional[datetime] = Query(None, description="End time filter"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get sensor readings with filters and pagination"""
    # Check permission
    if not has_permission(current_user.role, Permission.VIEW_SENSOR_DATA):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied"
        )
    
    service = SensorService(db=db)
    readings = await service.get_readings(
        well_id=well_id,
        sensor_type=sensor_type,
        start_time=start_time,
        end_time=end_time,
        limit=limit,
        offset=offset,
    )
    
    # Get total count (simplified - in production, use separate count query)
    total = len(readings)  # This is approximate
    
    return SensorReadingsListResponse(
        readings=readings,
        total=total,
        offset=offset,
        limit=limit,
    )


@router.get("/latest", response_model=List[SensorReadingResponse])
async def get_latest_readings(
    well_id: Optional[str] = Query(None, description="Filter by well ID"),
    sensor_type: Optional[str] = Query(None, description="Filter by sensor type"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get latest reading for each sensor"""
    if not has_permission(current_user.role, Permission.VIEW_SENSOR_DATA):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied"
        )
    
    service = SensorService(db=db)
    readings = await service.get_latest_readings(
        well_id=well_id,
        sensor_type=sensor_type,
    )
    
    return readings


@router.get("/realtime", response_model=RealtimeDataResponse)
async def get_realtime_sensor_data(
    well_id: Optional[str] = Query(None, description="Filter by well ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get real-time sensor data (cached, updates every 5 seconds)"""
    if not has_permission(current_user.role, Permission.VIEW_SENSOR_DATA):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied"
        )
    
    service = SensorService(db=db)
    data = await service.get_realtime_data(well_id=well_id)
    
    return RealtimeDataResponse(
        data=data,
        timestamp=datetime.utcnow().isoformat(),
    )


@router.post("/", response_model=SensorReadingResponse)
async def create_sensor_reading(
    reading: SensorReading,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Create a new sensor reading"""
    # Check permission
    if not has_permission(current_user.role, Permission.CREATE_SENSOR_DATA):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied"
        )
    
    service = SensorService(db=db)
    return await service.create_reading(reading)


@router.get("/aggregated", response_model=List[AggregatedDataResponse])
async def get_aggregated_data(
    well_id: str = Query(..., description="Well ID"),
    sensor_type: str = Query(..., description="Sensor type"),
    start_time: datetime = Query(..., description="Start time"),
    end_time: datetime = Query(..., description="End time"),
    aggregation: str = Query("hourly", regex="^(hourly|daily|weekly)$", description="Aggregation period"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get aggregated sensor data (hourly, daily, or weekly)"""
    if not has_permission(current_user.role, Permission.VIEW_SENSOR_DATA):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied"
        )
    
    # Validate time range
    if end_time <= start_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="End time must be after start time"
        )
    
    # Limit to 1 year
    max_range = timedelta(days=365)
    if end_time - start_time > max_range:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Time range cannot exceed 1 year"
        )
    
    service = SensorService(db=db)
    aggregated = await service.get_aggregated_data(
        well_id=well_id,
        sensor_type=sensor_type,
        start_time=start_time,
        end_time=end_time,
        aggregation=aggregation,
    )
    
    return [AggregatedDataResponse(**item) for item in aggregated]


@router.get("/statistics", response_model=SensorStatisticsResponse)
async def get_sensor_statistics(
    well_id: Optional[str] = Query(None, description="Filter by well ID"),
    sensor_type: Optional[str] = Query(None, description="Filter by sensor type"),
    start_time: Optional[datetime] = Query(None, description="Start time filter"),
    end_time: Optional[datetime] = Query(None, description="End time filter"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get statistics for sensor data"""
    if not has_permission(current_user.role, Permission.VIEW_SENSOR_DATA):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied"
        )
    
    service = SensorService(db=db)
    stats = await service.get_statistics(
        well_id=well_id,
        sensor_type=sensor_type,
        start_time=start_time,
        end_time=end_time,
    )
    
    return SensorStatisticsResponse(statistics=stats)


@router.get("/export")
async def export_sensor_data(
    well_id: Optional[str] = Query(None),
    sensor_type: Optional[str] = Query(None),
    start_time: Optional[datetime] = Query(None),
    end_time: Optional[datetime] = Query(None),
    format: str = Query("csv", regex="^(csv|json|parquet)$"),
    limit: int = Query(10000, ge=1, le=100000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Export sensor data in various formats"""
    if not has_permission(current_user.role, Permission.VIEW_SENSOR_DATA):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied"
        )
    
    from fastapi.responses import StreamingResponse, Response
    import pandas as pd
    import io
    
    service = SensorService(db=db)
    readings = await service.get_readings(
        well_id=well_id,
        sensor_type=sensor_type,
        start_time=start_time,
        end_time=end_time,
        limit=limit,
    )
    
    if not readings:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No data found"
        )
    
    # Convert to DataFrame
    data = [r.dict() for r in readings]
    df = pd.DataFrame(data)
    
    # Export based on format
    if format == "csv":
        output = io.StringIO()
        df.to_csv(output, index=False)
        output.seek(0)
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=sensor_data_{datetime.utcnow().strftime('%Y%m%d')}.csv"}
        )
    
    elif format == "json":
        return Response(
            content=df.to_json(orient="records", date_format="iso"),
            media_type="application/json",
            headers={"Content-Disposition": f"attachment; filename=sensor_data_{datetime.utcnow().strftime('%Y%m%d')}.json"}
        )
    
    elif format == "parquet":
        output = io.BytesIO()
        df.to_parquet(output, index=False)
        output.seek(0)
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="application/octet-stream",
            headers={"Content-Disposition": f"attachment; filename=sensor_data_{datetime.utcnow().strftime('%Y%m%d')}.parquet"}
        )
