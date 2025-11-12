"""
Tests for ML predictions endpoints
"""
import pytest
from fastapi import status


def test_get_predictions(client, auth_headers, test_well):
    """Test getting ML predictions"""
    response = client.get(
        "/api/v1/ml/predictions",
        params={"well_id": test_well["well_id"]},
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "items" in data or "predictions" in data


def test_create_prediction(client, auth_headers, test_well):
    """Test creating a prediction"""
    prediction_data = {
        "well_id": test_well["well_id"],
        "model_type": "anomaly_detection",
        "prediction": {
            "anomaly_score": 0.85,
            "is_anomaly": True
        }
    }
    
    response = client.post(
        "/api/v1/ml/predictions",
        json=prediction_data,
        headers=auth_headers
    )
    # May return 201 or 200 depending on implementation
    assert response.status_code in [status.HTTP_200_OK, status.HTTP_201_CREATED]


def test_get_anomaly_detection(client, auth_headers, test_well):
    """Test anomaly detection"""
    response = client.post(
        "/api/v1/ml/anomaly-detection",
        json={
            "well_id": test_well["well_id"],
            "sensor_type": "temperature",
            "hours": 24
        },
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "anomalies" in data or "results" in data

