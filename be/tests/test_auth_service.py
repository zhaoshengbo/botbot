"""
Unit tests for authentication service
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime, timedelta

from app.services.auth_service import AuthService
from app.schemas.auth import SendCodeRequest, VerifyCodeRequest


@pytest.mark.unit
@pytest.mark.asyncio
class TestAuthService:
    """Test authentication service"""

    @pytest.fixture
    def auth_service(self, test_db):
        """Create auth service instance"""
        return AuthService(test_db)

    async def test_send_verification_code_new_user(self, auth_service):
        """Test sending verification code to new user"""
        with patch("app.services.auth_service.SMSService") as mock_sms:
            mock_sms_instance = AsyncMock()
            mock_sms_instance.send_verification_code.return_value = True
            mock_sms.return_value = mock_sms_instance

            request = SendCodeRequest(phone_number="+8613800138001")
            result = await auth_service.send_verification_code(request)

            assert result["success"] is True
            assert "expires_at" in result
            mock_sms_instance.send_verification_code.assert_called_once()

    async def test_send_verification_code_existing_user(
        self, auth_service, test_user, test_db
    ):
        """Test sending code to existing user"""
        with patch("app.services.auth_service.SMSService") as mock_sms:
            mock_sms_instance = AsyncMock()
            mock_sms_instance.send_verification_code.return_value = True
            mock_sms.return_value = mock_sms_instance

            request = SendCodeRequest(phone_number=test_user["phone_number"])
            result = await auth_service.send_verification_code(request)

            assert result["success"] is True
            assert "expires_at" in result

    async def test_verify_code_success_new_user(self, auth_service, test_db):
        """Test successful verification and user creation"""
        phone_number = "+8613800138002"

        # First send code
        with patch("app.services.auth_service.SMSService") as mock_sms:
            mock_sms_instance = AsyncMock()
            mock_sms_instance.send_verification_code.return_value = True
            mock_sms.return_value = mock_sms_instance

            await auth_service.send_verification_code(
                SendCodeRequest(phone_number=phone_number)
            )

        # Get the code from database
        verification = await test_db.verifications.find_one(
            {"phone_number": phone_number}
        )
        assert verification is not None

        # Verify code
        request = VerifyCodeRequest(
            phone_number=phone_number, code=verification["code"]
        )
        result = await auth_service.verify_code_and_login(request)

        assert "access_token" in result
        assert "refresh_token" in result
        assert result["token_type"] == "bearer"
        assert "user" in result

        # Check user was created
        user = await test_db.users.find_one({"phone_number": phone_number})
        assert user is not None
        assert user["shrimp_food_balance"] == 100.0  # Initial balance
        assert user["level"] == "bronze"

    async def test_verify_code_invalid_code(self, auth_service, test_db):
        """Test verification with invalid code"""
        phone_number = "+8613800138003"

        # Send code first
        with patch("app.services.auth_service.SMSService") as mock_sms:
            mock_sms_instance = AsyncMock()
            mock_sms_instance.send_verification_code.return_value = True
            mock_sms.return_value = mock_sms_instance

            await auth_service.send_verification_code(
                SendCodeRequest(phone_number=phone_number)
            )

        # Try with wrong code
        request = VerifyCodeRequest(phone_number=phone_number, code="000000")

        with pytest.raises(Exception):  # Should raise invalid code error
            await auth_service.verify_code_and_login(request)

    async def test_verify_code_expired(self, auth_service, test_db):
        """Test verification with expired code"""
        phone_number = "+8613800138004"

        # Insert expired verification
        await test_db.verifications.insert_one(
            {
                "phone_number": phone_number,
                "code": "123456",
                "expires_at": datetime.utcnow() - timedelta(minutes=1),  # Expired
                "created_at": datetime.utcnow() - timedelta(minutes=10),
            }
        )

        request = VerifyCodeRequest(phone_number=phone_number, code="123456")

        with pytest.raises(Exception):  # Should raise expired error
            await auth_service.verify_code_and_login(request)

    async def test_direct_login_new_user(self, auth_service, test_db):
        """Test direct login creates new user"""
        phone_number = "+8613800138005"

        result = await auth_service.direct_login(phone_number)

        assert "access_token" in result
        assert "refresh_token" in result
        assert result["token_type"] == "bearer"

        # Verify user was created
        user = await test_db.users.find_one({"phone_number": phone_number})
        assert user is not None
        assert user["shrimp_food_balance"] == 100.0

    async def test_direct_login_existing_user(
        self, auth_service, test_user, test_db
    ):
        """Test direct login with existing user"""
        result = await auth_service.direct_login(test_user["phone_number"])

        assert "access_token" in result
        assert "user" in result
        assert result["user"]["username"] == test_user["username"]

    async def test_rate_limiting_send_code(self, auth_service, test_db):
        """Test rate limiting for sending codes"""
        phone_number = "+8613800138006"

        with patch("app.services.auth_service.SMSService") as mock_sms:
            mock_sms_instance = AsyncMock()
            mock_sms_instance.send_verification_code.return_value = True
            mock_sms.return_value = mock_sms_instance

            # First request should succeed
            request = SendCodeRequest(phone_number=phone_number)
            result1 = await auth_service.send_verification_code(request)
            assert result1["success"] is True

            # Immediate second request should be rate limited
            with pytest.raises(Exception):  # Should raise rate limit error
                await auth_service.send_verification_code(request)
