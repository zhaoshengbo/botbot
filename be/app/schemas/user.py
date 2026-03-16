"""User Schemas"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class UserLevel(str, Enum):
    """User level enum"""
    BRONZE = "Bronze"
    SILVER = "Silver"
    GOLD = "Gold"
    PLATINUM = "Platinum"
    DIAMOND = "Diamond"


class UserRole(str, Enum):
    """User role enum"""
    USER = "user"
    ADMIN = "admin"


class RatingInfo(BaseModel):
    """Rating information"""
    average: float = 5.0
    count: int = 0
    total: float = 0.0


class AIPreferences(BaseModel):
    """AI preferences"""
    # Bidding preferences
    auto_bid_enabled: bool = True
    max_bid_amount: float = 100.0
    min_confidence_threshold: float = 0.7

    # Recharge preferences
    auto_recharge_enabled: bool = False
    auto_recharge_threshold: float = 50.0  # Auto recharge when balance < this
    auto_recharge_amount: float = 100.0  # Amount to recharge (in shrimp food)
    preferred_payment_method: str = "alipay"  # alipay or wechat

    # Withdrawal preferences
    auto_withdrawal_enabled: bool = False
    auto_withdrawal_threshold: float = 500.0  # Auto withdraw when balance > this
    auto_withdrawal_amount: float = 300.0  # Amount to withdraw (in shrimp food)
    withdrawal_account_info: Optional[dict] = None  # Saved account info


class UserBase(BaseModel):
    """Base user schema"""
    phone_number: str
    username: Optional[str] = None


class UserCreate(BaseModel):
    """User creation schema"""
    phone_number: str
    verification_code: str


class UserResponse(BaseModel):
    """User response schema"""
    id: str = Field(..., alias="_id")
    phone_number: str
    username: str
    nickname: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    skills: Optional[list[str]] = None
    phone_verified: bool
    shrimp_food_balance: float
    shrimp_food_frozen: float
    level: UserLevel
    level_points: int
    role: UserRole = UserRole.USER
    tasks_published: int
    tasks_completed_as_publisher: int
    tasks_claimed: int
    tasks_completed_as_claimer: int
    rating_as_publisher: RatingInfo
    rating_as_claimer: RatingInfo
    ai_preferences: AIPreferences
    created_at: datetime

    class Config:
        populate_by_name = True
        json_encoders = {datetime: lambda v: v.isoformat()}


class UserUpdate(BaseModel):
    """User update schema"""
    username: Optional[str] = Field(None, min_length=3, max_length=50, pattern=r'^[a-zA-Z0-9_]+$')
    nickname: Optional[str] = Field(None, max_length=100)
    bio: Optional[str] = Field(None, max_length=500)
    avatar_url: Optional[str] = Field(None, max_length=500)
    skills: Optional[list[str]] = Field(None, max_length=20)  # Max 20 skills
    ai_preferences: Optional[AIPreferences] = None
