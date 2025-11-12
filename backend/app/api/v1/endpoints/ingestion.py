"""
Data ingestion endpoints (REST API)
"""
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_active_user
from app.core.permissions import Permission, has_permission
from app.models.user import User
from app.services.ingestion.ingestion_service import IngestionService
from app.schemas.ingestion import (
    SensorDataIngest,
    BatchSensorDataIngest,
    IngestionResponse,
    IngestionStatsResponse,
)

router = APIRouter()

# Global ingestion service instance
ingestion_service = IngestionService()


@router.on_event("startup")
async def startup_ingestion():
    """Initialize ingestion service on startup"""
    ingestion_service.initialize()


@router.on_event("shutdown")
async def shutdown_ingestion():
    """Shutdown ingestion service on shutdown"""
    ingestion_service.shutdown()


@router.post("/sensor", response_model=IngestionResponse)
async def ingest_sensor_data(
    data: SensorDataIngest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Ingest single sensor reading via REST API"""
    # Check permission
    if not has_permission(current_user.role, Permission.CREATE_SENSOR_DATA):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied: CREATE_SENSOR_DATA required"
        )
    
    try:
        # Convert to dict
        data_dict = data.dict()
        data_dict['_metadata'] = {
            'source': 'rest',
            'ingested_by': current_user.username,
        }
        
        # Ingest data
        result = ingestion_service.ingest_rest_data(data_dict)
        
        return IngestionResponse(
            success=result['errors'] == 0,
            message="Data ingested successfully" if result['errors'] == 0 else "Data ingested with errors",
            ingested_count=result['sent_to_kafka'],
            error_count=result['errors'],
            errors=result['errors_detail'] if result['errors_detail'] else None,
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error ingesting data: {str(e)}"
        )


@router.post("/sensor/batch", response_model=IngestionResponse)
async def ingest_batch_sensor_data(
    data: BatchSensorDataIngest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Ingest batch of sensor readings via REST API"""
    # Check permission
    if not has_permission(current_user.role, Permission.CREATE_SENSOR_DATA):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied: CREATE_SENSOR_DATA required"
        )
    
    try:
        # Convert to list of dicts
        data_list = [item.dict() for item in data.readings]
        
        # Add metadata
        for item in data_list:
            item['_metadata'] = {
                'source': 'rest',
                'ingested_by': current_user.username,
            }
        
        # Ingest data
        result = ingestion_service.ingest_rest_data(data_list)
        
        return IngestionResponse(
            success=result['errors'] == 0,
            message=f"Batch ingested: {result['sent_to_kafka']} successful, {result['errors']} errors",
            ingested_count=result['sent_to_kafka'],
            error_count=result['errors'],
            errors=result['errors_detail'] if result['errors_detail'] else None,
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error ingesting batch data: {str(e)}"
        )


@router.post("/raw", response_model=IngestionResponse)
async def ingest_raw_data(
    data: Dict[str, Any] = Body(...),
    current_user: User = Depends(get_current_active_user),
):
    """Ingest raw data in any format (will be normalized)"""
    # Check permission
    if not has_permission(current_user.role, Permission.CREATE_SENSOR_DATA):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied: CREATE_SENSOR_DATA required"
        )
    
    try:
        # Add metadata
        if '_metadata' not in data:
            data['_metadata'] = {}
        data['_metadata']['source'] = 'rest'
        data['_metadata']['ingested_by'] = current_user.username
        
        # Ingest data
        result = ingestion_service.ingest_rest_data(data)
        
        return IngestionResponse(
            success=result['errors'] == 0,
            message="Raw data ingested successfully" if result['errors'] == 0 else "Raw data ingested with errors",
            ingested_count=result['sent_to_kafka'],
            error_count=result['errors'],
            errors=result['errors_detail'] if result['errors_detail'] else None,
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error ingesting raw data: {str(e)}"
        )


@router.get("/stats", response_model=IngestionStatsResponse)
async def get_ingestion_stats(
    current_user: User = Depends(get_current_active_user),
):
    """Get ingestion statistics"""
    # Check permission
    if not has_permission(current_user.role, Permission.VIEW_SENSOR_DATA):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied"
        )
    
    stats = ingestion_service.get_stats()
    return IngestionStatsResponse(**stats)

