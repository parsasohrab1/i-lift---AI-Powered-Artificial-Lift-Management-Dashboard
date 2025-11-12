"""
Notification endpoints
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_active_user
from app.core.permissions import Permission, has_permission
from app.models.user import User
from app.schemas.notification import (
    NotificationRequest,
    NotificationResponse,
    NotificationPreferences,
)
from app.services.notification_service import NotificationService, NotificationChannel
from app.services.alert_service import AlertService

router = APIRouter()


@router.post("/send", response_model=NotificationResponse)
async def send_notification(
    request: NotificationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Send notification for an alert"""
    if not has_permission(current_user.role, Permission.CREATE_ALERTS):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied"
        )
    
    # Get alert
    alert_service = AlertService(db=db)
    from app.models.alert import Alert as AlertModel
    alert = db.query(AlertModel).filter(AlertModel.alert_id == request.alert_id).first()
    
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found"
        )
    
    # Convert channels
    channels = [NotificationChannel(ch) for ch in request.channels]
    
    # Send notification
    notification_service = NotificationService()
    alert_dict = {
        'alert_id': str(alert.alert_id),
        'well_id': alert.well_id,
        'alert_type': alert.alert_type,
        'severity': alert.severity,
        'message': alert.message,
        'sensor_type': alert.sensor_type,
        'created_at': alert.created_at.isoformat(),
    }
    
    result = await notification_service.send_notification(
        alert=alert_dict,
        channels=channels,
        recipients=request.recipients,
    )
    
    return NotificationResponse(**result)


@router.get("/preferences", response_model=NotificationPreferences)
async def get_notification_preferences(
    current_user: User = Depends(get_current_active_user),
):
    """Get user notification preferences"""
    # TODO: Load from database
    return NotificationPreferences(
        user_id=str(current_user.id),
        email_enabled=True,
        sms_enabled=False,
        push_enabled=True,
        webhook_enabled=False,
    )


@router.put("/preferences", response_model=NotificationPreferences)
async def update_notification_preferences(
    preferences: NotificationPreferences,
    current_user: User = Depends(get_current_active_user),
):
    """Update user notification preferences"""
    # TODO: Save to database
    return preferences

