"""Authentication Schemas"""
from pydantic import BaseModel


class SendCodeRequest(BaseModel):
    """Send verification code request"""
    phone_number: str


class SendCodeResponse(BaseModel):
    """Send verification code response"""
    message: str
    expires_in: int = 300  # 5 minutes


class VerifyCodeRequest(BaseModel):
    """Verify code request"""
    phone_number: str
    verification_code: str


class TokenResponse(BaseModel):
    """Token response"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user_id: str


class RefreshTokenRequest(BaseModel):
    """Refresh token request"""
    refresh_token: str
