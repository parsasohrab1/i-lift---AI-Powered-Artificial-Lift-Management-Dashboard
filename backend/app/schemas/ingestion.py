"""
Data ingestion schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class SensorDataIngest(BaseModel):
    """Single sensor reading ingestion schema"""
    well_id: str = Field(..., description="Well identifier")
    sensor_type: str = Field(..., description="Type of sensor")
    sensor_value: float = Field(..., description="Sensor reading value")
    measurement_unit: Optional[str] = Field(None, description="Unit of measurement")
    timestamp: Optional[datetime] = Field(None, description="Timestamp of reading")
    data_quality: Optional[int] = Field(None, ge=0, le=100, description="Data quality score")


class BatchSensorDataIngest(BaseModel):
    """Batch sensor readings ingestion schema"""
    readings: List[SensorDataIngest] = Field(..., min_items=1, max_items=1000)


class IngestionResponse(BaseModel):
    """Ingestion response schema"""
    success: bool
    message: str
    ingested_count: int
    error_count: int
    errors: Optional[List[str]] = None


class IngestionStatsResponse(BaseModel):
    """Ingestion statistics response schema"""
    total_received: int
    total_validated: int
    total_sent_to_kafka: int
    total_errors: int
    sources: Dict[str, int]
    is_running: bool
    mqtt_connected: bool
    opcua_connected: bool

