"""Authentication API Routes"""
from fastapi import APIRouter, HTTPException, status, Depends
from app.schemas.auth import (
    SendCodeRequest,
    SendCodeResponse,
    VerifyCodeRequest,
    TokenResponse,
    RefreshTokenRequest,
)
from app.schemas.user import UserResponse
from app.services.auth_service import auth_service
from app.core.security import get_current_user_id
from app.db.mongodb import get_database
from bson import ObjectId

router = APIRouter()


@router.post("/send-code", response_model=SendCodeResponse)
async def send_verification_code(request: SendCodeRequest):
    """Send SMS verification code to phone number"""
    try:
        result = await auth_service.send_verification_code(request.phone_number)
        return result
    except Exception as e:
        # SECURITY: Don't leak internal error details
        print(f"Error in send_verification_code: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send verification code. Please try again."
        )


@router.post("/verify-code", response_model=TokenResponse)
async def verify_code_and_login(request: VerifyCodeRequest):
    """Verify code and login/register user"""
    try:
        access_token, refresh_token, user_id = await auth_service.verify_code_and_login(
            request.phone_number,
            request.verification_code
        )

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            user_id=user_id
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        # SECURITY: Don't leak internal error details
        print(f"Error in verify_code_and_login: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication failed. Please try again."
        )


# SECURITY: Direct login endpoint disabled - use verification code flow
# @router.post("/direct-login", response_model=TokenResponse)
# async def direct_login_or_register(request: SendCodeRequest):
#     """Direct login/register with phone number only (no verification code)
#     WARNING: This endpoint is disabled for security reasons.
#     Use /send-code and /verify-code instead.
#     """
#     raise HTTPException(
#         status_code=status.HTTP_403_FORBIDDEN,
#         detail="Direct login is disabled. Please use verification code flow."
#     )


@router.post("/refresh", response_model=dict)
async def refresh_token(request: RefreshTokenRequest):
    """Refresh access token"""
    try:
        access_token = await auth_service.refresh_access_token(request.refresh_token)
        return {"access_token": access_token, "token_type": "bearer"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user(user_id: str = Depends(get_current_user_id)):
    """Get current logged-in user information"""
    db = get_database()

    user = await db.users.find_one({"_id": ObjectId(user_id)})

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    user["_id"] = str(user["_id"])
    return UserResponse(**user)
