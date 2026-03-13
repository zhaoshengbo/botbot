"""Authentication Service"""
from datetime import datetime, timedelta
from typing import Optional, Tuple
from bson import ObjectId
from app.db.mongodb import get_database
from app.core.security import create_access_token, create_refresh_token, verify_token
from app.services.sms_service import sms_service
from app.schemas.user import UserLevel, RatingInfo, AIPreferences
import random


class AuthService:
    """Authentication service"""

    @staticmethod
    async def send_verification_code(phone_number: str) -> dict:
        """
        Send verification code to phone number

        Args:
            phone_number: Phone number

        Returns:
            dict with success status and expiry time
        """
        db = get_database()

        # Generate verification code
        code = sms_service.generate_code()

        # Store code in database with expiry (5 minutes)
        expires_at = datetime.utcnow() + timedelta(minutes=5)

        # Update or create temp verification record
        await db.users.update_one(
            {"phone_number": phone_number},
            {
                "$set": {
                    "verification_code": code,
                    "verification_code_expires": expires_at,
                    "phone_number": phone_number,
                }
            },
            upsert=True
        )

        # Send SMS
        success = await sms_service.send_verification_code(phone_number, code)

        if not success:
            raise Exception("Failed to send verification code")

        return {
            "message": "Verification code sent",
            "expires_in": 300
        }

    @staticmethod
    async def verify_code_and_login(phone_number: str, code: str) -> Tuple[str, str, str]:
        """
        Verify code and login/register user

        Args:
            phone_number: Phone number
            code: Verification code

        Returns:
            Tuple of (access_token, refresh_token, user_id)
        """
        db = get_database()

        # Find user with matching code
        user = await db.users.find_one({"phone_number": phone_number})

        if not user:
            raise ValueError("Invalid phone number or code")

        # Check code
        if user.get("verification_code") != code:
            raise ValueError("Invalid verification code")

        # Check expiry
        if user.get("verification_code_expires", datetime.min) < datetime.utcnow():
            raise ValueError("Verification code expired")

        # Check if user is already registered (has phone_verified=True)
        is_new_user = not user.get("phone_verified", False)

        if is_new_user:
            # New user - initialize with default values
            username = f"Lobster_{random.randint(10000, 99999)}"

            update_data = {
                "username": username,
                "phone_verified": True,
                "shrimp_food_balance": 100.0,
                "shrimp_food_frozen": 0.0,
                "level": UserLevel.BRONZE.value,
                "level_points": 0,
                "tasks_published": 0,
                "tasks_completed_as_publisher": 0,
                "tasks_claimed": 0,
                "tasks_completed_as_claimer": 0,
                "rating_as_publisher": {
                    "average": 5.0,
                    "count": 0,
                    "total": 0.0
                },
                "rating_as_claimer": {
                    "average": 5.0,
                    "count": 0,
                    "total": 0.0
                },
                "ai_preferences": {
                    "auto_bid_enabled": True,
                    "max_bid_amount": 100.0,
                    "min_confidence_threshold": 0.7
                },
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "$unset": {"verification_code": "", "verification_code_expires": ""}
            }

            await db.users.update_one(
                {"phone_number": phone_number},
                {"$set": update_data}
            )

            # Refresh user data
            user = await db.users.find_one({"phone_number": phone_number})

        else:
            # Existing user - just clear verification code
            await db.users.update_one(
                {"phone_number": phone_number},
                {
                    "$unset": {"verification_code": "", "verification_code_expires": ""},
                    "$set": {"updated_at": datetime.utcnow()}
                }
            )

        user_id = str(user["_id"])

        # Generate tokens
        access_token = create_access_token({"sub": user_id})
        refresh_token = create_refresh_token({"sub": user_id})

        return access_token, refresh_token, user_id

    @staticmethod
    async def refresh_access_token(refresh_token: str) -> str:
        """
        Refresh access token using refresh token

        Args:
            refresh_token: Refresh token

        Returns:
            New access token
        """
        payload = verify_token(refresh_token)

        if payload.get("type") != "refresh":
            raise ValueError("Invalid token type")

        user_id = payload.get("sub")
        if not user_id:
            raise ValueError("Invalid token")

        # Verify user still exists
        db = get_database()
        user = await db.users.find_one({"_id": ObjectId(user_id)})

        if not user:
            raise ValueError("User not found")

        # Generate new access token
        access_token = create_access_token({"sub": user_id})

        return access_token

    @staticmethod
    async def direct_login_or_register(phone_number: str) -> Tuple[str, str, str, bool]:
        """
        Direct login or register with phone number only (no verification code needed)

        Args:
            phone_number: Phone number

        Returns:
            Tuple of (access_token, refresh_token, user_id, is_new_user)
        """
        db = get_database()

        # Check if user exists
        user = await db.users.find_one({"phone_number": phone_number})

        is_new_user = False

        if not user:
            # New user - create account with default values
            is_new_user = True
            username = f"Lobster_{random.randint(10000, 99999)}"

            user_data = {
                "phone_number": phone_number,
                "username": username,
                "phone_verified": True,
                "shrimp_food_balance": 100.0,
                "shrimp_food_frozen": 0.0,
                "level": UserLevel.BRONZE.value,
                "level_points": 0,
                "tasks_published": 0,
                "tasks_completed_as_publisher": 0,
                "tasks_claimed": 0,
                "tasks_completed_as_claimer": 0,
                "rating_as_publisher": {
                    "average": 5.0,
                    "count": 0,
                    "total": 0.0
                },
                "rating_as_claimer": {
                    "average": 5.0,
                    "count": 0,
                    "total": 0.0
                },
                "ai_preferences": {
                    "auto_bid_enabled": True,
                    "max_bid_amount": 100.0,
                    "min_confidence_threshold": 0.7
                },
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
            }

            result = await db.users.insert_one(user_data)
            user = await db.users.find_one({"_id": result.inserted_id})

        else:
            # Existing user - just update last access time
            await db.users.update_one(
                {"_id": user["_id"]},
                {"$set": {"updated_at": datetime.utcnow()}}
            )

        user_id = str(user["_id"])

        # Generate tokens
        access_token = create_access_token({"sub": user_id})
        refresh_token = create_refresh_token({"sub": user_id})

        return access_token, refresh_token, user_id, is_new_user


auth_service = AuthService()
