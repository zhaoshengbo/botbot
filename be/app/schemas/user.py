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


class RatingInfo(BaseModel):
    """Rating information"""
    average: float = 5.0
    count: int = 0
    total: float = 0.0


class AIPreferences(BaseModel):
    """AI preferences"""
    auto_bid_enabled: bool = True
    max_bid_amount: float = 100.0
    min_confidence_threshold: float = 0.7


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
    username: Optional[str] = None
    nickname: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    skills: Optional[list[str]] = None
    ai_preferences: Optional[AIPreferences] = None
