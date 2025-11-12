"""
Main API router
"""
from fastapi import APIRouter

from app.api.v1.endpoints import (
    auth,
    users,
    sensors,
    wells,
    analytics,
    ml_predictions,
    alerts,
    alert_rules,
    notifications,
    compliance,
    dashboard,
    ingestion,
    processing,
    synthetic_data,
    monitoring,
)

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(ingestion.router, prefix="/ingestion", tags=["data-ingestion"])
api_router.include_router(processing.router, prefix="/processing", tags=["data-processing"])
api_router.include_router(synthetic_data.router, prefix="/synthetic-data", tags=["synthetic-data"])
api_router.include_router(sensors.router, prefix="/sensors", tags=["sensors"])
api_router.include_router(wells.router, prefix="/wells", tags=["wells"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
api_router.include_router(ml_predictions.router, prefix="/ml", tags=["ml-predictions"])
api_router.include_router(alerts.router, prefix="/alerts", tags=["alerts"])
api_router.include_router(alert_rules.router, prefix="/alert-rules", tags=["alert-rules"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["notifications"])
api_router.include_router(compliance.router, prefix="/compliance", tags=["compliance"])
api_router.include_router(monitoring.router, prefix="/monitoring", tags=["monitoring"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])

