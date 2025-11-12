"""
Compliance Service
Generates compliance reports and ensures regulatory compliance
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_

from app.core.database import get_db
from app.models.audit import AuditLog
from app.models.user import User
from app.models.alert import Alert as AlertModel
from app.utils.logger import setup_logging

logger = setup_logging()


class ComplianceService:
    """Service for compliance reporting"""
    
    def __init__(self, db: Session = None):
        if db:
            self.db = db
        else:
            self.db = next(get_db())
    
    async def generate_compliance_report(
        self,
        start_date: datetime,
        end_date: datetime,
        report_type: str = "full",
    ) -> Dict[str, Any]:
        """Generate compliance report"""
        try:
            report = {
                'report_type': report_type,
                'generated_at': datetime.utcnow().isoformat(),
                'period': {
                    'start': start_date.isoformat(),
                    'end': end_date.isoformat(),
                },
                'sections': {},
            }
            
            # Audit Logs Summary
            audit_summary = await self._get_audit_summary(start_date, end_date)
            report['sections']['audit_logs'] = audit_summary
            
            # User Activity
            user_activity = await self._get_user_activity_summary(start_date, end_date)
            report['sections']['user_activity'] = user_activity
            
            # Security Events
            security_events = await self._get_security_events(start_date, end_date)
            report['sections']['security_events'] = security_events
            
            # Data Access
            data_access = await self._get_data_access_summary(start_date, end_date)
            report['sections']['data_access'] = data_access
            
            # Alerts and Incidents
            alerts_summary = await self._get_alerts_summary(start_date, end_date)
            report['sections']['alerts'] = alerts_summary
            
            # Compliance Status
            compliance_status = await self._check_compliance_status()
            report['sections']['compliance_status'] = compliance_status
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating compliance report: {e}")
            raise
    
    async def _get_audit_summary(
        self,
        start_date: datetime,
        end_date: datetime,
    ) -> Dict[str, Any]:
        """Get audit logs summary"""
        logs = self.db.query(AuditLog).filter(
            AuditLog.timestamp >= start_date,
            AuditLog.timestamp <= end_date,
        ).all()
        
        total_events = len(logs)
        successful_events = sum(1 for log in logs if log.success)
        failed_events = total_events - successful_events
        
        # Count by event type
        event_types = {}
        for log in logs:
            event_types[log.event_type] = event_types.get(log.event_type, 0) + 1
        
        # Count by user
        user_activity = {}
        for log in logs:
            if log.user_id:
                user_activity[log.user_id] = user_activity.get(log.user_id, 0) + 1
        
        return {
            'total_events': total_events,
            'successful_events': successful_events,
            'failed_events': failed_events,
            'event_types': event_types,
            'unique_users': len(user_activity),
            'top_users': dict(sorted(user_activity.items(), key=lambda x: x[1], reverse=True)[:10]),
        }
    
    async def _get_user_activity_summary(
        self,
        start_date: datetime,
        end_date: datetime,
    ) -> Dict[str, Any]:
        """Get user activity summary"""
        users = self.db.query(User).all()
        
        activity_summary = []
        for user in users:
            logs = self.db.query(AuditLog).filter(
                AuditLog.user_id == str(user.id),
                AuditLog.timestamp >= start_date,
                AuditLog.timestamp <= end_date,
            ).all()
            
            if logs:
                activity_summary.append({
                    'user_id': str(user.id),
                    'username': user.username,
                    'role': user.role.value,
                    'total_actions': len(logs),
                    'last_activity': max(log.timestamp for log in logs).isoformat(),
                })
        
        return {
            'total_active_users': len(activity_summary),
            'users': sorted(activity_summary, key=lambda x: x['total_actions'], reverse=True),
        }
    
    async def _get_security_events(
        self,
        start_date: datetime,
        end_date: datetime,
    ) -> Dict[str, Any]:
        """Get security events summary"""
        security_event_types = [
            'login_failed',
            'permission_denied',
            'unauthorized_access',
            'suspicious_activity',
        ]
        
        events = self.db.query(AuditLog).filter(
            AuditLog.timestamp >= start_date,
            AuditLog.timestamp <= end_date,
            AuditLog.event_type.in_(security_event_types),
        ).all()
        
        event_counts = {}
        for event in events:
            event_counts[event.event_type] = event_counts.get(event.event_type, 0) + 1
        
        return {
            'total_security_events': len(events),
            'event_counts': event_counts,
            'critical_events': len([e for e in events if e.event_type == 'unauthorized_access']),
        }
    
    async def _get_data_access_summary(
        self,
        start_date: datetime,
        end_date: datetime,
    ) -> Dict[str, Any]:
        """Get data access summary"""
        data_access_types = [
            'data_view',
            'data_create',
            'data_update',
            'data_delete',
            'data_export',
        ]
        
        logs = self.db.query(AuditLog).filter(
            AuditLog.timestamp >= start_date,
            AuditLog.timestamp <= end_date,
            AuditLog.event_type.in_(data_access_types),
        ).all()
        
        access_by_type = {}
        for log in logs:
            access_by_type[log.event_type] = access_by_type.get(log.event_type, 0) + 1
        
        # Count exports (sensitive operation)
        exports = [log for log in logs if log.event_type == 'data_export']
        
        return {
            'total_data_operations': len(logs),
            'operations_by_type': access_by_type,
            'data_exports': len(exports),
            'export_users': list(set(log.user_id for log in exports if log.user_id)),
        }
    
    async def _get_alerts_summary(
        self,
        start_date: datetime,
        end_date: datetime,
    ) -> Dict[str, Any]:
        """Get alerts summary"""
        alerts = self.db.query(AlertModel).filter(
            AlertModel.created_at >= start_date,
            AlertModel.created_at <= end_date,
        ).all()
        
        total_alerts = len(alerts)
        resolved_alerts = sum(1 for a in alerts if a.resolved)
        critical_alerts = sum(1 for a in alerts if a.severity == 'critical')
        
        # Count by severity
        severity_counts = {}
        for alert in alerts:
            severity_counts[alert.severity] = severity_counts.get(alert.severity, 0) + 1
        
        # Count by type
        type_counts = {}
        for alert in alerts:
            type_counts[alert.alert_type] = type_counts.get(alert.alert_type, 0) + 1
        
        return {
            'total_alerts': total_alerts,
            'resolved_alerts': resolved_alerts,
            'unresolved_alerts': total_alerts - resolved_alerts,
            'critical_alerts': critical_alerts,
            'severity_distribution': severity_counts,
            'type_distribution': type_counts,
        }
    
    async def _check_compliance_status(self) -> Dict[str, Any]:
        """Check overall compliance status"""
        from app.services.security_policy_service import SecurityPolicyService
        
        policy_service = SecurityPolicyService()
        
        # Check password policy
        password_policy = policy_service.get_policy(SecurityPolicyType.PASSWORD)
        
        # Check session policy
        session_policy = policy_service.get_policy(SecurityPolicyType.SESSION)
        
        # Check audit policy
        audit_policy = policy_service.get_policy(SecurityPolicyType.AUDIT)
        
        # Check encryption
        encryption_policy = policy_service.get_policy(SecurityPolicyType.ENCRYPTION)
        
        compliance_items = [
            {
                'item': 'Password Policy',
                'status': 'compliant' if password_policy.get('min_length', 0) >= 8 else 'non-compliant',
                'details': password_policy,
            },
            {
                'item': 'Session Management',
                'status': 'compliant' if session_policy.get('require_https') else 'non-compliant',
                'details': session_policy,
            },
            {
                'item': 'Audit Logging',
                'status': 'compliant' if audit_policy.get('log_all_actions') else 'non-compliant',
                'details': audit_policy,
            },
            {
                'item': 'Data Encryption',
                'status': 'compliant' if encryption_policy.get('encrypt_sensitive_fields') else 'non-compliant',
                'details': encryption_policy,
            },
        ]
        
        compliant_count = sum(1 for item in compliance_items if item['status'] == 'compliant')
        
        return {
            'overall_status': 'compliant' if compliant_count == len(compliance_items) else 'non-compliant',
            'compliance_score': compliant_count / len(compliance_items) * 100,
            'items': compliance_items,
        }
    
    async def export_compliance_report(
        self,
        report: Dict[str, Any],
        format: str = "json",
    ) -> bytes:
        """Export compliance report to file"""
        import json
        
        if format == "json":
            return json.dumps(report, indent=2).encode()
        elif format == "csv":
            # Convert to CSV format
            import io
            import csv
            
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Write header
            writer.writerow(['Section', 'Metric', 'Value'])
            
            # Write data
            for section, data in report['sections'].items():
                if isinstance(data, dict):
                    for key, value in data.items():
                        if isinstance(value, (str, int, float, bool)):
                            writer.writerow([section, key, value])
            
            return output.getvalue().encode()
        else:
            raise ValueError(f"Unsupported format: {format}")

