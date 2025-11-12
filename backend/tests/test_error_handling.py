"""
Tests for error handling
"""
import pytest
from fastapi import status


def test_get_nonexistent_well(client, auth_headers):
    """Test getting a well that doesn't exist"""
    response = client.get(
        "/api/v1/wells/nonexistent-well-id",
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "detail" in response.json()


def test_get_nonexistent_sensor(client, auth_headers):
    """Test getting a sensor that doesn't exist"""
    response = client.get(
        "/api/v1/sensors/nonexistent-sensor-id",
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_update_nonexistent_well(client, auth_headers):
    """Test updating a well that doesn't exist"""
    response = client.put(
        "/api/v1/wells/nonexistent-well-id",
        json={"name": "Updated Name"},
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_delete_nonexistent_well(client, auth_headers):
    """Test deleting a well that doesn't exist"""
    response = client.delete(
        "/api/v1/wells/nonexistent-well-id",
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_invalid_json(client, auth_headers):
    """Test handling invalid JSON"""
    response = client.post(
        "/api/v1/wells",
        data="invalid json",
        headers={**auth_headers, "Content-Type": "application/json"}
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

