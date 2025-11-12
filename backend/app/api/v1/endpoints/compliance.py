"""
Compliance endpoints
"""
from typing import Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, Query, HTTPException, status
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_active_user, get_current_admin_user
from app.core.permissions import Permission, has_permission
from app.models.user import User
from app.services.compliance_service import ComplianceService
from app.services.audit_service import AuditService, AuditEventType
from app.services.security_policy_service import SecurityPolicyService, SecurityPolicyType

router = APIRouter()


@router.get("/report")
async def generate_compliance_report(
    start_date: Optional[datetime] = Query(None, description="Start date"),
    end_date: Optional[datetime] = Query(None, description="End date"),
    days: int = Query(30, ge=1, le=365, description="Number of days if dates not provided"),
    report_type: str = Query("full", regex="^(full|summary|detailed)$"),
    format: str = Query("json", regex="^(json|csv)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    """Generate compliance report (admin only)"""
    if not has_permission(current_user.role, Permission.SYSTEM_ADMIN):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied: SYSTEM_ADMIN required"
        )
    
    if not end_date:
        end_date = datetime.utcnow()
    if not start_date:
        start_date = end_date - timedelta(days=days)
    
    service = ComplianceService(db=db)
    report = await service.generate_compliance_report(start_date, end_date, report_type)
    
    if format == "json":
        import json
        return Response(
            content=json.dumps(report, indent=2, default=str),
            media_type="application/json",
            headers={
                "Content-Disposition": f"attachment; filename=compliance_report_{datetime.utcnow().strftime('%Y%m%d')}.json"
            }
        )
    else:
        exported = await service.export_compliance_report(report, format)
        return Response(
            content=exported,
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename=compliance_report_{datetime.utcnow().strftime('%Y%m%d')}.csv"
            }
        )


@router.get("/audit-logs")
async def get_audit_logs(
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    event_type: Optional[str] = Query(None, description="Filter by event type"),
    resource_type: Optional[str] = Query(None, description="Filter by resource type"),
    start_time: Optional[datetime] = Query(None, description="Start time"),
    end_time: Optional[datetime] = Query(None, description="End time"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    """Get audit logs (admin only)"""
    if not has_permission(current_user.role, Permission.SYSTEM_ADMIN):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied"
        )
    
    service = AuditService(db=db)
    logs = await service.get_audit_logs(
        user_id=user_id,
        event_type=AuditEventType(event_type) if event_type else None,
        resource_type=resource_type,
        start_time=start_time,
        end_time=end_time,
        limit=limit,
        offset=offset,
    )
    
    return {
        'logs': logs,
        'total': len(logs),
        'offset': offset,
        'limit': limit,
    }


@router.get("/user-activity/{user_id}")
async def get_user_activity(
    user_id: str,
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    """Get user activity summary (admin only)"""
    if not has_permission(current_user.role, Permission.SYSTEM_ADMIN):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied"
        )
    
    service = AuditService(db=db)
    activity = await service.get_user_activity(user_id, days)
    
    return activity


@router.get("/suspicious-activity")
async def get_suspicious_activity(
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    hours: int = Query(24, ge=1, le=168),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    """Detect suspicious activity (admin only)"""
    if not has_permission(current_user.role, Permission.SYSTEM_ADMIN):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied"
        )
    
    service = AuditService(db=db)
    suspicious = await service.detect_suspicious_activity(user_id, hours)
    
    return {
        'suspicious_activities': suspicious,
        'count': len(suspicious),
    }


@router.get("/security-policies")
async def get_security_policies(
    policy_type: Optional[str] = Query(None, description="Filter by policy type"),
    current_user: User = Depends(get_current_admin_user),
):
    """Get security policies (admin only)"""
    if not has_permission(current_user.role, Permission.SYSTEM_ADMIN):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied"
        )
    
    service = SecurityPolicyService()
    
    if policy_type:
        policy = service.get_policy(SecurityPolicyType(policy_type))
        return {policy_type: policy}
    else:
        return {
            policy_type.value: service.get_policy(policy_type)
            for policy_type in SecurityPolicyType
        }


@router.put("/security-policies/{policy_type}")
async def update_security_policy(
    policy_type: str,
    updates: dict,
    current_user: User = Depends(get_current_admin_user),
):
    """Update security policy (admin only)"""
    if not has_permission(current_user.role, Permission.SYSTEM_ADMIN):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied"
        )
    
    service = SecurityPolicyService()
    success = service.update_policy(SecurityPolicyType(policy_type), updates)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid policy type"
        )
    
    return {
        'message': 'Policy updated successfully',
        'policy': service.get_policy(SecurityPolicyType(policy_type)),
    }

