"""
Alert endpoints
"""
from typing import List, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_active_user, get_current_admin_user
from app.core.permissions import Permission, has_permission
from app.models.user import User
from app.schemas.alert import (
    Alert,
    AlertResponse,
    AlertListResponse,
    AlertStatisticsResponse,
    BulkResolveRequest,
    BulkResolveResponse,
)
from app.services.alert_service import AlertService

router = APIRouter()


@router.get("/", response_model=AlertListResponse)
async def get_alerts(
    well_id: Optional[str] = Query(None, description="Filter by well ID"),
    severity: Optional[str] = Query(None, regex="^(low|medium|high|critical)$", description="Filter by severity"),
    resolved: Optional[bool] = Query(None, description="Filter by resolved status"),
    alert_type: Optional[str] = Query(None, description="Filter by alert type"),
    start_time: Optional[datetime] = Query(None, description="Start time filter"),
    end_time: Optional[datetime] = Query(None, description="End time filter"),
    limit: int = Query(100, ge=1, le=1000, description="Number of alerts to return"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get alerts with filters and pagination"""
    if not has_permission(current_user.role, Permission.VIEW_ALERTS):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied: VIEW_ALERTS required"
        )
    
    service = AlertService(db=db)
    alerts = await service.get_alerts(
        well_id=well_id,
        severity=severity,
        resolved=resolved,
        alert_type=alert_type,
        start_time=start_time,
        end_time=end_time,
        limit=limit,
        offset=offset,
    )
    
    # Get total count (simplified - in production use separate count query)
    total = len(alerts)  # This is approximate
    
    return AlertListResponse(
        alerts=alerts,
        total=total,
        offset=offset,
        limit=limit,
    )


@router.get("/unresolved", response_model=List[AlertResponse])
async def get_unresolved_alerts(
    well_id: Optional[str] = Query(None, description="Filter by well ID"),
    severity: Optional[str] = Query(None, regex="^(low|medium|high|critical)$", description="Filter by severity"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get unresolved alerts (cached)"""
    if not has_permission(current_user.role, Permission.VIEW_ALERTS):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied"
        )
    
    service = AlertService(db=db)
    alerts = await service.get_unresolved_alerts(
        well_id=well_id,
        severity=severity,
    )
    
    return alerts


@router.get("/critical", response_model=List[AlertResponse])
async def get_critical_alerts(
    well_id: Optional[str] = Query(None, description="Filter by well ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get critical unresolved alerts"""
    if not has_permission(current_user.role, Permission.VIEW_ALERTS):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied"
        )
    
    service = AlertService(db=db)
    alerts = await service.get_critical_alerts(well_id=well_id)
    
    return alerts


@router.get("/{alert_id}", response_model=AlertResponse)
async def get_alert(
    alert_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get alert by ID"""
    if not has_permission(current_user.role, Permission.VIEW_ALERTS):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied"
        )
    
    from app.models.alert import Alert as AlertModel
    
    alert = db.query(AlertModel).filter(AlertModel.alert_id == alert_id).first()
    
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found"
        )
    
    return AlertResponse.model_validate(alert)


@router.post("/", response_model=AlertResponse)
async def create_alert(
    alert: Alert,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Create a new alert"""
    if not has_permission(current_user.role, Permission.CREATE_ALERTS):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied: CREATE_ALERTS required"
        )
    
    # Validate severity
    valid_severities = ['low', 'medium', 'high', 'critical']
    if alert.severity not in valid_severities:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid severity. Must be one of: {', '.join(valid_severities)}"
        )
    
    service = AlertService(db=db)
    return await service.create_alert(alert)


@router.post("/{alert_id}/resolve", response_model=AlertResponse)
async def resolve_alert(
    alert_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Resolve an alert"""
    if not has_permission(current_user.role, Permission.RESOLVE_ALERTS):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied: RESOLVE_ALERTS required"
        )
    
    service = AlertService(db=db)
    
    try:
        return await service.resolve_alert(alert_id, resolved_by=current_user.username)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.post("/bulk-resolve", response_model=BulkResolveResponse)
async def bulk_resolve_alerts(
    request: BulkResolveRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Bulk resolve multiple alerts"""
    if not has_permission(current_user.role, Permission.RESOLVE_ALERTS):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied: RESOLVE_ALERTS required"
        )
    
    if len(request.alert_ids) > 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum 100 alerts can be resolved at once"
        )
    
    service = AlertService(db=db)
    result = await service.bulk_resolve_alerts(
        request.alert_ids,
        resolved_by=request.resolved_by or current_user.username,
    )
    
    return BulkResolveResponse(**result)


@router.delete("/{alert_id}")
async def delete_alert(
    alert_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    """Delete an alert (admin only)"""
    service = AlertService(db=db)
    
    try:
        await service.delete_alert(alert_id)
        return {"message": "Alert deleted successfully"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.get("/statistics/summary", response_model=AlertStatisticsResponse)
async def get_alert_statistics(
    well_id: Optional[str] = Query(None, description="Filter by well ID"),
    start_time: Optional[datetime] = Query(None, description="Start time"),
    end_time: Optional[datetime] = Query(None, description="End time"),
    days: int = Query(30, ge=1, le=365, description="Number of days (if start_time not provided)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get alert statistics"""
    if not has_permission(current_user.role, Permission.VIEW_ALERTS):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied"
        )
    
    if not end_time:
        end_time = datetime.utcnow()
    if not start_time:
        start_time = end_time - timedelta(days=days)
    
    service = AlertService(db=db)
    stats = await service.get_alert_statistics(
        well_id=well_id,
        start_time=start_time,
        end_time=end_time,
    )
    
    return AlertStatisticsResponse(**stats)


@router.get("/realtime/count")
async def get_realtime_alert_count(
    well_id: Optional[str] = Query(None, description="Filter by well ID"),
    severity: Optional[str] = Query(None, regex="^(low|medium|high|critical)$", description="Filter by severity"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get real-time alert count (cached)"""
    if not has_permission(current_user.role, Permission.VIEW_ALERTS):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied"
        )
    
    service = AlertService(db=db)
    alerts = await service.get_unresolved_alerts(
        well_id=well_id,
        severity=severity,
    )
    
    # Count by severity
    severity_counts = {}
    for alert in alerts:
        severity_counts[alert.severity] = severity_counts.get(alert.severity, 0) + 1
    
    return {
        "total": len(alerts),
        "by_severity": severity_counts,
        "timestamp": datetime.utcnow().isoformat(),
    }
