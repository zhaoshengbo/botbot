"""Arbitration Schemas"""
from pydantic import BaseModel, Field
from enum import Enum
from typing import Optional
from datetime import datetime


class ArbitrationStatus(str, Enum):
    """Arbitration status enum"""
    PENDING = "pending"              # Awaiting admin assignment
    UNDER_REVIEW = "under_review"    # Admin is reviewing
    PUBLISHER_FAVOR = "publisher_favor"  # Publisher wins
    CLAIMER_FAVOR = "claimer_favor"      # Claimer wins
    SPLIT_DECISION = "split_decision"    # Compromise
    RESOLVED = "resolved"                # Final resolution


class ArbitrationRequest(BaseModel):
    """Arbitration request schema"""
    contract_id: str
    requester_role: str = Field(..., pattern="^(publisher|claimer)$")
    reason: str = Field(..., min_length=10, max_length=1000)
    evidence_urls: Optional[list[str]] = None


class ArbitrationDecision(BaseModel):
    """Arbitration decision schema"""
    arbitration_id: str
    decision: ArbitrationStatus
    resolution_notes: str
    publisher_refund_percentage: float = Field(..., ge=0, le=100)
    claimer_payment_percentage: float = Field(..., ge=0, le=100)


class ArbitrationResponse(BaseModel):
    """Arbitration response schema"""
    id: str
    contract_id: str
    task_id: str
    task_title: Optional[str] = None
    publisher_id: str
    publisher_username: Optional[str] = None
    claimer_id: str
    claimer_username: Optional[str] = None
    requester_id: str
    requester_role: str
    status: ArbitrationStatus
    reason: str
    evidence_urls: Optional[list[str]] = None
    admin_notes: Optional[str] = None
    decision: Optional[ArbitrationStatus] = None
    publisher_refund_percentage: float = 0.0
    claimer_payment_percentage: float = 0.0
    resolution_notes: Optional[str] = None
    created_at: datetime
    assigned_admin_id: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None

    class Config:
        populate_by_name = True
        json_encoders = {datetime: lambda v: v.isoformat()}


class ArbitrationListResponse(BaseModel):
    """Arbitration list response"""
    arbitrations: list[ArbitrationResponse]
    total: int
    page: int
    page_size: int
