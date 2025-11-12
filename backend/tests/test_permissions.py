"""
Tests for permissions and role-based access control
"""
import pytest
from fastapi import status
from app.models.user import UserRole


def test_operator_cannot_create_user(client, auth_headers):
    """Test that operator cannot create users"""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "SecurePass123!",
            "full_name": "New User",
            "role": "operator"
        },
        headers=auth_headers
    )
    # Should be forbidden for non-admin users
    assert response.status_code in [status.HTTP_403_FORBIDDEN, status.HTTP_401_UNAUTHORIZED]


def test_admin_can_create_user(client, admin_auth_headers):
    """Test that admin can create users"""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "SecurePass123!",
            "full_name": "New User",
            "role": "operator"
        },
        headers=admin_auth_headers
    )
    assert response.status_code == status.HTTP_200_OK


def test_operator_can_view_wells(client, auth_headers):
    """Test that operator can view wells"""
    response = client.get(
        "/api/v1/wells",
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK


def test_unauthorized_access(client):
    """Test that unauthorized access is blocked"""
    response = client.get("/api/v1/wells")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

