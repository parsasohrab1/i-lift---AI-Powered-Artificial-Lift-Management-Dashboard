"""
Alert service for managing alerts
"""
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import desc, func, and_, or_

from app.schemas.alert import Alert, AlertResponse
from app.models.alert import Alert as AlertModel
from app.core.database import get_db
from app.core.redis_client import redis_client
from app.utils.logger import setup_logging

logger = setup_logging()


class AlertService:
    """Service for alert operations"""
    
    def __init__(self, db: Session = None):
        if db:
            self.db = db
        else:
            self.db = next(get_db())
    
    async def get_alerts(
        self,
        well_id: Optional[str] = None,
        severity: Optional[str] = None,
        resolved: Optional[bool] = None,
        alert_type: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[AlertResponse]:
        """Get alerts with filters"""
        try:
            query = self.db.query(AlertModel)
            
            # Apply filters
            if well_id:
                query = query.filter(AlertModel.well_id == well_id)
            if severity:
                query = query.filter(AlertModel.severity == severity)
            if resolved is not None:
                query = query.filter(AlertModel.resolved == resolved)
            if alert_type:
                query = query.filter(AlertModel.alert_type == alert_type)
            if start_time:
                query = query.filter(AlertModel.created_at >= start_time)
            if end_time:
                query = query.filter(AlertModel.created_at <= end_time)
            
            # Order by created_at descending (newest first)
            query = query.order_by(desc(AlertModel.created_at))
            
            # Apply pagination
            alerts = query.offset(offset).limit(limit).all()
            
            return [AlertResponse.model_validate(a) for a in alerts]
            
        except Exception as e:
            logger.error("Error getting alerts", error=str(e))
            raise
    
    async def create_alert(self, alert: Alert) -> AlertResponse:
        """Create a new alert"""
        try:
            import uuid
            
            db_alert = AlertModel(
                alert_id=uuid.uuid4(),
                well_id=alert.well_id,
                alert_type=alert.alert_type,
                severity=alert.severity,
                message=alert.message,
                sensor_type=alert.sensor_type,
                resolved=False,
                created_at=datetime.utcnow(),
            )
            
            self.db.add(db_alert)
            self.db.commit()
            self.db.refresh(db_alert)
            
            # Invalidate cache
            redis_client.delete("alerts:unresolved")
            redis_client.delete(f"alerts:well:{alert.well_id}")
            
            # Log alert creation
            logger.info(
                "Alert created",
                alert_id=str(db_alert.alert_id),
                well_id=alert.well_id,
                severity=alert.severity,
                alert_type=alert.alert_type,
            )
            
            return AlertResponse.model_validate(db_alert)
            
        except Exception as e:
            self.db.rollback()
            logger.error("Error creating alert", error=str(e))
            raise
    
    async def resolve_alert(
        self,
        alert_id: str,
        resolved_by: Optional[str] = None,
    ) -> AlertResponse:
        """Resolve an alert"""
        try:
            alert = self.db.query(AlertModel).filter(AlertModel.alert_id == alert_id).first()
            
            if not alert:
                raise ValueError(f"Alert {alert_id} not found")
            
            if alert.resolved:
                raise ValueError(f"Alert {alert_id} is already resolved")
            
            alert.resolved = True
            alert.resolved_at = datetime.utcnow()
            
            self.db.commit()
            self.db.refresh(alert)
            
            # Invalidate cache
            redis_client.delete("alerts:unresolved")
            redis_client.delete(f"alerts:well:{alert.well_id}")
            
            logger.info(
                "Alert resolved",
                alert_id=alert_id,
                resolved_by=resolved_by,
            )
            
            return AlertResponse.model_validate(alert)
            
        except Exception as e:
            self.db.rollback()
            logger.error("Error resolving alert", error=str(e))
            raise
    
    async def get_unresolved_alerts(
        self,
        well_id: Optional[str] = None,
        severity: Optional[str] = None,
    ) -> List[AlertResponse]:
        """Get unresolved alerts (cached)"""
        try:
            cache_key = f"alerts:unresolved"
            if well_id:
                cache_key += f":{well_id}"
            if severity:
                cache_key += f":{severity}"
            
            # Try cache first
            cached = redis_client.get(cache_key)
            if cached:
                return cached
            
            # Get from database
            alerts = await self.get_alerts(
                well_id=well_id,
                severity=severity,
                resolved=False,
                limit=1000,
            )
            
            # Cache for 30 seconds
            redis_client.set(cache_key, alerts, ttl=30)
            
            return alerts
            
        except Exception as e:
            logger.error("Error getting unresolved alerts", error=str(e))
            raise
    
    async def get_alert_statistics(
        self,
        well_id: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """Get alert statistics"""
        try:
            if not end_time:
                end_time = datetime.utcnow()
            if not start_time:
                start_time = end_time - timedelta(days=30)
            
            query = self.db.query(AlertModel).filter(
                AlertModel.created_at >= start_time,
                AlertModel.created_at <= end_time,
            )
            
            if well_id:
                query = query.filter(AlertModel.well_id == well_id)
            
            alerts = query.all()
            
            # Calculate statistics
            total_alerts = len(alerts)
            resolved_count = sum(1 for a in alerts if a.resolved)
            unresolved_count = total_alerts - resolved_count
            
            # Count by severity
            severity_counts = {}
            for alert in alerts:
                severity_counts[alert.severity] = severity_counts.get(alert.severity, 0) + 1
            
            # Count by type
            type_counts = {}
            for alert in alerts:
                type_counts[alert.alert_type] = type_counts.get(alert.alert_type, 0) + 1
            
            # Count by well
            well_counts = {}
            for alert in alerts:
                well_counts[alert.well_id] = well_counts.get(alert.well_id, 0) + 1
            
            # Average resolution time
            resolved_alerts = [a for a in alerts if a.resolved and a.resolved_at]
            avg_resolution_time = None
            if resolved_alerts:
                resolution_times = [
                    (a.resolved_at - a.created_at).total_seconds() / 3600  # hours
                    for a in resolved_alerts
                ]
                avg_resolution_time = sum(resolution_times) / len(resolution_times)
            
            return {
                'total_alerts': total_alerts,
                'resolved_count': resolved_count,
                'unresolved_count': unresolved_count,
                'resolution_rate': (resolved_count / total_alerts * 100) if total_alerts > 0 else 0,
                'severity_distribution': severity_counts,
                'type_distribution': type_counts,
                'well_distribution': well_counts,
                'average_resolution_time_hours': avg_resolution_time,
                'time_range': {
                    'start': start_time.isoformat(),
                    'end': end_time.isoformat(),
                },
            }
            
        except Exception as e:
            logger.error("Error getting alert statistics", error=str(e))
            raise
    
    async def get_critical_alerts(
        self,
        well_id: Optional[str] = None,
    ) -> List[AlertResponse]:
        """Get critical alerts (unresolved)"""
        try:
            alerts = await self.get_alerts(
                well_id=well_id,
                severity='critical',
                resolved=False,
                limit=100,
            )
            
            return alerts
            
        except Exception as e:
            logger.error("Error getting critical alerts", error=str(e))
            raise
    
    async def bulk_resolve_alerts(
        self,
        alert_ids: List[str],
        resolved_by: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Bulk resolve alerts"""
        try:
            resolved_count = 0
            failed_count = 0
            failed_ids = []
            
            for alert_id in alert_ids:
                try:
                    await self.resolve_alert(alert_id, resolved_by)
                    resolved_count += 1
                except Exception as e:
                    failed_count += 1
                    failed_ids.append(alert_id)
                    logger.warning(f"Failed to resolve alert {alert_id}: {e}")
            
            return {
                'total': len(alert_ids),
                'resolved': resolved_count,
                'failed': failed_count,
                'failed_ids': failed_ids,
            }
            
        except Exception as e:
            logger.error("Error bulk resolving alerts", error=str(e))
            raise
    
    async def delete_alert(self, alert_id: str) -> bool:
        """Delete an alert (admin only)"""
        try:
            alert = self.db.query(AlertModel).filter(AlertModel.alert_id == alert_id).first()
            
            if not alert:
                raise ValueError(f"Alert {alert_id} not found")
            
            self.db.delete(alert)
            self.db.commit()
            
            # Invalidate cache
            redis_client.delete("alerts:unresolved")
            redis_client.delete(f"alerts:well:{alert.well_id}")
            
            logger.info("Alert deleted", alert_id=alert_id)
            
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error("Error deleting alert", error=str(e))
            raise
