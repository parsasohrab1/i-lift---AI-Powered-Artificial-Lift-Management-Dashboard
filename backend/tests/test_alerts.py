"""
Tests for alerts endpoints
"""
import pytest
from fastapi import status
from datetime import datetime, timedelta


def test_create_alert(client, auth_headers, test_well, test_sensor):
    """Test creating an alert"""
    alert_data = {
        "well_id": test_well["well_id"],
        "sensor_id": test_sensor["sensor_id"],
        "severity": "critical",
        "alert_type": "threshold_exceeded",
        "message": "Temperature exceeded threshold",
        "value": 150.0,
        "threshold": 100.0
    }
    
    response = client.post(
        "/api/v1/alerts",
        json=alert_data,
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["severity"] == alert_data["severity"]
    assert data["alert_type"] == alert_data["alert_type"]


def test_get_alerts(client, auth_headers):
    """Test getting list of alerts"""
    response = client.get(
        "/api/v1/alerts",
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "items" in data


def test_get_alerts_by_severity(client, auth_headers):
    """Test getting alerts filtered by severity"""
    response = client.get(
        "/api/v1/alerts",
        params={"severity": "critical"},
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "items" in data


def test_resolve_alert(client, auth_headers, test_well, test_sensor):
    """Test resolving an alert"""
    # First create an alert
    alert_data = {
        "well_id": test_well["well_id"],
        "sensor_id": test_sensor["sensor_id"],
        "severity": "warning",
        "alert_type": "threshold_exceeded",
        "message": "Test alert",
        "value": 120.0,
        "threshold": 100.0
    }
    
    create_response = client.post(
        "/api/v1/alerts",
        json=alert_data,
        headers=auth_headers
    )
    assert create_response.status_code == status.HTTP_201_CREATED
    alert_id = create_response.json()["alert_id"]
    
    # Resolve the alert
    resolve_response = client.post(
        f"/api/v1/alerts/{alert_id}/resolve",
        json={"resolution_notes": "Issue resolved"},
        headers=auth_headers
    )
    assert resolve_response.status_code == status.HTTP_200_OK
    data = resolve_response.json()
    assert data["status"] == "resolved"

