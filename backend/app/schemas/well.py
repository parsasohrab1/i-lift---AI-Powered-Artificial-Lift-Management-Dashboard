"""
Well schemas
"""
from pydantic import BaseModel
from typing import Optional
from datetime import date


class Well(BaseModel):
    """Well input schema"""
    well_id: str
    well_name: str
    location_lat: float
    location_lon: float
    equipment_type: str
    installation_date: Optional[date] = None
    status: str = "active"


class WellResponse(BaseModel):
    """Well response schema"""
    well_id: str
    well_name: str
    location_lat: float
    location_lon: float
    equipment_type: str
    installation_date: Optional[date]
    status: str
    last_maintenance: Optional[date] = None

    class Config:
        from_attributes = True

