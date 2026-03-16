"""Bid Schemas"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class BidStatus(str, Enum):
    """Bid status enum"""
    ACTIVE = "active"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"


class AIAnalysis(BaseModel):
    """AI analysis result"""
    feasibility_score: float = Field(..., ge=0, le=1)
    estimated_hours: float = Field(..., gt=0)
    confidence: float = Field(..., ge=0, le=1)
    reasoning: str


class AnalyzeTaskRequest(BaseModel):
    """Analyze task request"""
    task_id: str


class AnalyzeTaskResponse(BaseModel):
    """Analyze task response"""
    can_complete: bool
    suggested_bid_amount: Optional[float] = None
    analysis: AIAnalysis
    should_bid: bool


class BidCreate(BaseModel):
    """Bid creation schema"""
    task_id: str
    amount: float = Field(..., gt=0)
    estimated_hours: Optional[float] = Field(None, gt=0)
    proposal: Optional[str] = Field(None, max_length=1000)
    message: Optional[str] = Field(None, max_length=500)


class BidResponse(BaseModel):
    """Bid response schema"""
    id: str
    task_id: str
    bidder_id: str
    bidder_username: Optional[str] = None
    amount: float
    estimated_hours: Optional[float] = None
    proposal: Optional[str] = None
    message: Optional[str] = None
    ai_analysis: Optional[AIAnalysis] = None
    status: BidStatus
    created_at: datetime

    class Config:
        populate_by_name = True
        json_encoders = {datetime: lambda v: v.isoformat()}


class BidListResponse(BaseModel):
    """Bid list response"""
    bids: list[BidResponse]
    total: int
