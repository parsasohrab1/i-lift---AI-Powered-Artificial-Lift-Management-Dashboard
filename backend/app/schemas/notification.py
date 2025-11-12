"""
Notification schemas
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class NotificationRequest(BaseModel):
    """Notification request schema"""
    alert_id: str
    channels: List[str] = Field(..., description="Notification channels: email, sms, push, webhook")
    recipients: Optional[List[str]] = Field(None, description="Recipient list (optional)")


class NotificationResponse(BaseModel):
    """Notification response schema"""
    alert_id: str
    channels: Dict[str, Dict[str, Any]]
    sent_at: str


class NotificationPreferences(BaseModel):
    """User notification preferences"""
    user_id: str
    email_enabled: bool = True
    sms_enabled: bool = False
    push_enabled: bool = True
    webhook_enabled: bool = False
    email_recipients: Optional[List[str]] = None
    sms_recipients: Optional[List[str]] = None
    webhook_urls: Optional[List[str]] = None
    critical_alerts_only: bool = False

