"""
Sensor data schemas
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List, Dict, Any


class SensorReading(BaseModel):
    """Sensor reading input schema"""
    well_id: str
    sensor_type: str
    sensor_value: float
    measurement_unit: Optional[str] = None
    data_quality: Optional[int] = Field(None, ge=0, le=100)
    timestamp: Optional[datetime] = None


class SensorReadingResponse(BaseModel):
    """Sensor reading response schema"""
    reading_id: str
    well_id: str
    sensor_type: str
    sensor_value: float
    measurement_unit: Optional[str]
    data_quality: Optional[int]
    timestamp: datetime
    created_at: datetime

    class Config:
        from_attributes = True


class SensorReadingsListResponse(BaseModel):
    """List of sensor readings with pagination"""
    readings: List[SensorReadingResponse]
    total: int
    offset: int
    limit: int


class AggregatedDataResponse(BaseModel):
    """Aggregated sensor data response"""
    timestamp: str
    well_id: str
    sensor_type: str
    avg_value: float
    min_value: float
    max_value: float
    std_value: float
    count: int


class SensorStatisticsResponse(BaseModel):
    """Sensor statistics response"""
    statistics: Dict[str, Dict[str, Any]]


class RealtimeDataResponse(BaseModel):
    """Real-time sensor data response"""
    data: Dict[str, Dict[str, Dict[str, Any]]]
    timestamp: str

