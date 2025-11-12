"""
Synthetic data generation schemas
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class SyntheticDataRequest(BaseModel):
    """Request schema for synthetic data generation"""
    well_ids: List[str] = Field(..., min_items=1, description="List of well IDs to generate data for")
    days: int = Field(180, ge=1, le=365, description="Number of days to generate")
    interval_seconds: int = Field(1, ge=1, le=3600, description="Data interval in seconds")
    start_date: Optional[datetime] = Field(None, description="Start date (defaults to days ago from now)")
    include_anomalies: bool = Field(True, description="Include random anomalies")
    include_failures: bool = Field(True, description="Include failure scenarios")
    failure_probability: float = Field(0.1, ge=0, le=1, description="Probability of failure scenario")
    seed: Optional[int] = Field(None, description="Random seed for reproducibility")
    export_format: Optional[str] = Field(None, description="Export format: parquet, csv, or json")


class SyntheticDataResponse(BaseModel):
    """Response schema for synthetic data generation"""
    success: bool
    message: str
    record_count: int
    well_ids: List[str]
    date_range: Dict[str, str]
    output_path: Optional[str] = None
    statistics: Dict[str, Any]


class SyntheticDataStatsResponse(BaseModel):
    """Statistics response schema"""
    total_records: int
    date_range: Dict[str, str]
    wells: List[str]
    sensors: List[str]
    sensor_statistics: Dict[str, Dict[str, float]]
    status_distribution: Optional[Dict[str, int]] = None

