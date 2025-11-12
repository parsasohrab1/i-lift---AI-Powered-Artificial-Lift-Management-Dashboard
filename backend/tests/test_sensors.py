"""
Tests for sensors endpoints
"""
import pytest
from fastapi import status


def test_create_sensor(client, auth_headers, fake_sensor_data):
    """Test creating a sensor"""
    response = client.post(
        "/api/v1/sensors",
        json=fake_sensor_data,
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["sensor_type"] == fake_sensor_data["sensor_type"]
    assert data["name"] == fake_sensor_data["name"]
    assert "sensor_id" in data


def test_get_sensors(client, auth_headers, test_sensor):
    """Test getting list of sensors"""
    response = client.get(
        "/api/v1/sensors",
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "items" in data
    assert len(data["items"]) > 0


def test_get_sensor_by_id(client, auth_headers, test_sensor):
    """Test getting a sensor by ID"""
    response = client.get(
        f"/api/v1/sensors/{test_sensor['sensor_id']}",
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["sensor_id"] == test_sensor["sensor_id"]


def test_get_sensor_readings(client, auth_headers, test_sensor):
    """Test getting sensor readings"""
    response = client.get(
        f"/api/v1/sensors/{test_sensor['sensor_id']}/readings",
        params={"hours": 24},
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "readings" in data


def test_update_sensor(client, auth_headers, test_sensor):
    """Test updating a sensor"""
    update_data = {
        "name": "Updated Sensor Name",
        "is_active": False
    }
    response = client.put(
        f"/api/v1/sensors/{test_sensor['sensor_id']}",
        json=update_data,
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["name"] == update_data["name"]


def test_delete_sensor(client, auth_headers, test_sensor):
    """Test deleting a sensor"""
    response = client.delete(
        f"/api/v1/sensors/{test_sensor['sensor_id']}",
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT

