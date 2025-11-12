"""
Analytics schemas
"""
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List


class KPIMetrics(BaseModel):
    """KPI metrics schema"""
    total_readings: int
    active_wells: int
    time_range: Dict[str, str]
    average_efficiency: Optional[float] = None
    data_quality_percentage: Optional[float] = None
    average_pressure_differential: Optional[float] = None


class AnalyticsResponse(BaseModel):
    """Analytics response schema"""
    kpis: Dict[str, Any]
    trends: Optional[Dict[str, Any]] = None
    comparisons: Optional[Dict[str, Any]] = None


class TrendDataPoint(BaseModel):
    """Trend data point schema"""
    date: str
    avg: float
    min: float
    max: float
    count: int


class TrendAnalysis(BaseModel):
    """Trend analysis schema"""
    direction: str  # increasing, decreasing, stable
    slope: float
    strength: float
    intercept: float


class TrendResponse(BaseModel):
    """Trend response schema"""
    well_id: str
    metric: str
    sensor_type: str
    time_range: Dict[str, Any]
    data_points: List[TrendDataPoint]
    trend: TrendAnalysis
    statistics: Dict[str, float]


class WellComparison(BaseModel):
    """Well comparison data schema"""
    avg: float
    min: float
    max: float
    std: float
    count: int


class ComparisonResponse(BaseModel):
    """Comparison response schema"""
    metric: str
    sensor_type: str
    time_range: Dict[str, str]
    wells: Dict[str, WellComparison]
    rankings: Dict[str, int]
    best_performer: Optional[str] = None
    worst_performer: Optional[str] = None


class PerformanceMetricsResponse(BaseModel):
    """Performance metrics response schema"""
    total_readings: int
    active_wells: int
    data_quality_score: float
    average_efficiency: float
    time_range: Dict[str, str]
    well_performance: Dict[str, Dict[str, Any]]


class TimeSeriesDataPoint(BaseModel):
    """Time series data point"""
    timestamp: str
    value: float
    well_id: Optional[str] = None


class TimeSeriesResponse(BaseModel):
    """Time series response schema"""
    metric: str
    sensor_type: str
    data_points: List[TimeSeriesDataPoint]
    time_range: Dict[str, str]
