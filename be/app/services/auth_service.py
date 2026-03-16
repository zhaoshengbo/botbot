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
        # SECURITY: Reset failed attempts when new code is sent
        await db.users.update_one(
            {"phone_number": phone_number},
            {
                "$set": {
                    "verification_code": code,
                    "verification_code_expires": expires_at,
                    "phone_number": phone_number,
                    "verification_failed_attempts": 0
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
    async def direct_login(phone_number: str) -> Tuple[str, str, str]:
        """
        Direct login without verification code (for development/convenience)

        Args:
            phone_number: Phone number

        Returns:
            Tuple of (access_token, refresh_token, user_id)
        """
        db = get_database()

        # Find or create user
        user = await db.users.find_one({"phone_number": phone_number})

        if not user:
            # Create new user
            new_user = {
                "phone_number": phone_number,
                "phone_verified": True,
                "balance": 100.0,  # Initial shrimp food
                "frozen_balance": 0.0,
                "level": UserLevel.BRONZE.value,
                "rating": RatingInfo(
                    average_score=0.0,
                    total_ratings=0,
                    as_publisher=0,
                    as_claimer=0
                ).dict(),
                "ai_preferences": AIPreferences(
                    auto_bid_enabled=False,
                    max_bid_amount=None,
                    preferred_task_types=[]
                ).dict(),
                "tasks_published": 0,
                "tasks_completed": 0,
                "tasks_claimed": 0,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            result = await db.users.insert_one(new_user)
            user_id = str(result.inserted_id)
        else:
            user_id = str(user["_id"])

            # Mark phone as verified if not already
            if not user.get("phone_verified", False):
                await db.users.update_one(
                    {"_id": ObjectId(user_id)},
                    {
                        "$set": {
                            "phone_verified": True,
                            "updated_at": datetime.utcnow()
                        }
                    }
                )

        # Generate tokens
        access_token = create_access_token({"sub": user_id})
        refresh_token = create_refresh_token({"sub": user_id})

        return access_token, refresh_token, user_id

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

        # SECURITY: Check failed attempts to prevent brute force
        failed_attempts = user.get("verification_failed_attempts", 0)
        if failed_attempts >= 5:
            raise ValueError("Too many failed attempts. Please request a new verification code.")

        # Check expiry first
        if user.get("verification_code_expires", datetime.min) < datetime.utcnow():
            raise ValueError("Verification code expired")

        # Check code
        if user.get("verification_code") != code:
            # SECURITY: Increment failed attempts
            await db.users.update_one(
                {"phone_number": phone_number},
                {"$inc": {"verification_failed_attempts": 1}}
            )
            raise ValueError("Invalid verification code")

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
                "$unset": {
                    "verification_code": "",
                    "verification_code_expires": "",
                    "verification_failed_attempts": ""
                }
            }

            await db.users.update_one(
                {"phone_number": phone_number},
                {"$set": update_data}
            )

            # Refresh user data
            user = await db.users.find_one({"phone_number": phone_number})

        else:
            # Existing user - clear verification code and failed attempts
            await db.users.update_one(
                {"phone_number": phone_number},
                {
                    "$unset": {
                        "verification_code": "",
                        "verification_code_expires": "",
                        "verification_failed_attempts": ""
                    },
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
