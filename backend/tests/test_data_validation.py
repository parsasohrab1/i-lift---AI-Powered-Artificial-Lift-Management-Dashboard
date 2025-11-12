"""
Tests for data validation
"""
import pytest
from fastapi import status


def test_create_well_invalid_data(client, auth_headers):
    """Test creating well with invalid data"""
    invalid_data = {
        "name": "",  # Empty name
        "location": "Test",
        "latitude": 200.0,  # Invalid latitude
        "longitude": 50.0
    }
    
    response = client.post(
        "/api/v1/wells",
        json=invalid_data,
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_create_sensor_invalid_data(client, auth_headers, test_well):
    """Test creating sensor with invalid data"""
    invalid_data = {
        "well_id": test_well["well_id"],
        "sensor_type": "",  # Empty sensor type
        "name": "Test Sensor",
        "unit": "Celsius",
        "min_value": 100.0,
        "max_value": 0.0  # Invalid: max < min
    }
    
    response = client.post(
        "/api/v1/sensors",
        json=invalid_data,
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_password_validation(client, admin_auth_headers):
    """Test password validation on registration"""
    # Too short
    response = client.post(
        "/api/v1/auth/register",
        json={
            "username": "user1",
            "email": "user1@example.com",
            "password": "Short1!",
            "full_name": "User 1",
            "role": "operator"
        },
        headers=admin_auth_headers
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    # Missing uppercase
    response = client.post(
        "/api/v1/auth/register",
        json={
            "username": "user2",
            "email": "user2@example.com",
            "password": "nopassword123!",
            "full_name": "User 2",
            "role": "operator"
        },
        headers=admin_auth_headers
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST

