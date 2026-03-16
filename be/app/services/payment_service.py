"""Payment Service"""
from datetime import datetime
from typing import Optional, Dict, Any
from bson import ObjectId
import time
import random

from app.db.mongodb import get_database
from app.core.config import settings
from app.schemas.payment import (
    RechargeStatus,
    WithdrawalStatus,
    PlatformWithdrawalStatus,
    PaymentMethod,
    WithdrawalMethod,
    DeviceInfo,
    WithdrawalAccount
)


class PaymentService:
    """Payment service for recharge, withdrawal, and fee management"""

    @staticmethod
    def generate_order_no(prefix: str) -> str:
        """
        Generate unique order number
        Format: PREFIX + timestamp + 6-digit random number
        """
        timestamp = int(time.time() * 1000)
        random_num = random.randint(100000, 999999)
        return f"{prefix}{timestamp}{random_num}"

    @staticmethod
    async def create_recharge_order(
        user_id: str,
        amount_rmb: float,
        payment_method: PaymentMethod,
        device_info: Optional[DeviceInfo] = None
    ) -> Dict[str, Any]:
        """
        Create recharge order
        """
        db = get_database()

        # Validate amount
        if amount_rmb < settings.MIN_RECHARGE_AMOUNT:
            raise ValueError(f"Minimum recharge amount is {settings.MIN_RECHARGE_AMOUNT} RMB")

        # Calculate shrimp amount
        amount_shrimp = amount_rmb * settings.RECHARGE_EXCHANGE_RATE

        # Generate order number
        order_no = PaymentService.generate_order_no("RCH")

        # Create order document
        order_doc = {
            "user_id": ObjectId(user_id),
            "order_no": order_no,
            "amount_rmb": amount_rmb,
            "amount_shrimp": amount_shrimp,
            "exchange_rate": settings.RECHARGE_EXCHANGE_RATE,
            "payment_method": payment_method.value,
            "payment_status": RechargeStatus.PENDING.value,
            "payment_channel_order_no": None,
            "payment_time": None,
            "device_info": device_info.model_dump() if device_info else None,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "callback_received_at": None,
            "callback_verified": False,
            "remarks": None
        }

        # Insert order
        result = await db.recharge_orders.insert_one(order_doc)
        order_doc["_id"] = result.inserted_id

        return order_doc

    @staticmethod
    async def complete_recharge_order(
        order_no: str,
        payment_channel_order_no: str,
        payment_time: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Complete recharge order after payment callback
        Uses MongoDB transaction for atomicity
        """
        db = get_database()

        if payment_time is None:
            payment_time = datetime.utcnow()

        # Find order
        order = await db.recharge_orders.find_one({"order_no": order_no})
        if not order:
            raise ValueError(f"Recharge order not found: {order_no}")

        # Check if already completed (idempotency)
        if order["payment_status"] == RechargeStatus.SUCCESS.value:
            return order

        # Check status
        if order["payment_status"] != RechargeStatus.PENDING.value:
            raise ValueError(f"Order status is {order['payment_status']}, cannot complete")

        # Use transaction for atomicity
        async with await db.client.start_session() as session:
            async with session.start_transaction():
                # Update order status
                await db.recharge_orders.update_one(
                    {"_id": order["_id"]},
                    {
                        "$set": {
                            "payment_status": RechargeStatus.SUCCESS.value,
                            "payment_channel_order_no": payment_channel_order_no,
                            "payment_time": payment_time,
                            "callback_received_at": datetime.utcnow(),
                            "callback_verified": True,
                            "updated_at": datetime.utcnow()
                        }
                    },
                    session=session
                )

                # Get user balance before update
                user = await db.users.find_one(
                    {"_id": order["user_id"]},
                    session=session
                )
                balance_before = user.get("shrimp_food_balance", 0)

                # Add shrimp to user balance
                await db.users.update_one(
                    {"_id": order["user_id"]},
                    {"$inc": {"shrimp_food_balance": order["amount_shrimp"]}},
                    session=session
                )

                # Record transaction log
                await PaymentService._record_transaction_log(
                    transaction_type="recharge",
                    user_id=order["user_id"],
                    amount=order["amount_shrimp"],
                    balance_before=balance_before,
                    balance_after=balance_before + order["amount_shrimp"],
                    related_order_id=order["_id"],
                    related_order_type="recharge_order",
                    description=f"Recharge {order['amount_rmb']} RMB",
                    session=session
                )

        # Return updated order
        return await db.recharge_orders.find_one({"order_no": order_no})

    @staticmethod
    async def create_withdrawal_order(
        user_id: str,
        amount_shrimp: float,
        withdrawal_method: WithdrawalMethod,
        withdrawal_account: WithdrawalAccount,
        device_info: Optional[DeviceInfo] = None
    ) -> Dict[str, Any]:
        """
        Create withdrawal order
        """
        db = get_database()

        # Validate amount
        if amount_shrimp < settings.MIN_WITHDRAWAL_AMOUNT:
            raise ValueError(f"Minimum withdrawal amount is {settings.MIN_WITHDRAWAL_AMOUNT} kg")

        # Get user
        user = await db.users.find_one({"_id": ObjectId(user_id)})
        if not user:
            raise ValueError("User not found")

        # Check available balance
        available_balance = user.get("shrimp_food_balance", 0) - user.get("shrimp_food_frozen", 0)
        if available_balance < amount_shrimp:
            raise ValueError(f"Insufficient balance. Available: {available_balance} kg")

        # Calculate RMB amount
        amount_rmb = amount_shrimp / settings.WITHDRAWAL_EXCHANGE_RATE

        # Generate order number
        order_no = PaymentService.generate_order_no("WDR")

        # Use transaction
        async with await db.client.start_session() as session:
            async with session.start_transaction():
                # Create withdrawal order
                order_doc = {
                    "user_id": ObjectId(user_id),
                    "order_no": order_no,
                    "amount_shrimp": amount_shrimp,
                    "amount_rmb": amount_rmb,
                    "exchange_rate": settings.WITHDRAWAL_EXCHANGE_RATE,
                    "withdrawal_method": withdrawal_method.value,
                    "withdrawal_account": withdrawal_account.model_dump(),
                    "status": WithdrawalStatus.PENDING.value,
                    "created_at": datetime.utcnow(),
                    "reviewed_at": None,
                    "reviewed_by": None,
                    "completed_at": None,
                    "rejection_reason": None,
                    "transfer_order_no": None,
                    "remarks": None,
                    "device_info": device_info.model_dump() if device_info else None
                }

                result = await db.withdrawal_orders.insert_one(order_doc, session=session)
                order_doc["_id"] = result.inserted_id

                # Freeze shrimp
                balance_before = user.get("shrimp_food_balance", 0)
                await db.users.update_one(
                    {"_id": ObjectId(user_id)},
                    {"$inc": {"shrimp_food_frozen": amount_shrimp}},
                    session=session
                )

                # Record transaction log
                await PaymentService._record_transaction_log(
                    transaction_type="withdrawal_freeze",
                    user_id=ObjectId(user_id),
                    amount=amount_shrimp,
                    balance_before=balance_before,
                    balance_after=balance_before,  # Balance unchanged, just frozen
                    related_order_id=order_doc["_id"],
                    related_order_type="withdrawal_order",
                    description=f"Withdrawal freeze {amount_shrimp} kg",
                    session=session
                )

        return order_doc

    @staticmethod
    async def cancel_withdrawal_order(order_no: str, user_id: str) -> Dict[str, Any]:
        """
        Cancel withdrawal order (only PENDING status can be cancelled)
        """
        db = get_database()

        # Find order
        order = await db.withdrawal_orders.find_one({"order_no": order_no})
        if not order:
            raise ValueError(f"Withdrawal order not found: {order_no}")

        # Verify user
        if str(order["user_id"]) != user_id:
            raise ValueError("Not authorized to cancel this order")

        # Check status
        if order["status"] != WithdrawalStatus.PENDING.value:
            raise ValueError(f"Cannot cancel order with status: {order['status']}")

        # Use transaction
        async with await db.client.start_session() as session:
            async with session.start_transaction():
                # Update order status
                await db.withdrawal_orders.update_one(
                    {"_id": order["_id"]},
                    {
                        "$set": {
                            "status": WithdrawalStatus.FAILED.value,
                            "rejection_reason": "Cancelled by user"
                        }
                    },
                    session=session
                )

                # Unfreeze shrimp
                user = await db.users.find_one({"_id": order["user_id"]}, session=session)
                balance_before = user.get("shrimp_food_balance", 0)

                await db.users.update_one(
                    {"_id": order["user_id"]},
                    {"$inc": {"shrimp_food_frozen": -order["amount_shrimp"]}},
                    session=session
                )

                # Record transaction log
                await PaymentService._record_transaction_log(
                    transaction_type="withdrawal_unfreeze",
                    user_id=order["user_id"],
                    amount=order["amount_shrimp"],
                    balance_before=balance_before,
                    balance_after=balance_before,
                    related_order_id=order["_id"],
                    related_order_type="withdrawal_order",
                    description=f"Withdrawal cancelled, unfreeze {order['amount_shrimp']} kg",
                    session=session
                )

        return await db.withdrawal_orders.find_one({"order_no": order_no})

    @staticmethod
    async def review_withdrawal_order(
        order_no: str,
        approved: bool,
        rejection_reason: Optional[str] = None,
        reviewer_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Review withdrawal order (admin only)
        """
        db = get_database()

        # Find order
        order = await db.withdrawal_orders.find_one({"order_no": order_no})
        if not order:
            raise ValueError(f"Withdrawal order not found: {order_no}")

        # Check status
        if order["status"] not in [WithdrawalStatus.PENDING.value, WithdrawalStatus.REVIEWING.value]:
            raise ValueError(f"Cannot review order with status: {order['status']}")

        new_status = WithdrawalStatus.APPROVED.value if approved else WithdrawalStatus.REJECTED.value

        # Use transaction
        async with await db.client.start_session() as session:
            async with session.start_transaction():
                # Update order
                update_data = {
                    "status": new_status,
                    "reviewed_at": datetime.utcnow(),
                    "reviewed_by": reviewer_id
                }
                if not approved and rejection_reason:
                    update_data["rejection_reason"] = rejection_reason

                await db.withdrawal_orders.update_one(
                    {"_id": order["_id"]},
                    {"$set": update_data},
                    session=session
                )

                # If rejected, unfreeze shrimp
                if not approved:
                    user = await db.users.find_one({"_id": order["user_id"]}, session=session)
                    balance_before = user.get("shrimp_food_balance", 0)

                    await db.users.update_one(
                        {"_id": order["user_id"]},
                        {"$inc": {"shrimp_food_frozen": -order["amount_shrimp"]}},
                        session=session
                    )

                    # Record transaction log
                    await PaymentService._record_transaction_log(
                        transaction_type="withdrawal_rejected",
                        user_id=order["user_id"],
                        amount=order["amount_shrimp"],
                        balance_before=balance_before,
                        balance_after=balance_before,
                        related_order_id=order["_id"],
                        related_order_type="withdrawal_order",
                        description=f"Withdrawal rejected, unfreeze {order['amount_shrimp']} kg",
                        session=session
                    )

        return await db.withdrawal_orders.find_one({"order_no": order_no})

    @staticmethod
    async def complete_withdrawal_order(
        order_no: str,
        transfer_order_no: str
    ) -> Dict[str, Any]:
        """
        Complete withdrawal order after transfer (admin only)
        """
        db = get_database()

        # Find order
        order = await db.withdrawal_orders.find_one({"order_no": order_no})
        if not order:
            raise ValueError(f"Withdrawal order not found: {order_no}")

        # Check status
        if order["status"] != WithdrawalStatus.APPROVED.value:
            raise ValueError(f"Order must be APPROVED status, current: {order['status']}")

        # Use transaction
        async with await db.client.start_session() as session:
            async with session.start_transaction():
                # Update order
                await db.withdrawal_orders.update_one(
                    {"_id": order["_id"]},
                    {
                        "$set": {
                            "status": WithdrawalStatus.COMPLETED.value,
                            "completed_at": datetime.utcnow(),
                            "transfer_order_no": transfer_order_no
                        }
                    },
                    session=session
                )

                # Get user balance
                user = await db.users.find_one({"_id": order["user_id"]}, session=session)
                balance_before = user.get("shrimp_food_balance", 0)

                # Deduct shrimp from user (both balance and frozen)
                await db.users.update_one(
                    {"_id": order["user_id"]},
                    {
                        "$inc": {
                            "shrimp_food_balance": -order["amount_shrimp"],
                            "shrimp_food_frozen": -order["amount_shrimp"]
                        }
                    },
                    session=session
                )

                # Record transaction log
                await PaymentService._record_transaction_log(
                    transaction_type="withdrawal",
                    user_id=order["user_id"],
                    amount=order["amount_shrimp"],
                    balance_before=balance_before,
                    balance_after=balance_before - order["amount_shrimp"],
                    related_order_id=order["_id"],
                    related_order_type="withdrawal_order",
                    description=f"Withdrawal completed, {order['amount_rmb']} RMB",
                    session=session
                )

        return await db.withdrawal_orders.find_one({"order_no": order_no})

    @staticmethod
    async def add_platform_fee(
        amount: float,
        contract_id: str,
        session=None
    ) -> None:
        """
        Add platform fee to platform account
        """
        db = get_database()

        # Get or create platform account
        platform_account = await db.platform_accounts.find_one(
            {"account_type": "fee_income"},
            session=session
        )

        if not platform_account:
            # Create platform account
            platform_account = {
                "account_type": "fee_income",
                "balance": 0.0,
                "frozen_balance": 0.0,
                "total_income": 0.0,
                "total_withdrawal": 0.0,
                "last_updated": datetime.utcnow(),
                "created_at": datetime.utcnow()
            }
            result = await db.platform_accounts.insert_one(platform_account, session=session)
            platform_account["_id"] = result.inserted_id

        balance_before = platform_account["balance"]

        # Update platform account
        await db.platform_accounts.update_one(
            {"_id": platform_account["_id"]},
            {
                "$inc": {
                    "balance": amount,
                    "total_income": amount
                },
                "$set": {"last_updated": datetime.utcnow()}
            },
            session=session
        )

        # Record transaction log
        await PaymentService._record_transaction_log(
            transaction_type="fee",
            user_id=None,  # Platform income, no user
            amount=amount,
            balance_before=balance_before,
            balance_after=balance_before + amount,
            related_order_id=ObjectId(contract_id),
            related_order_type="contract",
            description=f"Platform fee from contract {contract_id}",
            session=session
        )

    @staticmethod
    async def get_platform_account() -> Dict[str, Any]:
        """
        Get platform account statistics
        """
        db = get_database()

        # Get platform account
        platform_account = await db.platform_accounts.find_one({"account_type": "fee_income"})
        if not platform_account:
            return {
                "total_fee_income": 0.0,
                "current_balance": 0.0,
                "total_recharge_amount": 0.0,
                "total_withdrawal_amount": 0.0,
                "pending_withdrawal_count": 0
            }

        # Get total recharge amount
        recharge_pipeline = [
            {"$match": {"payment_status": RechargeStatus.SUCCESS.value}},
            {"$group": {"_id": None, "total": {"$sum": "$amount_shrimp"}}}
        ]
        recharge_result = await db.recharge_orders.aggregate(recharge_pipeline).to_list(1)
        total_recharge = recharge_result[0]["total"] if recharge_result else 0.0

        # Get total withdrawal amount
        withdrawal_pipeline = [
            {"$match": {"status": WithdrawalStatus.COMPLETED.value}},
            {"$group": {"_id": None, "total": {"$sum": "$amount_shrimp"}}}
        ]
        withdrawal_result = await db.withdrawal_orders.aggregate(withdrawal_pipeline).to_list(1)
        total_withdrawal = withdrawal_result[0]["total"] if withdrawal_result else 0.0

        # Get pending withdrawal count
        pending_count = await db.withdrawal_orders.count_documents({
            "status": {"$in": [WithdrawalStatus.PENDING.value, WithdrawalStatus.REVIEWING.value]}
        })

        return {
            "total_fee_income": platform_account.get("total_income", 0.0),
            "current_balance": platform_account.get("balance", 0.0),
            "total_recharge_amount": total_recharge,
            "total_withdrawal_amount": total_withdrawal,
            "pending_withdrawal_count": pending_count
        }

    @staticmethod
    async def _record_transaction_log(
        transaction_type: str,
        user_id: Optional[ObjectId],
        amount: float,
        balance_before: float,
        balance_after: float,
        related_order_id: ObjectId,
        related_order_type: str,
        description: str,
        session=None
    ) -> None:
        """
        Internal method to record transaction log
        """
        db = get_database()

        log_doc = {
            "transaction_type": transaction_type,
            "user_id": user_id,
            "amount": amount,
            "balance_before": balance_before,
            "balance_after": balance_after,
            "related_order_id": related_order_id,
            "related_order_type": related_order_type,
            "description": description,
            "created_at": datetime.utcnow()
        }

        await db.transaction_logs.insert_one(log_doc, session=session)

    @staticmethod
    async def create_platform_withdrawal_order(
        admin_id: str,
        amount_shrimp: float,
        withdrawal_method: WithdrawalMethod,
        withdrawal_account: WithdrawalAccount,
        remarks: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create platform withdrawal order (admin only)
        """
        db = get_database()

        # Validate amount
        if amount_shrimp < settings.MIN_PLATFORM_WITHDRAWAL_AMOUNT:
            raise ValueError(
                f"Minimum platform withdrawal amount is {settings.MIN_PLATFORM_WITHDRAWAL_AMOUNT} kg"
            )

        # Get platform account
        platform_account = await db.platform_accounts.find_one({"account_type": "fee_income"})
        if not platform_account:
            raise ValueError("Platform account not found")

        # Check available balance (balance - frozen_balance)
        balance = platform_account.get("balance", 0)
        frozen_balance = platform_account.get("frozen_balance", 0)
        available_balance = balance - frozen_balance

        if available_balance < amount_shrimp:
            raise ValueError(
                f"Insufficient platform balance. Available: {available_balance} kg, "
                f"Balance: {balance} kg, Frozen: {frozen_balance} kg"
            )

        # Calculate RMB amount
        amount_rmb = amount_shrimp / settings.WITHDRAWAL_EXCHANGE_RATE

        # Generate order number
        order_no = PaymentService.generate_order_no("PWDR")

        # Use transaction
        async with await db.client.start_session() as session:
            async with session.start_transaction():
                # Create platform withdrawal order
                order_doc = {
                    "order_no": order_no,
                    "amount_shrimp": amount_shrimp,
                    "amount_rmb": amount_rmb,
                    "exchange_rate": settings.WITHDRAWAL_EXCHANGE_RATE,
                    "withdrawal_method": withdrawal_method.value,
                    "withdrawal_account": withdrawal_account.model_dump(),
                    "status": PlatformWithdrawalStatus.PENDING.value,
                    "created_by": ObjectId(admin_id),
                    "created_at": datetime.utcnow(),
                    "reviewed_by": None,
                    "reviewed_at": None,
                    "completed_at": None,
                    "rejection_reason": None,
                    "transfer_order_no": None,
                    "remarks": remarks
                }

                result = await db.platform_withdrawal_orders.insert_one(order_doc, session=session)
                order_doc["_id"] = result.inserted_id

                # Freeze platform balance
                balance_before = platform_account.get("balance", 0)
                await db.platform_accounts.update_one(
                    {"_id": platform_account["_id"]},
                    {
                        "$inc": {"frozen_balance": amount_shrimp},
                        "$set": {"last_updated": datetime.utcnow()}
                    },
                    session=session
                )

                # Record transaction log
                await PaymentService._record_transaction_log(
                    transaction_type="platform_withdrawal_freeze",
                    user_id=None,  # Platform operation, no user
                    amount=amount_shrimp,
                    balance_before=balance_before,
                    balance_after=balance_before,  # Balance unchanged, just frozen
                    related_order_id=order_doc["_id"],
                    related_order_type="platform_withdrawal_order",
                    description=f"Platform withdrawal freeze {amount_shrimp} kg ({amount_rmb} RMB)",
                    session=session
                )

        return order_doc

    @staticmethod
    async def review_platform_withdrawal_order(
        order_no: str,
        approved: bool,
        reviewer_id: str,
        rejection_reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Review platform withdrawal order (admin only)
        Requires different admin than creator for security (dual-approval)
        """
        db = get_database()

        # Find order
        order = await db.platform_withdrawal_orders.find_one({"order_no": order_no})
        if not order:
            raise ValueError(f"Platform withdrawal order not found: {order_no}")

        # Check status
        if order["status"] not in [PlatformWithdrawalStatus.PENDING.value,
                                    PlatformWithdrawalStatus.REVIEWING.value]:
            raise ValueError(f"Cannot review order with status: {order['status']}")

        # Prevent self-review (dual-approval security mechanism)
        if str(order["created_by"]) == reviewer_id:
            raise ValueError("Cannot review your own withdrawal request. Dual approval required.")

        new_status = PlatformWithdrawalStatus.APPROVED.value if approved else PlatformWithdrawalStatus.REJECTED.value

        # Use transaction
        async with await db.client.start_session() as session:
            async with session.start_transaction():
                # Update order
                update_data = {
                    "status": new_status,
                    "reviewed_at": datetime.utcnow(),
                    "reviewed_by": ObjectId(reviewer_id)
                }
                if not approved and rejection_reason:
                    update_data["rejection_reason"] = rejection_reason

                await db.platform_withdrawal_orders.update_one(
                    {"_id": order["_id"]},
                    {"$set": update_data},
                    session=session
                )

                # If rejected, unfreeze platform balance
                if not approved:
                    platform_account = await db.platform_accounts.find_one(
                        {"account_type": "fee_income"},
                        session=session
                    )
                    balance_before = platform_account.get("balance", 0)

                    await db.platform_accounts.update_one(
                        {"account_type": "fee_income"},
                        {
                            "$inc": {"frozen_balance": -order["amount_shrimp"]},
                            "$set": {"last_updated": datetime.utcnow()}
                        },
                        session=session
                    )

                    # Record transaction log
                    await PaymentService._record_transaction_log(
                        transaction_type="platform_withdrawal_rejected",
                        user_id=None,
                        amount=order["amount_shrimp"],
                        balance_before=balance_before,
                        balance_after=balance_before,
                        related_order_id=order["_id"],
                        related_order_type="platform_withdrawal_order",
                        description=f"Platform withdrawal rejected, unfreeze {order['amount_shrimp']} kg",
                        session=session
                    )

        return await db.platform_withdrawal_orders.find_one({"order_no": order_no})

    @staticmethod
    async def complete_platform_withdrawal_order(
        order_no: str,
        transfer_order_no: str,
        admin_id: str
    ) -> Dict[str, Any]:
        """
        Complete platform withdrawal order after bank transfer (admin only)
        """
        db = get_database()

        # Find order
        order = await db.platform_withdrawal_orders.find_one({"order_no": order_no})
        if not order:
            raise ValueError(f"Platform withdrawal order not found: {order_no}")

        # Check status
        if order["status"] != PlatformWithdrawalStatus.APPROVED.value:
            raise ValueError(f"Order must be APPROVED status, current: {order['status']}")

        # Use transaction
        async with await db.client.start_session() as session:
            async with session.start_transaction():
                # Update order
                await db.platform_withdrawal_orders.update_one(
                    {"_id": order["_id"]},
                    {
                        "$set": {
                            "status": PlatformWithdrawalStatus.COMPLETED.value,
                            "completed_at": datetime.utcnow(),
                            "transfer_order_no": transfer_order_no
                        }
                    },
                    session=session
                )

                # Get platform account balance
                platform_account = await db.platform_accounts.find_one(
                    {"account_type": "fee_income"},
                    session=session
                )
                balance_before = platform_account.get("balance", 0)

                # Deduct from platform balance (both balance and frozen)
                await db.platform_accounts.update_one(
                    {"_id": platform_account["_id"]},
                    {
                        "$inc": {
                            "balance": -order["amount_shrimp"],
                            "frozen_balance": -order["amount_shrimp"],
                            "total_withdrawal": order["amount_shrimp"]
                        },
                        "$set": {"last_updated": datetime.utcnow()}
                    },
                    session=session
                )

                # Record transaction log
                await PaymentService._record_transaction_log(
                    transaction_type="platform_withdrawal",
                    user_id=None,
                    amount=order["amount_shrimp"],
                    balance_before=balance_before,
                    balance_after=balance_before - order["amount_shrimp"],
                    related_order_id=order["_id"],
                    related_order_type="platform_withdrawal_order",
                    description=f"Platform withdrawal completed, {order['amount_rmb']} RMB (Transfer: {transfer_order_no})",
                    session=session
                )

        return await db.platform_withdrawal_orders.find_one({"order_no": order_no})


# Create singleton instance
payment_service = PaymentService()
