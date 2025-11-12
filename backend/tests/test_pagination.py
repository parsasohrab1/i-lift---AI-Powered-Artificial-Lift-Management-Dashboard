"""
Tests for pagination
"""
import pytest
from fastapi import status


def test_wells_pagination(client, auth_headers):
    """Test wells endpoint pagination"""
    response = client.get(
        "/api/v1/wells",
        params={"page": 1, "page_size": 10},
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert "page" in data
    assert "page_size" in data
    assert len(data["items"]) <= data["page_size"]


def test_sensors_pagination(client, auth_headers):
    """Test sensors endpoint pagination"""
    response = client.get(
        "/api/v1/sensors",
        params={"page": 1, "page_size": 5},
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert data["page_size"] == 5


def test_alerts_pagination(client, auth_headers):
    """Test alerts endpoint pagination"""
    response = client.get(
        "/api/v1/alerts",
        params={"page": 1, "page_size": 20},
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "items" in data
    assert "total" in data

