"""Task Schemas"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class TaskStatus(str, Enum):
    """Task status enum"""
    OPEN = "open"
    BIDDING = "bidding"
    SELECTING = "selecting"  # Reached max bids, publisher must choose
    CONTRACTED = "contracted"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class TaskCreate(BaseModel):
    """Task creation schema"""
    title: str = Field(..., min_length=5, max_length=200)
    description: str = Field(..., min_length=10)
    deliverables: Optional[str] = None
    budget: float = Field(..., gt=0)
    deadline: Optional[datetime] = None
    category: Optional[str] = None
    tags: Optional[list[str]] = None
    bidding_period_hours: int = Field(default=48, ge=1, le=168)  # 1 hour to 7 days
    completion_deadline_hours: int = Field(default=168, ge=1, le=720)  # 1 hour to 30 days


class TaskUpdate(BaseModel):
    """Task update schema"""
    title: Optional[str] = Field(None, min_length=5, max_length=200)
    description: Optional[str] = Field(None, min_length=10)
    deliverables: Optional[str] = None
    budget: Optional[float] = Field(None, gt=0)


class TaskResponse(BaseModel):
    """Task response schema"""
    id: str
    publisher_id: str
    publisher_username: Optional[str] = None
    title: str
    description: str
    deliverables: Optional[str] = None
    budget: float
    deadline: Optional[datetime] = None
    category: Optional[str] = None
    tags: Optional[list[str]] = None
    bidding_period_hours: int
    completion_deadline_hours: int
    status: TaskStatus
    created_at: datetime
    bidding_ends_at: Optional[datetime] = None
    deadline_at: Optional[datetime] = None
    view_count: int = 0
    bid_count: int = 0

    class Config:
        populate_by_name = True
        json_encoders = {datetime: lambda v: v.isoformat()}


class TaskListResponse(BaseModel):
    """Task list response"""
    tasks: list[TaskResponse]
    total: int
    page: int
    page_size: int
