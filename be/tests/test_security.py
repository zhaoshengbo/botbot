"""
Unit tests for security functions
"""
import pytest
from datetime import timedelta
from jose import jwt

from app.core.security import (
    create_access_token,
    verify_password,
    get_password_hash,
)
from app.core.config import get_settings

settings = get_settings()


@pytest.mark.unit
class TestSecurity:
    """Test security utilities"""

    def test_password_hashing(self):
        """Test password hashing and verification"""
        password = "test_password_123"
        hashed = get_password_hash(password)

        # Hash should be different from original
        assert hashed != password

        # Should verify correctly
        assert verify_password(password, hashed) is True

        # Wrong password should not verify
        assert verify_password("wrong_password", hashed) is False

    def test_password_hash_unique(self):
        """Test that same password produces different hashes"""
        password = "same_password"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)

        # Different hashes (due to salt)
        assert hash1 != hash2

        # Both should verify
        assert verify_password(password, hash1)
        assert verify_password(password, hash2)

    def test_create_access_token(self):
        """Test JWT token creation"""
        data = {"sub": "+8613800138000", "user_id": "test_user_id"}
        token = create_access_token(data)

        # Should return a string token
        assert isinstance(token, str)
        assert len(token) > 0

        # Decode and verify
        payload = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
        assert payload["sub"] == "+8613800138000"
        assert payload["user_id"] == "test_user_id"
        assert "exp" in payload

    def test_create_access_token_with_expiration(self):
        """Test JWT token with custom expiration"""
        data = {"sub": "+8613800138000"}
        expires_delta = timedelta(minutes=15)
        token = create_access_token(data, expires_delta)

        payload = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
        assert "exp" in payload

    def test_token_contains_expiration(self):
        """Test that tokens always contain expiration"""
        data = {"sub": "test_user"}
        token = create_access_token(data)

        payload = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
        assert "exp" in payload
        assert isinstance(payload["exp"], int)
