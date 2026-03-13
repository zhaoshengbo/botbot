"""Contract Schemas"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class ContractStatus(str, Enum):
    """Contract status enum"""
    ACTIVE = "active"
    COMPLETED = "completed"
    DISPUTED = "disputed"


class ContractCreate(BaseModel):
    """Contract creation schema (accepting a bid)"""
    bid_id: str


class DeliverableSubmit(BaseModel):
    """Deliverable submission schema"""
    deliverables_url: str


class ContractComplete(BaseModel):
    """Contract completion schema"""
    approved: bool
    rejection_reason: Optional[str] = None


class ContractResponse(BaseModel):
    """Contract response schema"""
    id: str = Field(..., alias="_id")
    task_id: str
    task_title: Optional[str] = None
    publisher_id: str
    publisher_username: Optional[str] = None
    claimer_id: str
    claimer_username: Optional[str] = None
    amount: float
    status: ContractStatus
    deliverables_submitted: bool = False
    deliverables_url: Optional[str] = None
    deliverables_submitted_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        populate_by_name = True
        json_encoders = {datetime: lambda v: v.isoformat()}


class ContractListResponse(BaseModel):
    """Contract list response"""
    contracts: list[ContractResponse]
    total: int
