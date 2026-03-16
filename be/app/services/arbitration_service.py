"""Arbitration Service - Handle dispute resolution"""
from app.db.mongodb import get_database
from app.schemas.arbitration import (
    ArbitrationRequest,
    ArbitrationDecision,
    ArbitrationStatus
)
from app.schemas.contract import ContractStatus
from bson import ObjectId
from datetime import datetime
from typing import Optional


class ArbitrationService:
    """Arbitration service for dispute resolution"""

    @staticmethod
    async def create_arbitration(
        request: ArbitrationRequest,
        requester_id: str
    ) -> dict:
        """
        Create arbitration request

        Args:
            request: Arbitration request data
            requester_id: ID of user requesting arbitration

        Returns:
            Created arbitration document
        """
        db = get_database()

        # 1. Verify contract exists and is DISPUTED
        contract = await db.contracts.find_one({"_id": ObjectId(request.contract_id)})
        if not contract:
            raise ValueError("Contract not found")

        if contract["status"] != ContractStatus.DISPUTED.value:
            raise ValueError("Contract must be in DISPUTED status to request arbitration")

        # 2. Verify requester identity
        if request.requester_role == "publisher":
            if str(contract["publisher_id"]) != requester_id:
                raise ValueError("Not authorized as publisher")
        elif request.requester_role == "claimer":
            if str(contract["claimer_id"]) != requester_id:
                raise ValueError("Not authorized as claimer")
        else:
            raise ValueError("Invalid requester role")

        # 3. Check for existing arbitration
        existing = await db.arbitrations.find_one({
            "contract_id": ObjectId(request.contract_id),
            "status": {"$in": [
                ArbitrationStatus.PENDING.value,
                ArbitrationStatus.UNDER_REVIEW.value
            ]}
        })
        if existing:
            raise ValueError("An arbitration request already exists for this contract")

        # 4. Create arbitration record
        arbitration = {
            "contract_id": ObjectId(request.contract_id),
            "task_id": contract["task_id"],
            "publisher_id": contract["publisher_id"],
            "claimer_id": contract["claimer_id"],
            "requester_id": ObjectId(requester_id),
            "requester_role": request.requester_role,
            "status": ArbitrationStatus.PENDING.value,
            "reason": request.reason,
            "evidence_urls": request.evidence_urls or [],
            "admin_notes": None,
            "decision": None,
            "publisher_refund_percentage": 0,
            "claimer_payment_percentage": 0,
            "resolution_notes": None,
            "created_at": datetime.utcnow(),
            "assigned_admin_id": None,
            "reviewed_at": None,
            "resolved_at": None
        }

        result = await db.arbitrations.insert_one(arbitration)
        arbitration["_id"] = result.inserted_id

        return arbitration

    @staticmethod
    async def get_pending_arbitrations(
        skip: int = 0,
        limit: int = 20
    ) -> tuple[list[dict], int]:
        """
        Get pending arbitrations for admin review

        Args:
            skip: Number of records to skip
            limit: Maximum records to return

        Returns:
            Tuple of (arbitrations list, total count)
        """
        db = get_database()

        query = {"status": ArbitrationStatus.PENDING.value}

        cursor = db.arbitrations.find(query).sort("created_at", 1).skip(skip).limit(limit)
        arbitrations = await cursor.to_list(length=limit)

        total = await db.arbitrations.count_documents(query)

        # Enrich with user and task info
        for arb in arbitrations:
            # Get task title
            task = await db.tasks.find_one({"_id": arb["task_id"]}, {"title": 1})
            arb["task_title"] = task.get("title") if task else None

            # Get publisher username
            publisher = await db.users.find_one({"_id": arb["publisher_id"]}, {"username": 1})
            arb["publisher_username"] = publisher.get("username") if publisher else None

            # Get claimer username
            claimer = await db.users.find_one({"_id": arb["claimer_id"]}, {"username": 1})
            arb["claimer_username"] = claimer.get("username") if claimer else None

        return arbitrations, total

    @staticmethod
    async def assign_arbitration(
        arbitration_id: str,
        admin_id: str
    ) -> dict:
        """
        Admin claims arbitration case

        Args:
            arbitration_id: Arbitration ID
            admin_id: Admin user ID

        Returns:
            Updated arbitration document
        """
        db = get_database()

        arbitration = await db.arbitrations.find_one({"_id": ObjectId(arbitration_id)})
        if not arbitration:
            raise ValueError("Arbitration not found")

        if arbitration["status"] != ArbitrationStatus.PENDING.value:
            raise ValueError("Arbitration is not in pending status")

        # Update status and assign admin
        await db.arbitrations.update_one(
            {"_id": ObjectId(arbitration_id)},
            {"$set": {
                "status": ArbitrationStatus.UNDER_REVIEW.value,
                "assigned_admin_id": ObjectId(admin_id),
                "reviewed_at": datetime.utcnow()
            }}
        )

        return await db.arbitrations.find_one({"_id": ObjectId(arbitration_id)})

    @staticmethod
    async def resolve_arbitration(
        decision: ArbitrationDecision,
        admin_id: str
    ) -> dict:
        """
        Admin makes arbitration decision and executes payment

        Args:
            decision: Arbitration decision with payment split
            admin_id: Admin user ID

        Returns:
            Updated arbitration document
        """
        db = get_database()

        # 1. Get arbitration record
        arbitration = await db.arbitrations.find_one({"_id": ObjectId(decision.arbitration_id)})
        if not arbitration:
            raise ValueError("Arbitration not found")

        if arbitration["status"] != ArbitrationStatus.UNDER_REVIEW.value:
            raise ValueError("Arbitration is not under review")

        if str(arbitration.get("assigned_admin_id")) != admin_id:
            raise ValueError("Not authorized to resolve this arbitration")

        # 2. Verify percentages sum to 100%
        total_percentage = decision.publisher_refund_percentage + decision.claimer_payment_percentage
        if abs(total_percentage - 100) > 0.01:
            raise ValueError("Publisher refund and claimer payment must sum to 100%")

        # 3. Get contract information
        contract = await db.contracts.find_one({"_id": arbitration["contract_id"]})
        if not contract:
            raise ValueError("Contract not found")

        # 4. Calculate payment amounts
        from app.core.config import settings
        contract_amount = contract["amount"]
        platform_fee = contract_amount * settings.PLATFORM_FEE_RATE  # 10%
        distributable_amount = contract_amount - platform_fee

        claimer_payment = distributable_amount * (decision.claimer_payment_percentage / 100)
        publisher_refund = distributable_amount * (decision.publisher_refund_percentage / 100)

        # 5. Execute payment using transaction
        async with await db.client.start_session() as session:
            async with session.start_transaction():
                try:
                    # Get user info
                    publisher = await db.users.find_one(
                        {"_id": contract["publisher_id"]},
                        session=session
                    )
                    claimer = await db.users.find_one(
                        {"_id": contract["claimer_id"]},
                        session=session
                    )

                    # Publisher: deduct full amount, receive partial refund
                    await db.users.update_one(
                        {"_id": contract["publisher_id"]},
                        {"$inc": {
                            "shrimp_food_balance": -contract_amount + publisher_refund,
                            "shrimp_food_frozen": -contract_amount
                        }},
                        session=session
                    )

                    # Claimer: receive partial payment
                    await db.users.update_one(
                        {"_id": contract["claimer_id"]},
                        {"$inc": {"shrimp_food_balance": claimer_payment}},
                        session=session
                    )

                    # Platform: collect fee
                    platform_account = await db.platform_accounts.find_one(
                        {"account_type": "main"},
                        session=session
                    )
                    if platform_account:
                        await db.platform_accounts.update_one(
                            {"_id": platform_account["_id"]},
                            {"$inc": {"balance": platform_fee}},
                            session=session
                        )

                    # Update contract status
                    await db.contracts.update_one(
                        {"_id": arbitration["contract_id"]},
                        {"$set": {
                            "status": ContractStatus.COMPLETED.value,
                            "completed_at": datetime.utcnow(),
                            "arbitration_resolved": True
                        }},
                        session=session
                    )

                    # Update task status
                    await db.tasks.update_one(
                        {"_id": arbitration["task_id"]},
                        {"$set": {"status": "completed"}},
                        session=session
                    )

                    # Update arbitration status
                    await db.arbitrations.update_one(
                        {"_id": ObjectId(decision.arbitration_id)},
                        {"$set": {
                            "status": ArbitrationStatus.RESOLVED.value,
                            "decision": decision.decision.value,
                            "publisher_refund_percentage": decision.publisher_refund_percentage,
                            "claimer_payment_percentage": decision.claimer_payment_percentage,
                            "resolution_notes": decision.resolution_notes,
                            "resolved_at": datetime.utcnow()
                        }},
                        session=session
                    )

                    # Record transaction logs
                    await db.transaction_logs.insert_many([
                        {
                            "transaction_type": "arbitration_payment",
                            "user_id": contract["claimer_id"],
                            "amount": claimer_payment,
                            "balance_before": claimer["shrimp_food_balance"],
                            "balance_after": claimer["shrimp_food_balance"] + claimer_payment,
                            "related_order_id": arbitration["contract_id"],
                            "related_order_type": "contract",
                            "description": f"Arbitration payment ({decision.claimer_payment_percentage}%)",
                            "created_at": datetime.utcnow()
                        },
                        {
                            "transaction_type": "arbitration_refund",
                            "user_id": contract["publisher_id"],
                            "amount": publisher_refund,
                            "balance_before": publisher["shrimp_food_balance"],
                            "balance_after": publisher["shrimp_food_balance"] - contract_amount + publisher_refund,
                            "related_order_id": arbitration["contract_id"],
                            "related_order_type": "contract",
                            "description": f"Arbitration refund ({decision.publisher_refund_percentage}%)",
                            "created_at": datetime.utcnow()
                        }
                    ], session=session)

                    await session.commit_transaction()

                except Exception as e:
                    await session.abort_transaction()
                    raise ValueError(f"Failed to execute arbitration payment: {str(e)}")

        return await db.arbitrations.find_one({"_id": ObjectId(decision.arbitration_id)})

    @staticmethod
    async def get_user_arbitrations(
        user_id: str,
        skip: int = 0,
        limit: int = 20
    ) -> tuple[list[dict], int]:
        """
        Get arbitrations for a specific user

        Args:
            user_id: User ID
            skip: Number of records to skip
            limit: Maximum records to return

        Returns:
            Tuple of (arbitrations list, total count)
        """
        db = get_database()

        query = {
            "$or": [
                {"publisher_id": ObjectId(user_id)},
                {"claimer_id": ObjectId(user_id)}
            ]
        }

        cursor = db.arbitrations.find(query).sort("created_at", -1).skip(skip).limit(limit)
        arbitrations = await cursor.to_list(length=limit)

        total = await db.arbitrations.count_documents(query)

        # Enrich with task info
        for arb in arbitrations:
            task = await db.tasks.find_one({"_id": arb["task_id"]}, {"title": 1})
            arb["task_title"] = task.get("title") if task else None

        return arbitrations, total


arbitration_service = ArbitrationService()
