"""Authentication Schemas"""
from pydantic import BaseModel, Field, field_validator
import re


class SendCodeRequest(BaseModel):
    """Send verification code request"""
    phone_number: str = Field(..., min_length=11, max_length=11, description="11-digit phone number")

    @field_validator('phone_number')
    @classmethod
    def validate_phone_number(cls, v: str) -> str:
        """Validate phone number format (Chinese mobile)"""
        # Remove any spaces or dashes
        v = v.replace(' ', '').replace('-', '')

        # Check if it's 11 digits starting with 1
        if not re.match(r'^1[3-9]\d{9}$', v):
            raise ValueError('Invalid phone number format. Must be 11 digits starting with 1.')

        return v


class SendCodeResponse(BaseModel):
    """Send verification code response"""
    message: str
    expires_in: int = 300  # 5 minutes


class VerifyCodeRequest(BaseModel):
    """Verify code request"""
    phone_number: str = Field(..., min_length=11, max_length=11)
    verification_code: str = Field(..., min_length=6, max_length=6, pattern=r'^\d{6}$')

    @field_validator('phone_number')
    @classmethod
    def validate_phone_number(cls, v: str) -> str:
        """Validate phone number format"""
        v = v.replace(' ', '').replace('-', '')
        if not re.match(r'^1[3-9]\d{9}$', v):
            raise ValueError('Invalid phone number format')
        return v


class TokenResponse(BaseModel):
    """Token response"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user_id: str


class RefreshTokenRequest(BaseModel):
    """Refresh token request"""
    refresh_token: str
