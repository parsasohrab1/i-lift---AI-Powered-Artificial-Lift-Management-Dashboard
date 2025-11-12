"""
Role-Based Access Control (RBAC) permissions
"""
from enum import Enum
from typing import List
from functools import wraps
from fastapi import HTTPException, status, Depends
from sqlalchemy.orm import Session

from app.models.user import UserRole


class Permission(str, Enum):
    """System permissions"""
    # Sensor data permissions
    VIEW_SENSOR_DATA = "view_sensor_data"
    CREATE_SENSOR_DATA = "create_sensor_data"
    DELETE_SENSOR_DATA = "delete_sensor_data"
    
    # Well management permissions
    VIEW_WELLS = "view_wells"
    CREATE_WELLS = "create_wells"
    UPDATE_WELLS = "update_wells"
    DELETE_WELLS = "delete_wells"
    
    # Analytics permissions
    VIEW_ANALYTICS = "view_analytics"
    EXPORT_ANALYTICS = "export_analytics"
    
    # ML predictions permissions
    VIEW_ML_PREDICTIONS = "view_ml_predictions"
    CREATE_ML_PREDICTIONS = "create_ml_predictions"
    TRAIN_MODELS = "train_models"
    
    # Alerts permissions
    VIEW_ALERTS = "view_alerts"
    CREATE_ALERTS = "create_alerts"
    RESOLVE_ALERTS = "resolve_alerts"
    
    # Dashboard permissions
    VIEW_DASHBOARD = "view_dashboard"
    CUSTOMIZE_DASHBOARD = "customize_dashboard"
    
    # User management permissions
    VIEW_USERS = "view_users"
    CREATE_USERS = "create_users"
    UPDATE_USERS = "update_users"
    DELETE_USERS = "delete_users"
    
    # System administration
    SYSTEM_ADMIN = "system_admin"


# Role to permissions mapping
ROLE_PERMISSIONS: Dict[UserRole, List[Permission]] = {
    UserRole.FIELD_OPERATOR: [
        Permission.VIEW_SENSOR_DATA,
        Permission.VIEW_WELLS,
        Permission.VIEW_ALERTS,
        Permission.VIEW_DASHBOARD,
    ],
    UserRole.PRODUCTION_ENGINEER: [
        Permission.VIEW_SENSOR_DATA,
        Permission.CREATE_SENSOR_DATA,
        Permission.VIEW_WELLS,
        Permission.CREATE_WELLS,
        Permission.UPDATE_WELLS,
        Permission.VIEW_ANALYTICS,
        Permission.EXPORT_ANALYTICS,
        Permission.VIEW_ML_PREDICTIONS,
        Permission.VIEW_ALERTS,
        Permission.CREATE_ALERTS,
        Permission.RESOLVE_ALERTS,
        Permission.VIEW_DASHBOARD,
        Permission.CUSTOMIZE_DASHBOARD,
    ],
    UserRole.DATA_SCIENTIST: [
        Permission.VIEW_SENSOR_DATA,
        Permission.VIEW_WELLS,
        Permission.VIEW_ANALYTICS,
        Permission.EXPORT_ANALYTICS,
        Permission.VIEW_ML_PREDICTIONS,
        Permission.CREATE_ML_PREDICTIONS,
        Permission.TRAIN_MODELS,
        Permission.VIEW_DASHBOARD,
        Permission.CUSTOMIZE_DASHBOARD,
    ],
    UserRole.OPERATIONS_MANAGER: [
        Permission.VIEW_SENSOR_DATA,
        Permission.VIEW_WELLS,
        Permission.VIEW_ANALYTICS,
        Permission.EXPORT_ANALYTICS,
        Permission.VIEW_ML_PREDICTIONS,
        Permission.VIEW_ALERTS,
        Permission.RESOLVE_ALERTS,
        Permission.VIEW_DASHBOARD,
        Permission.CUSTOMIZE_DASHBOARD,
        Permission.VIEW_USERS,
    ],
    UserRole.ADMIN: [
        # Admin has all permissions
        *[p for p in Permission],
    ],
}


def get_user_permissions(role: UserRole) -> List[Permission]:
    """Get permissions for a role"""
    return ROLE_PERMISSIONS.get(role, [])


def has_permission(user_role: UserRole, permission: Permission) -> bool:
    """Check if a role has a specific permission"""
    permissions = get_user_permissions(user_role)
    return permission in permissions or UserRole.ADMIN == user_role


def require_permission(permission: Permission):
    """Decorator to require a specific permission"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get current user from kwargs or dependencies
            current_user = kwargs.get('current_user')
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )
            
            if not has_permission(current_user.role, permission):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Permission denied: {permission.value}"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator

