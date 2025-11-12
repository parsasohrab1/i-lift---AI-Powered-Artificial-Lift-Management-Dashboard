"""
Tests for monitoring endpoints
"""
import pytest
from fastapi import status


def test_health_check(client):
    """Test basic health check endpoint"""
    response = client.get("/api/v1/monitoring/health")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "healthy"


def test_health_summary(client, auth_headers):
    """Test health summary endpoint"""
    response = client.get(
        "/api/v1/monitoring/health/summary",
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "overall_status" in data
    assert "database" in data
    assert "redis" in data


def test_metrics_summary(client, auth_headers):
    """Test metrics summary endpoint"""
    response = client.get(
        "/api/v1/monitoring/metrics/summary",
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "active_wells" in data
    assert "active_sensors" in data


def test_business_metrics(client, auth_headers):
    """Test business metrics endpoint"""
    response = client.get(
        "/api/v1/monitoring/metrics/business",
        params={"hours": 24},
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "sensor_readings" in data
    assert "alerts" in data


def test_prometheus_metrics(client, admin_auth_headers):
    """Test Prometheus metrics endpoint"""
    response = client.get(
        "/api/v1/monitoring/metrics",
        headers=admin_auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.headers["content-type"] == "text/plain; version=0.0.4"
    assert "http_requests_total" in response.text or len(response.text) > 0

