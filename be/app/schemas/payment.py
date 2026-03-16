"""Payment Schemas"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class PaymentMethod(str, Enum):
    """Payment method enum"""
    ALIPAY = "alipay"
    WECHAT = "wechat"


class RechargeStatus(str, Enum):
    """Recharge order status"""
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"


class WithdrawalStatus(str, Enum):
    """Withdrawal order status"""
    PENDING = "pending"
    REVIEWING = "reviewing"
    APPROVED = "approved"
    REJECTED = "rejected"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class WithdrawalMethod(str, Enum):
    """Withdrawal method enum"""
    ALIPAY = "alipay"
    WECHAT = "wechat"
    BANK = "bank"


class DeviceInfo(BaseModel):
    """Device information"""
    ip: str
    user_agent: str
    device_type: Optional[str] = "web"


class WithdrawalAccount(BaseModel):
    """Withdrawal account information"""
    account_type: str
    account_name: str
    account_number: str
    bank_name: Optional[str] = None


# Recharge Schemas
class RechargeCreate(BaseModel):
    """Create recharge order"""
    amount_rmb: float = Field(..., gt=0, description="充值金额（人民币）")
    payment_method: PaymentMethod
    device_info: Optional[DeviceInfo] = None


class RechargeResponse(BaseModel):
    """Recharge order response"""
    id: str = Field(..., alias="_id")
    user_id: str
    order_no: str
    amount_rmb: float
    amount_shrimp: float
    exchange_rate: float
    payment_method: PaymentMethod
    payment_status: RechargeStatus
    payment_channel_order_no: Optional[str] = None
    payment_time: Optional[datetime] = None
    created_at: datetime

    class Config:
        populate_by_name = True
        json_encoders = {datetime: lambda v: v.isoformat()}


class RechargePaymentInfo(BaseModel):
    """Payment information for client"""
    order_no: str
    payment_method: PaymentMethod
    payment_url: Optional[str] = None
    payment_form: Optional[str] = None
    qr_code: Optional[str] = None


# Withdrawal Schemas
class WithdrawalCreate(BaseModel):
    """Create withdrawal order"""
    amount_shrimp: float = Field(..., gt=0, description="提现虾粮数量")
    withdrawal_method: WithdrawalMethod
    withdrawal_account: WithdrawalAccount
    device_info: Optional[DeviceInfo] = None


class WithdrawalResponse(BaseModel):
    """Withdrawal order response"""
    id: str = Field(..., alias="_id")
    user_id: str
    order_no: str
    amount_shrimp: float
    amount_rmb: float
    exchange_rate: float
    withdrawal_method: WithdrawalMethod
    withdrawal_account: WithdrawalAccount
    status: WithdrawalStatus
    created_at: datetime
    reviewed_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    rejection_reason: Optional[str] = None

    class Config:
        populate_by_name = True
        json_encoders = {datetime: lambda v: v.isoformat()}


class WithdrawalReview(BaseModel):
    """Withdrawal review action"""
    approved: bool
    rejection_reason: Optional[str] = None


# Transaction Log Schemas
class TransactionLogResponse(BaseModel):
    """Transaction log response"""
    id: str = Field(..., alias="_id")
    transaction_type: str
    user_id: Optional[str] = None
    amount: float
    balance_before: float
    balance_after: float
    description: str
    created_at: datetime

    class Config:
        populate_by_name = True
        json_encoders = {datetime: lambda v: v.isoformat()}


# Statistics
class PlatformStatsResponse(BaseModel):
    """Platform statistics"""
    total_fee_income: float
    current_balance: float
    total_recharge_amount: float
    total_withdrawal_amount: float
    pending_withdrawal_count: int
