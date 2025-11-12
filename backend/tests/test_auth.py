"""
Tests for authentication endpoints
"""
import pytest
from fastapi import status


def test_register_user(client, admin_auth_headers):
    """Test user registration"""
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
    data = response.json()
    assert data["username"] == "newuser"
    assert data["email"] == "newuser@example.com"
    assert "password" not in data


def test_register_user_duplicate_username(client, admin_auth_headers, test_user):
    """Test registration with duplicate username"""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "username": test_user.username,
            "email": "different@example.com",
            "password": "SecurePass123!",
            "full_name": "Different User",
            "role": "operator"
        },
        headers=admin_auth_headers
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_register_user_weak_password(client, admin_auth_headers):
    """Test registration with weak password"""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "weak",
            "full_name": "New User",
            "role": "operator"
        },
        headers=admin_auth_headers
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_login_success(client, test_user):
    """Test successful login"""
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": test_user.username,
            "password": "testpassword123"
        }
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_credentials(client):
    """Test login with invalid credentials"""
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "nonexistent",
            "password": "wrongpassword"
        }
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_get_current_user(client, auth_headers, test_user):
    """Test getting current user"""
    response = client.get(
        "/api/v1/auth/me",
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["username"] == test_user.username
    assert data["email"] == test_user.email


def test_get_current_user_unauthorized(client):
    """Test getting current user without authentication"""
    response = client.get("/api/v1/auth/me")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_change_password(client, auth_headers, test_user):
    """Test changing password"""
    response = client.post(
        "/api/v1/auth/change-password",
        json={
            "current_password": "testpassword123",
            "new_password": "NewSecurePass123!",
            "confirm_password": "NewSecurePass123!"
        },
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    
    # Try to login with new password
    login_response = client.post(
        "/api/v1/auth/login",
        data={
            "username": test_user.username,
            "password": "NewSecurePass123!"
        }
    )
    assert login_response.status_code == status.HTTP_200_OK


def test_change_password_wrong_current(client, auth_headers):
    """Test changing password with wrong current password"""
    response = client.post(
        "/api/v1/auth/change-password",
        json={
            "current_password": "wrongpassword",
            "new_password": "NewSecurePass123!",
            "confirm_password": "NewSecurePass123!"
        },
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_refresh_token(client, test_user):
    """Test token refresh"""
    # First login
    login_response = client.post(
        "/api/v1/auth/login",
        data={
            "username": test_user.username,
            "password": "testpassword123"
        }
    )
    assert login_response.status_code == status.HTTP_200_OK
    refresh_token = login_response.json()["refresh_token"]
    
    # Refresh token
    refresh_response = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token}
    )
    assert refresh_response.status_code == status.HTTP_200_OK
    data = refresh_response.json()
    assert "access_token" in data
    assert "refresh_token" in data

