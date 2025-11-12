"""
Alert Rules endpoints
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from app.core.database import get_db
from app.core.dependencies import get_current_active_user, get_current_admin_user
from app.core.permissions import Permission, has_permission
from app.models.user import User
from app.services.alert_rules import AlertRulesEngine, AlertRule, AlertSeverity

router = APIRouter()


class AlertRuleRequest(BaseModel):
    """Alert rule request schema"""
    rule_id: str
    name: str
    sensor_type: str
    condition: str = Field(..., regex="^(gt|lt|eq|between)$")
    threshold: float
    threshold_max: float | None = None
    severity: str = Field(..., regex="^(low|medium|high|critical)$")
    message_template: str = "{sensor_type} {condition} threshold"
    enabled: bool = True


class AlertRuleResponse(BaseModel):
    """Alert rule response schema"""
    rule_id: str
    name: str
    sensor_type: str
    condition: str
    threshold: float
    threshold_max: float | None
    severity: str
    message_template: str
    enabled: bool


@router.get("/", response_model=List[AlertRuleResponse])
async def list_alert_rules(
    current_user: User = Depends(get_current_active_user),
):
    """List all alert rules"""
    if not has_permission(current_user.role, Permission.VIEW_ALERTS):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied"
        )
    
    engine = AlertRulesEngine()
    rules = engine.list_rules()
    
    return [
        AlertRuleResponse(
            rule_id=rule.rule_id,
            name=rule.name,
            sensor_type=rule.sensor_type,
            condition=rule.condition,
            threshold=rule.threshold,
            threshold_max=rule.threshold_max,
            severity=rule.severity.value,
            message_template=rule.message_template,
            enabled=rule.enabled,
        )
        for rule in rules
    ]


@router.post("/", response_model=AlertRuleResponse)
async def create_alert_rule(
    request: AlertRuleRequest,
    current_user: User = Depends(get_current_admin_user),
):
    """Create a new alert rule (admin only)"""
    if not has_permission(current_user.role, Permission.SYSTEM_ADMIN):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied"
        )
    
    engine = AlertRulesEngine()
    
    rule = AlertRule(
        rule_id=request.rule_id,
        name=request.name,
        sensor_type=request.sensor_type,
        condition=request.condition,
        threshold=request.threshold,
        threshold_max=request.threshold_max,
        severity=AlertSeverity(request.severity),
        message_template=request.message_template,
        enabled=request.enabled,
    )
    
    engine.add_rule(rule)
    
    return AlertRuleResponse(
        rule_id=rule.rule_id,
        name=rule.name,
        sensor_type=rule.sensor_type,
        condition=rule.condition,
        threshold=rule.threshold,
        threshold_max=rule.threshold_max,
        severity=rule.severity.value,
        message_template=rule.message_template,
        enabled=rule.enabled,
    )


@router.put("/{rule_id}", response_model=AlertRuleResponse)
async def update_alert_rule(
    rule_id: str,
    request: AlertRuleRequest,
    current_user: User = Depends(get_current_admin_user),
):
    """Update an alert rule (admin only)"""
    if not has_permission(current_user.role, Permission.SYSTEM_ADMIN):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied"
        )
    
    engine = AlertRulesEngine()
    
    success = engine.update_rule(
        rule_id,
        name=request.name,
        sensor_type=request.sensor_type,
        condition=request.condition,
        threshold=request.threshold,
        threshold_max=request.threshold_max,
        severity=AlertSeverity(request.severity),
        message_template=request.message_template,
        enabled=request.enabled,
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert rule not found"
        )
    
    rule = engine.get_rule(rule_id)
    return AlertRuleResponse(
        rule_id=rule.rule_id,
        name=rule.name,
        sensor_type=rule.sensor_type,
        condition=rule.condition,
        threshold=rule.threshold,
        threshold_max=rule.threshold_max,
        severity=rule.severity.value,
        message_template=rule.message_template,
        enabled=rule.enabled,
    )


@router.delete("/{rule_id}")
async def delete_alert_rule(
    rule_id: str,
    current_user: User = Depends(get_current_admin_user),
):
    """Delete an alert rule (admin only)"""
    if not has_permission(current_user.role, Permission.SYSTEM_ADMIN):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied"
        )
    
    engine = AlertRulesEngine()
    engine.remove_rule(rule_id)
    
    return {"message": "Alert rule deleted successfully"}


@router.get("/{rule_id}", response_model=AlertRuleResponse)
async def get_alert_rule(
    rule_id: str,
    current_user: User = Depends(get_current_active_user),
):
    """Get an alert rule"""
    if not has_permission(current_user.role, Permission.VIEW_ALERTS):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied"
        )
    
    engine = AlertRulesEngine()
    rule = engine.get_rule(rule_id)
    
    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert rule not found"
        )
    
    return AlertRuleResponse(
        rule_id=rule.rule_id,
        name=rule.name,
        sensor_type=rule.sensor_type,
        condition=rule.condition,
        threshold=rule.threshold,
        threshold_max=rule.threshold_max,
        severity=rule.severity.value,
        message_template=rule.message_template,
        enabled=rule.enabled,
    )

