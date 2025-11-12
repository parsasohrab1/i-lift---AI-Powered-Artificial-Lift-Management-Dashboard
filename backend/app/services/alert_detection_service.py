"""
Alert Detection Service
Monitors sensor data and triggers alerts
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
import asyncio

from app.services.alert_rules import AlertRulesEngine
from app.services.alert_service import AlertService
from app.services.notification_service import NotificationService, NotificationChannel
from app.models.sensor import SensorReading as SensorReadingModel
from app.core.database import get_db
from app.utils.logger import setup_logging

logger = setup_logging()


class AlertDetectionService:
    """Service for detecting and creating alerts from sensor data"""
    
    def __init__(self, db: Session = None):
        self.db = db or next(get_db())
        self.rules_engine = AlertRulesEngine()
        self.alert_service = AlertService(db=self.db)
        self.notification_service = NotificationService()
        self.is_running = False
    
    async def process_sensor_reading(
        self,
        reading: SensorReadingModel,
    ) -> List[Dict[str, Any]]:
        """Process a sensor reading and create alerts if needed"""
        try:
            # Evaluate reading against alert rules
            triggered_alerts = self.rules_engine.evaluate_sensor_reading(
                well_id=reading.well_id,
                sensor_type=reading.sensor_type,
                sensor_value=reading.sensor_value,
            )
            
            created_alerts = []
            
            for alert_data in triggered_alerts:
                # Check if similar alert already exists (avoid duplicates)
                existing_alert = await self._check_existing_alert(
                    well_id=alert_data['well_id'],
                    alert_type=alert_data['alert_type'],
                    severity=alert_data['severity'],
                )
                
                if not existing_alert:
                    # Create alert
                    from app.schemas.alert import Alert
                    
                    alert = Alert(
                        well_id=alert_data['well_id'],
                        alert_type=alert_data['alert_type'],
                        severity=alert_data['severity'],
                        message=alert_data['message'],
                        sensor_type=alert_data['sensor_type'],
                    )
                    
                    created_alert = await self.alert_service.create_alert(alert)
                    created_alerts.append(created_alert)
                    
                    # Send notifications for critical and high severity alerts
                    if alert_data['severity'] in ['critical', 'high']:
                        await self._send_alert_notifications(created_alert)
            
            return created_alerts
            
        except Exception as e:
            logger.error(f"Error processing sensor reading: {e}")
            return []
    
    async def _check_existing_alert(
        self,
        well_id: str,
        alert_type: str,
        severity: str,
    ) -> Optional[Dict[str, Any]]:
        """Check if similar unresolved alert exists"""
        from app.models.alert import Alert as AlertModel
        
        # Check for unresolved alert in last 5 minutes
        time_threshold = datetime.utcnow() - timedelta(minutes=5)
        
        existing = self.db.query(AlertModel).filter(
            AlertModel.well_id == well_id,
            AlertModel.alert_type == alert_type,
            AlertModel.severity == severity,
            AlertModel.resolved == False,
            AlertModel.created_at >= time_threshold,
        ).first()
        
        return existing
    
    async def _send_alert_notifications(self, alert: Any):
        """Send notifications for an alert"""
        try:
            # Determine notification channels based on severity
            channels = []
            if alert.severity == 'critical':
                channels = [
                    NotificationChannel.EMAIL,
                    NotificationChannel.SMS,
                    NotificationChannel.PUSH,
                ]
            elif alert.severity == 'high':
                channels = [
                    NotificationChannel.EMAIL,
                    NotificationChannel.PUSH,
                ]
            elif alert.severity == 'medium':
                channels = [NotificationChannel.EMAIL]
            else:
                channels = [NotificationChannel.PUSH]
            
            alert_dict = {
                'alert_id': str(alert.alert_id),
                'well_id': alert.well_id,
                'alert_type': alert.alert_type,
                'severity': alert.severity,
                'message': alert.message,
                'sensor_type': alert.sensor_type,
                'created_at': alert.created_at.isoformat(),
            }
            
            await self.notification_service.send_notification(
                alert=alert_dict,
                channels=channels,
            )
            
        except Exception as e:
            logger.error(f"Error sending alert notifications: {e}")
    
    async def monitor_sensor_data(
        self,
        well_id: Optional[str] = None,
        interval_seconds: int = 60,
    ):
        """Continuously monitor sensor data and create alerts"""
        self.is_running = True
        
        while self.is_running:
            try:
                # Get recent sensor readings
                time_threshold = datetime.utcnow() - timedelta(seconds=interval_seconds)
                
                query = self.db.query(SensorReadingModel).filter(
                    SensorReadingModel.timestamp >= time_threshold,
                )
                
                if well_id:
                    query = query.filter(SensorReadingModel.well_id == well_id)
                
                readings = query.all()
                
                # Process each reading
                for reading in readings:
                    await self.process_sensor_reading(reading)
                
                # Wait before next check
                await asyncio.sleep(interval_seconds)
                
            except Exception as e:
                logger.error(f"Error in monitor loop: {e}")
                await asyncio.sleep(interval_seconds)
    
    def stop_monitoring(self):
        """Stop monitoring sensor data"""
        self.is_running = False
    
    async def check_well_status(
        self,
        well_id: str,
    ) -> List[Dict[str, Any]]:
        """Check well status and create alerts if needed"""
        try:
            # Get latest sensor readings for well
            readings = self.db.query(SensorReadingModel).filter(
                SensorReadingModel.well_id == well_id,
            ).order_by(SensorReadingModel.timestamp.desc()).limit(10).all()
            
            created_alerts = []
            
            for reading in readings:
                alerts = await self.process_sensor_reading(reading)
                created_alerts.extend(alerts)
            
            return created_alerts
            
        except Exception as e:
            logger.error(f"Error checking well status: {e}")
            return []

