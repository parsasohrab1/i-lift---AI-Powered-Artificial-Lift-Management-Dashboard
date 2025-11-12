"""
Alert schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class Alert(BaseModel):
    """Alert input schema"""
    well_id: str = Field(..., description="Well ID")
    alert_type: str = Field(..., description="Alert type (temperature_high, pressure_low, vibration_high, etc.)")
    severity: str = Field(..., description="Severity level (low, medium, high, critical)")
    message: str = Field(..., description="Alert message")
    sensor_type: Optional[str] = Field(None, description="Related sensor type")


class AlertResponse(BaseModel):
    """Alert response schema"""
    alert_id: str
    well_id: str
    alert_type: str
    severity: str
    message: str
    sensor_type: Optional[str]
    resolved: bool
    created_at: datetime
    resolved_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class AlertListResponse(BaseModel):
    """List of alerts with pagination"""
    alerts: List[AlertResponse]
    total: int
    offset: int
    limit: int


class AlertStatisticsResponse(BaseModel):
    """Alert statistics response"""
    total_alerts: int
    resolved_count: int
    unresolved_count: int
    resolution_rate: float
    severity_distribution: Dict[str, int]
    type_distribution: Dict[str, int]
    well_distribution: Dict[str, int]
    average_resolution_time_hours: Optional[float] = None
    time_range: Dict[str, str]


class BulkResolveRequest(BaseModel):
    """Bulk resolve request schema"""
    alert_ids: List[str] = Field(..., min_items=1, description="List of alert IDs to resolve")
    resolved_by: Optional[str] = Field(None, description="User who resolved the alerts")


class BulkResolveResponse(BaseModel):
    """Bulk resolve response schema"""
    total: int
    resolved: int
    failed: int
    failed_ids: List[str]
