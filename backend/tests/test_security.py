"""
Tests for security utilities
"""
import pytest
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    decode_token,
    validate_password_policy
)


def test_password_hashing():
    """Test password hashing and verification"""
    password = "TestPassword123!"
    hashed = get_password_hash(password)
    
    assert hashed != password
    assert verify_password(password, hashed)
    assert not verify_password("wrongpassword", hashed)


def test_password_policy_validation():
    """Test password policy validation"""
    # Valid password
    is_valid, errors = validate_password_policy("SecurePass123!")
    assert is_valid
    assert len(errors) == 0
    
    # Too short
    is_valid, errors = validate_password_policy("Short1!")
    assert not is_valid
    assert len(errors) > 0
    
    # No uppercase
    is_valid, errors = validate_password_policy("nopassword123!")
    assert not is_valid
    
    # No lowercase
    is_valid, errors = validate_password_policy("NOPASSWORD123!")
    assert not is_valid
    
    # No numbers
    is_valid, errors = validate_password_policy("NoNumbers!")
    assert not is_valid
    
    # No special characters
    is_valid, errors = validate_password_policy("NoSpecial123")
    assert not is_valid


def test_jwt_token_creation():
    """Test JWT token creation and decoding"""
    data = {"sub": "user123", "role": "operator"}
    token = create_access_token(data)
    
    assert token is not None
    assert isinstance(token, str)
    
    decoded = decode_token(token)
    assert decoded["sub"] == "user123"
    assert decoded["role"] == "operator"


def test_jwt_token_invalid():
    """Test JWT token validation with invalid token"""
    with pytest.raises(Exception):  # Should raise HTTPException
        decode_token("invalid.token.here")

