"""
Tests for service layer
"""
import pytest
from datetime import datetime, timedelta
from app.services.well_service import WellService
from app.services.sensor_service import SensorService
from app.services.analytics_service import AnalyticsService


def test_well_service_create(db, test_user, fake_well_data):
    """Test WellService create method"""
    service = WellService(db=db)
    well = service.create_well(
        well_data=fake_well_data,
        user_id=str(test_user.user_id)
    )
    
    assert well is not None
    assert well.name == fake_well_data["name"]
    assert well.location == fake_well_data["location"]


def test_well_service_get_by_id(db, test_well):
    """Test WellService get_by_id method"""
    service = WellService(db=db)
    well = service.get_well_by_id(test_well["well_id"])
    
    assert well is not None
    assert well.well_id == test_well["well_id"]


def test_sensor_service_create(db, test_well, fake_sensor_data):
    """Test SensorService create method"""
    service = SensorService(db=db)
    sensor = service.create_sensor(fake_sensor_data)
    
    assert sensor is not None
    assert sensor.sensor_type == fake_sensor_data["sensor_type"]
    assert sensor.well_id == test_well["well_id"]


def test_analytics_service_get_kpis(db, test_well):
    """Test AnalyticsService get_kpis method"""
    service = AnalyticsService(db=db)
    kpis = service.get_kpis(well_id=test_well["well_id"])
    
    assert kpis is not None
    assert "total_readings" in kpis
    assert "average_value" in kpis


def test_analytics_service_get_trends(db, test_well):
    """Test AnalyticsService get_trends method"""
    service = AnalyticsService(db=db)
    trends = service.get_trends(
        well_id=test_well["well_id"],
        metric="temperature",
        hours=24
    )
    
    assert trends is not None
    assert "data_points" in trends or "trend" in trends

