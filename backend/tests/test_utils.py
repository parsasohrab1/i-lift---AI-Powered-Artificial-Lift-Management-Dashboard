"""
Test utilities and helpers
"""
import pytest
from typing import Dict, Any


def assert_response_success(response, expected_status=200):
    """Assert that a response is successful"""
    assert response.status_code == expected_status


def assert_response_error(response, expected_status=400):
    """Assert that a response is an error"""
    assert response.status_code == expected_status
    assert "detail" in response.json()


def assert_pagination(response_data: Dict[str, Any]):
    """Assert that response has pagination structure"""
    assert "items" in response_data
    assert "total" in response_data
    assert "page" in response_data
    assert "page_size" in response_data


def assert_well_structure(well_data: Dict[str, Any]):
    """Assert that well data has required structure"""
    required_fields = ["well_id", "name", "location", "latitude", "longitude", "well_type"]
    for field in required_fields:
        assert field in well_data, f"Missing required field: {field}"


def assert_sensor_structure(sensor_data: Dict[str, Any]):
    """Assert that sensor data has required structure"""
    required_fields = ["sensor_id", "well_id", "sensor_type", "name", "unit"]
    for field in required_fields:
        assert field in sensor_data, f"Missing required field: {field}"

