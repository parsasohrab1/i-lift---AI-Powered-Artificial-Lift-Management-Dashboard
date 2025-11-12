"""
Data processing pipeline endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_active_user, get_current_admin_user
from app.core.permissions import Permission, has_permission
from app.models.user import User
from app.services.processing.pipeline import DataProcessingPipeline

router = APIRouter()

# Global pipeline instance
pipeline: DataProcessingPipeline = None


def get_pipeline() -> DataProcessingPipeline:
    """Get or create pipeline instance"""
    global pipeline
    if pipeline is None:
        pipeline = DataProcessingPipeline()
    return pipeline


@router.post("/start")
async def start_pipeline(
    current_user: User = Depends(get_current_admin_user),
):
    """Start the data processing pipeline (admin only)"""
    if not has_permission(current_user.role, Permission.SYSTEM_ADMIN):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied: Admin access required"
        )
    
    try:
        pipeline = get_pipeline()
        pipeline.start()
        
        return {
            "message": "Processing pipeline started",
            "status": "running"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start pipeline: {str(e)}"
        )


@router.post("/stop")
async def stop_pipeline(
    current_user: User = Depends(get_current_admin_user),
):
    """Stop the data processing pipeline (admin only)"""
    if not has_permission(current_user.role, Permission.SYSTEM_ADMIN):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied: Admin access required"
        )
    
    try:
        pipeline = get_pipeline()
        pipeline.stop()
        
        return {
            "message": "Processing pipeline stopped",
            "status": "stopped"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to stop pipeline: {str(e)}"
        )


@router.post("/pause")
async def pause_pipeline(
    current_user: User = Depends(get_current_admin_user),
):
    """Pause the data processing pipeline (admin only)"""
    if not has_permission(current_user.role, Permission.SYSTEM_ADMIN):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied: Admin access required"
        )
    
    try:
        pipeline = get_pipeline()
        pipeline.pause()
        
        return {
            "message": "Processing pipeline paused",
            "status": "paused"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to pause pipeline: {str(e)}"
        )


@router.post("/resume")
async def resume_pipeline(
    current_user: User = Depends(get_current_admin_user),
):
    """Resume the data processing pipeline (admin only)"""
    if not has_permission(current_user.role, Permission.SYSTEM_ADMIN):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied: Admin access required"
        )
    
    try:
        pipeline = get_pipeline()
        pipeline.resume()
        
        return {
            "message": "Processing pipeline resumed",
            "status": "running"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to resume pipeline: {str(e)}"
        )


@router.get("/stats")
async def get_pipeline_stats(
    current_user: User = Depends(get_current_active_user),
):
    """Get processing pipeline statistics"""
    if not has_permission(current_user.role, Permission.VIEW_SENSOR_DATA):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied"
        )
    
    try:
        pipeline = get_pipeline()
        stats = pipeline.get_stats()
        return stats
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get stats: {str(e)}"
        )


@router.get("/health")
async def pipeline_health_check(
    current_user: User = Depends(get_current_active_user),
):
    """Health check for processing pipeline"""
    try:
        pipeline = get_pipeline()
        health = pipeline.health_check()
        return health
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Health check failed: {str(e)}"
        )

