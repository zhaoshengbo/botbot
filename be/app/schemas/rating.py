"""Rating Schemas"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class RatingType(str, Enum):
    """Rating type enum"""
    PUBLISHER_TO_CLAIMER = "publisher_to_claimer"
    CLAIMER_TO_PUBLISHER = "claimer_to_publisher"


class RatingCreate(BaseModel):
    """Rating creation schema"""
    contract_id: str
    score: Optional[int] = Field(None, ge=1, le=5)  # Auto-calculated from sub-scores if not provided
    quality_score: int = Field(..., ge=1, le=5)
    communication_score: int = Field(..., ge=1, le=5)
    timeliness_score: int = Field(..., ge=1, le=5)
    comment: Optional[str] = Field(None, max_length=1000)


class RatingResponse(BaseModel):
    """Rating response schema"""
    id: str = Field(..., alias="_id")
    contract_id: str
    task_id: str
    rater_id: str
    rater_username: Optional[str] = None
    ratee_id: str
    ratee_username: Optional[str] = None
    rating_type: RatingType
    score: int
    quality_score: int
    communication_score: int
    timeliness_score: int
    comment: Optional[str] = None
    created_at: datetime

    class Config:
        populate_by_name = True
        json_encoders = {datetime: lambda v: v.isoformat()}


class RatingListResponse(BaseModel):
    """Rating list response"""
    ratings: list[RatingResponse]
    total: int
