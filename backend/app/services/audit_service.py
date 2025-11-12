"""
Audit Logging Service
Records all security-relevant events for compliance
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import desc
from enum import Enum
import uuid

from app.core.database import get_db
from app.utils.logger import setup_logging

logger = setup_logging()


class AuditEventType(str, Enum):
    """Types of audit events"""
    # Authentication
    LOGIN = "login"
    LOGOUT = "logout"
    LOGIN_FAILED = "login_failed"
    PASSWORD_CHANGE = "password_change"
    TOKEN_REFRESH = "token_refresh"
    
    # Data Access
    DATA_VIEW = "data_view"
    DATA_CREATE = "data_create"
    DATA_UPDATE = "data_update"
    DATA_DELETE = "data_delete"
    DATA_EXPORT = "data_export"
    
    # User Management
    USER_CREATE = "user_create"
    USER_UPDATE = "user_update"
    USER_DELETE = "user_delete"
    ROLE_CHANGE = "role_change"
    
    # System
    CONFIG_CHANGE = "config_change"
    ALERT_CREATE = "alert_create"
    ALERT_RESOLVE = "alert_resolve"
    MODEL_TRAIN = "model_train"
    
    # Security
    PERMISSION_DENIED = "permission_denied"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"


class AuditService:
    """Service for audit logging"""
    
    def __init__(self, db: Session = None):
        if db:
            self.db = db
        else:
            self.db = next(get_db())
    
    async def log_event(
        self,
        event_type: AuditEventType,
        user_id: Optional[str] = None,
        username: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        action: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        success: bool = True,
    ):
        """Log an audit event"""
        try:
            from app.models.audit import AuditLog
            
            audit_log = AuditLog(
                audit_id=uuid.uuid4(),
                event_type=event_type.value,
                user_id=user_id,
                username=username,
                resource_type=resource_type,
                resource_id=resource_id,
                action=action,
                details=details or {},
                ip_address=ip_address,
                user_agent=user_agent,
                success=success,
                timestamp=datetime.utcnow(),
            )
            
            self.db.add(audit_log)
            self.db.commit()
            
            # Also log to structured logger
            logger.info(
                "Audit event",
                event_type=event_type.value,
                user_id=user_id,
                username=username,
                resource_type=resource_type,
                resource_id=resource_id,
                action=action,
                success=success,
            )
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error logging audit event: {e}")
    
    async def get_audit_logs(
        self,
        user_id: Optional[str] = None,
        event_type: Optional[AuditEventType] = None,
        resource_type: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        """Get audit logs with filters"""
        try:
            from app.models.audit import AuditLog
            
            query = self.db.query(AuditLog)
            
            if user_id:
                query = query.filter(AuditLog.user_id == user_id)
            if event_type:
                query = query.filter(AuditLog.event_type == event_type.value)
            if resource_type:
                query = query.filter(AuditLog.resource_type == resource_type)
            if start_time:
                query = query.filter(AuditLog.timestamp >= start_time)
            if end_time:
                query = query.filter(AuditLog.timestamp <= end_time)
            
            query = query.order_by(desc(AuditLog.timestamp))
            logs = query.offset(offset).limit(limit).all()
            
            return [
                {
                    'audit_id': str(log.audit_id),
                    'event_type': log.event_type,
                    'user_id': log.user_id,
                    'username': log.username,
                    'resource_type': log.resource_type,
                    'resource_id': log.resource_id,
                    'action': log.action,
                    'details': log.details,
                    'ip_address': log.ip_address,
                    'user_agent': log.user_agent,
                    'success': log.success,
                    'timestamp': log.timestamp.isoformat(),
                }
                for log in logs
            ]
            
        except Exception as e:
            logger.error(f"Error getting audit logs: {e}")
            return []
    
    async def get_user_activity(
        self,
        user_id: str,
        days: int = 30,
    ) -> Dict[str, Any]:
        """Get user activity summary"""
        try:
            from app.models.audit import AuditLog
            from datetime import timedelta
            
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(days=days)
            
            logs = self.db.query(AuditLog).filter(
                AuditLog.user_id == user_id,
                AuditLog.timestamp >= start_time,
                AuditLog.timestamp <= end_time,
            ).all()
            
            # Count by event type
            event_counts = {}
            for log in logs:
                event_counts[log.event_type] = event_counts.get(log.event_type, 0) + 1
            
            # Count by resource type
            resource_counts = {}
            for log in logs:
                if log.resource_type:
                    resource_counts[log.resource_type] = resource_counts.get(log.resource_type, 0) + 1
            
            return {
                'user_id': user_id,
                'total_events': len(logs),
                'event_counts': event_counts,
                'resource_counts': resource_counts,
                'time_range': {
                    'start': start_time.isoformat(),
                    'end': end_time.isoformat(),
                },
            }
            
        except Exception as e:
            logger.error(f"Error getting user activity: {e}")
            return {}
    
    async def detect_suspicious_activity(
        self,
        user_id: Optional[str] = None,
        hours: int = 24,
    ) -> List[Dict[str, Any]]:
        """Detect suspicious activity patterns"""
        try:
            from app.models.audit import AuditLog
            from datetime import timedelta
            
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(hours=hours)
            
            query = self.db.query(AuditLog).filter(
                AuditLog.timestamp >= start_time,
            )
            
            if user_id:
                query = query.filter(AuditLog.user_id == user_id)
            
            logs = query.all()
            
            suspicious = []
            
            # Check for multiple failed logins
            failed_logins = [
                log for log in logs
                if log.event_type == AuditEventType.LOGIN_FAILED.value
            ]
            if len(failed_logins) >= 5:
                suspicious.append({
                    'type': 'multiple_failed_logins',
                    'count': len(failed_logins),
                    'user_id': user_id,
                    'time_range': {
                        'start': start_time.isoformat(),
                        'end': end_time.isoformat(),
                    },
                })
            
            # Check for permission denied events
            permission_denied = [
                log for log in logs
                if log.event_type == AuditEventType.PERMISSION_DENIED.value
            ]
            if len(permission_denied) >= 10:
                suspicious.append({
                    'type': 'excessive_permission_denials',
                    'count': len(permission_denied),
                    'user_id': user_id,
                    'time_range': {
                        'start': start_time.isoformat(),
                        'end': end_time.isoformat(),
                    },
                })
            
            # Check for unusual access patterns
            if user_id:
                user_logs = [log for log in logs if log.user_id == user_id]
                if len(user_logs) > 1000:  # More than 1000 events in 24 hours
                    suspicious.append({
                        'type': 'unusual_activity_volume',
                        'count': len(user_logs),
                        'user_id': user_id,
                        'time_range': {
                            'start': start_time.isoformat(),
                            'end': end_time.isoformat(),
                        },
                    })
            
            return suspicious
            
        except Exception as e:
            logger.error(f"Error detecting suspicious activity: {e}")
            return []

