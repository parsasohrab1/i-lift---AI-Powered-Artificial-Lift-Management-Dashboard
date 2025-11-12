"""
Monitoring and observability endpoints
"""
from typing import Optional, List
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_active_user, get_current_admin_user
from app.models.user import User
from app.services.metrics_service import metrics_service
from app.services.health_service import health_service
from app.utils.logger import setup_logging

logger = setup_logging()

router = APIRouter()


@router.get("/metrics")
async def get_prometheus_metrics(
    current_user: User = Depends(get_current_admin_user)
):
    """Get Prometheus metrics (admin only)"""
    from fastapi.responses import Response
    
    metrics_data = metrics_service.get_prometheus_metrics()
    return Response(
        content=metrics_data,
        media_type="text/plain; version=0.0.4"
    )


@router.get("/health")
async def health_check():
    """Basic health check endpoint (public)"""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}


@router.get("/health/detailed")
async def detailed_health_check(
    include_system: bool = Query(False, description="Include system resources"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Detailed health check for all services"""
    health = await health_service.get_overall_health(
        db=db,
        include_details=include_system
    )
    return health


@router.get("/health/summary")
async def health_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get health summary for dashboard"""
    summary = await health_service.get_health_summary(db=db)
    return summary


@router.get("/metrics/summary")
async def get_metrics_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get metrics summary"""
    summary = metrics_service.get_metrics_summary(db=db)
    return summary


@router.get("/metrics/requests")
async def get_request_metrics(
    hours: int = Query(24, ge=1, le=168, description="Hours to look back"),
    endpoint: Optional[str] = Query(None, description="Filter by endpoint"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Get HTTP request metrics (admin only)"""
    # In production, this would query from a metrics database
    # For now, return a placeholder
    return {
        "total_requests": 0,
        "requests_by_method": {},
        "requests_by_endpoint": {},
        "requests_by_status": {},
        "average_response_time_ms": 0,
        "p95_response_time_ms": 0,
        "p99_response_time_ms": 0,
        "time_range": {
            "start": (datetime.utcnow() - timedelta(hours=hours)).isoformat(),
            "end": datetime.utcnow().isoformat()
        }
    }


@router.get("/metrics/business")
async def get_business_metrics(
    hours: int = Query(24, ge=1, le=168, description="Hours to look back"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get business metrics"""
    from sqlalchemy import text
    
    try:
        # Get sensor readings count
        readings_count = db.execute(
            text("""
                SELECT COUNT(*) 
                FROM sensor_readings 
                WHERE timestamp >= NOW() - INTERVAL ':hours hours'
            """).bindparam(hours=hours)
        ).scalar()
        
        # Get alerts count
        alerts_count = db.execute(
            text("""
                SELECT COUNT(*) 
                FROM alerts 
                WHERE created_at >= NOW() - INTERVAL ':hours hours'
            """).bindparam(hours=hours)
        ).scalar()
        
        # Get ML predictions count
        predictions_count = db.execute(
            text("""
                SELECT COUNT(*) 
                FROM ml_predictions 
                WHERE created_at >= NOW() - INTERVAL ':hours hours'
            """).bindparam(hours=hours)
        ).scalar()
        
        # Get active wells
        active_wells = db.execute(
            text("SELECT COUNT(*) FROM wells WHERE is_active = true")
        ).scalar()
        
        return {
            "sensor_readings": readings_count or 0,
            "alerts": alerts_count or 0,
            "ml_predictions": predictions_count or 0,
            "active_wells": active_wells or 0,
            "time_range": {
                "start": (datetime.utcnow() - timedelta(hours=hours)).isoformat(),
                "end": datetime.utcnow().isoformat()
            }
        }
    except Exception as e:
        logger.error(f"Error getting business metrics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving business metrics"
        )


@router.get("/metrics/system")
async def get_system_metrics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Get system metrics (admin only)"""
    system_health = await health_service.check_system_resources()
    return system_health


@router.get("/logs")
async def get_logs(
    level: Optional[str] = Query(None, description="Filter by log level"),
    hours: int = Query(24, ge=1, le=168, description="Hours to look back"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of logs"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Get application logs (admin only)"""
    # In production, this would query from a log aggregation system (ELK, Loki, etc.)
    # For now, return a placeholder
    return {
        "logs": [],
        "total": 0,
        "time_range": {
            "start": (datetime.utcnow() - timedelta(hours=hours)).isoformat(),
            "end": datetime.utcnow().isoformat()
        }
    }


@router.get("/tracing")
async def get_traces(
    trace_id: Optional[str] = Query(None, description="Filter by trace ID"),
    service: Optional[str] = Query(None, description="Filter by service"),
    hours: int = Query(1, ge=1, le=24, description="Hours to look back"),
    limit: int = Query(50, ge=1, le=500, description="Maximum number of traces"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Get distributed traces (admin only)"""
    # In production, this would query from a tracing system (Jaeger, Zipkin, etc.)
    # For now, return a placeholder
    return {
        "traces": [],
        "total": 0,
        "time_range": {
            "start": (datetime.utcnow() - timedelta(hours=hours)).isoformat(),
            "end": datetime.utcnow().isoformat()
        }
    }

