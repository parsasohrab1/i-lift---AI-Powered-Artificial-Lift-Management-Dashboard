"""
Tests for analytics endpoints
"""
import pytest
from fastapi import status


def test_get_kpis(client, auth_headers, test_well):
    """Test getting KPIs"""
    response = client.get(
        f"/api/v1/analytics/kpis",
        params={"well_id": test_well["well_id"]},
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "total_readings" in data
    assert "average_value" in data


def test_get_trends(client, auth_headers, test_well):
    """Test getting trends"""
    response = client.get(
        f"/api/v1/analytics/trends",
        params={
            "well_id": test_well["well_id"],
            "metric": "temperature",
            "hours": 24
        },
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "data_points" in data or "trend" in data


def test_get_comparison(client, auth_headers, test_well):
    """Test getting comparison"""
    response = client.get(
        f"/api/v1/analytics/comparison",
        params={
            "well_ids": [test_well["well_id"]],
            "metric": "temperature"
        },
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "wells" in data or "comparison" in data


def test_get_performance_metrics(client, auth_headers, test_well):
    """Test getting performance metrics"""
    response = client.get(
        f"/api/v1/analytics/performance",
        params={"well_id": test_well["well_id"]},
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "metrics" in data or "performance" in data

