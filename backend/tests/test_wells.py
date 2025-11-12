"""
Tests for wells endpoints
"""
import pytest
from fastapi import status


def test_create_well(client, auth_headers, fake_well_data):
    """Test creating a well"""
    response = client.post(
        "/api/v1/wells",
        json=fake_well_data,
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["name"] == fake_well_data["name"]
    assert data["location"] == fake_well_data["location"]
    assert "well_id" in data


def test_get_wells(client, auth_headers, test_well):
    """Test getting list of wells"""
    response = client.get(
        "/api/v1/wells",
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "items" in data
    assert len(data["items"]) > 0


def test_get_well_by_id(client, auth_headers, test_well):
    """Test getting a well by ID"""
    response = client.get(
        f"/api/v1/wells/{test_well['well_id']}",
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["well_id"] == test_well["well_id"]
    assert data["name"] == test_well["name"]


def test_update_well(client, auth_headers, test_well):
    """Test updating a well"""
    update_data = {
        "name": "Updated Well Name",
        "is_active": False
    }
    response = client.put(
        f"/api/v1/wells/{test_well['well_id']}",
        json=update_data,
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["name"] == update_data["name"]
    assert data["is_active"] == update_data["is_active"]


def test_delete_well(client, auth_headers, test_well):
    """Test deleting a well"""
    response = client.delete(
        f"/api/v1/wells/{test_well['well_id']}",
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT
    
    # Verify well is deleted
    get_response = client.get(
        f"/api/v1/wells/{test_well['well_id']}",
        headers=auth_headers
    )
    assert get_response.status_code == status.HTTP_404_NOT_FOUND


def test_get_wells_unauthorized(client):
    """Test getting wells without authentication"""
    response = client.get("/api/v1/wells")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

