"""Task Service"""
from datetime import datetime, timedelta
from typing import Optional, List, Dict
from bson import ObjectId
from app.db.mongodb import get_database
from app.schemas.task import TaskCreate, TaskUpdate, TaskStatus
from app.schemas.bid import BidStatus


class TaskService:
    """Task management service"""

    @staticmethod
    async def create_task(task_data: TaskCreate, publisher_id: str) -> dict:
        """
        Create a new task

        Args:
            task_data: Task creation data
            publisher_id: Publisher user ID

        Returns:
            Created task document
        """
        db = get_database()

        # Check if user has enough balance
        user = await db.users.find_one({"_id": ObjectId(publisher_id)})
        if not user:
            raise ValueError("User not found")

        available_balance = user.get("shrimp_food_balance", 0) - user.get("shrimp_food_frozen", 0)
        if available_balance < task_data.budget:
            raise ValueError("Insufficient shrimp food balance")

        # Create task
        now = datetime.utcnow()
        bidding_ends_at = now + timedelta(hours=task_data.bidding_period_hours)

        task_doc = {
            "publisher_id": ObjectId(publisher_id),
            "title": task_data.title,
            "description": task_data.description,
            "deliverables": task_data.deliverables,
            "budget": task_data.budget,
            "deadline": task_data.deadline,
            "category": task_data.category,
            "tags": task_data.tags or [],
            "bidding_period_hours": task_data.bidding_period_hours,
            "completion_deadline_hours": task_data.completion_deadline_hours,
            "status": TaskStatus.BIDDING.value,
            "created_at": now,
            "bidding_ends_at": bidding_ends_at,
            "deadline_at": task_data.deadline or (now + timedelta(hours=task_data.completion_deadline_hours)),
            "view_count": 0,
            "bid_count": 0,
        }

        result = await db.tasks.insert_one(task_doc)

        # Freeze budget amount
        await db.users.update_one(
            {"_id": ObjectId(publisher_id)},
            {
                "$inc": {
                    "shrimp_food_frozen": task_data.budget,
                    "tasks_published": 1
                }
            }
        )

        task_doc["_id"] = result.inserted_id
        return task_doc

    @staticmethod
    async def get_task(task_id: str, increment_view: bool = False) -> Optional[dict]:
        """Get task by ID"""
        db = get_database()

        try:
            task = await db.tasks.find_one({"_id": ObjectId(task_id)})
        except:
            return None

        if task and increment_view:
            await db.tasks.update_one(
                {"_id": ObjectId(task_id)},
                {"$inc": {"view_count": 1}}
            )
            task["view_count"] = task.get("view_count", 0) + 1

        return task

    @staticmethod
    async def list_tasks(
        status: Optional[str] = None,
        publisher_id: Optional[str] = None,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[List[dict], int]:
        """
        List tasks with filters

        Args:
            status: Filter by status
            publisher_id: Filter by publisher
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            Tuple of (tasks list, total count)
        """
        db = get_database()

        # Build filter
        filter_query = {}
        if status:
            filter_query["status"] = status
        if publisher_id:
            filter_query["publisher_id"] = ObjectId(publisher_id)

        # Get total count
        total = await db.tasks.count_documents(filter_query)

        # Get tasks
        cursor = db.tasks.find(filter_query).sort("created_at", -1).skip(skip).limit(limit)
        tasks = await cursor.to_list(length=limit)

        # Enrich with publisher info and bidders
        for task in tasks:
            # Get publisher username
            publisher = await db.users.find_one(
                {"_id": task["publisher_id"]},
                {"username": 1}
            )
            task["publisher_username"] = publisher.get("username") if publisher else None

            # Get bidders info for bidding tasks
            if task.get("status") == "bidding":
                bids = await db.bids.find(
                    {"task_id": task["_id"], "status": BidStatus.ACTIVE.value}
                ).to_list(length=100)

                bidders = []
                for bid in bids:
                    bidder = await db.users.find_one(
                        {"_id": bid["bidder_id"]},
                        {"username": 1, "level": 1}
                    )
                    if bidder:
                        bidders.append({
                            "user_id": str(bid["bidder_id"]),
                            "username": bidder.get("username", "Unknown"),
                            "level": bidder.get("level", "Bronze"),
                            "bid_amount": bid.get("amount", 0)
                        })

                task["bidders"] = bidders
            else:
                task["bidders"] = []

        return tasks, total

    @staticmethod
    async def update_task(task_id: str, update_data: TaskUpdate, user_id: str) -> dict:
        """Update task (only by publisher)"""
        db = get_database()

        # Get task
        task = await db.tasks.find_one({"_id": ObjectId(task_id)})
        if not task:
            raise ValueError("Task not found")

        # Check ownership
        if str(task["publisher_id"]) != user_id:
            raise ValueError("Not authorized to update this task")

        # Can only update if status is BIDDING or OPEN
        if task["status"] not in [TaskStatus.BIDDING.value, TaskStatus.OPEN.value]:
            raise ValueError("Cannot update task in current status")

        # Build update dict
        update_dict = update_data.model_dump(exclude_unset=True)
        if not update_dict:
            raise ValueError("No fields to update")

        # If budget changed, check balance
        if "budget" in update_dict:
            old_budget = task["budget"]
            new_budget = update_dict["budget"]
            budget_diff = new_budget - old_budget

            if budget_diff > 0:
                # Need more funds
                user = await db.users.find_one({"_id": ObjectId(user_id)})
                available = user.get("shrimp_food_balance", 0) - user.get("shrimp_food_frozen", 0)
                if available < budget_diff:
                    raise ValueError("Insufficient balance for budget increase")

                # Update frozen amount
                await db.users.update_one(
                    {"_id": ObjectId(user_id)},
                    {"$inc": {"shrimp_food_frozen": budget_diff}}
                )
            else:
                # Release funds
                await db.users.update_one(
                    {"_id": ObjectId(user_id)},
                    {"$inc": {"shrimp_food_frozen": budget_diff}}
                )

        # Update task
        result = await db.tasks.update_one(
            {"_id": ObjectId(task_id)},
            {"$set": update_dict}
        )

        # Return updated task
        updated_task = await db.tasks.find_one({"_id": ObjectId(task_id)})
        return updated_task

    @staticmethod
    async def cancel_task(task_id: str, user_id: str, cancellation_reason: Optional[str] = None) -> dict:
        """
        Cancel task with penalty calculation

        Scenario 1: No bids - free cancellation
        Scenario 2: Has bids - 3% penalty per bidder
        Scenario 3: Contracted/In progress - not allowed, use arbitration
        """
        db = get_database()

        # 1. Get task and validate
        task = await db.tasks.find_one({"_id": ObjectId(task_id)})
        if not task:
            raise ValueError("Task not found")

        # Check ownership
        if str(task["publisher_id"]) != user_id:
            raise ValueError("Not authorized to cancel this task")

        # 2. Check task status - Scenario 3: contracted/in progress not allowed
        if task["status"] in [
            TaskStatus.CONTRACTED.value,
            TaskStatus.IN_PROGRESS.value,
            TaskStatus.COMPLETED.value
        ]:
            raise ValueError("Cannot cancel task in current status. Please submit arbitration if there's a dispute.")

        # Already cancelled - idempotent
        if task["status"] == TaskStatus.CANCELLED.value:
            return task

        # 3. Get active bids
        active_bids = await db.bids.find({
            "task_id": ObjectId(task_id),
            "status": BidStatus.ACTIVE.value
        }).to_list(None)

        active_bid_count = len(active_bids)

        # 4. Route to appropriate scenario
        if active_bid_count == 0:
            # Scenario 1: No bids - free cancellation
            return await TaskService._cancel_task_without_penalty(
                db, task_id, user_id, task, cancellation_reason
            )
        else:
            # Scenario 2: Has bids - pay penalty
            return await TaskService._cancel_task_with_penalty(
                db, task_id, user_id, task, active_bids, cancellation_reason
            )

    @staticmethod
    async def _cancel_task_without_penalty(
        db, task_id: str, user_id: str, task: dict, reason: Optional[str]
    ) -> dict:
        """Scenario 1: No bids - free cancellation"""

        # Update task status
        await db.tasks.update_one(
            {"_id": ObjectId(task_id)},
            {"$set": {
                "status": TaskStatus.CANCELLED.value,
                "cancelled_at": datetime.utcnow(),
                "cancellation_reason": reason,
                "cancellation_penalty_paid": 0.0
            }}
        )

        # Release frozen funds
        await db.users.update_one(
            {"_id": ObjectId(user_id)},
            {"$inc": {"shrimp_food_frozen": -task["budget"]}}
        )

        return await db.tasks.find_one({"_id": ObjectId(task_id)})

    @staticmethod
    async def _cancel_task_with_penalty(
        db, task_id: str, user_id: str, task: dict,
        active_bids: list, reason: Optional[str]
    ) -> dict:
        """
        Scenario 2: Has bids - pay cancellation penalty

        Penalty: 3% of budget per bidder
        Total penalty = budget × 0.03 × active_bid_count
        """
        from app.core.config import settings

        budget = task["budget"]
        penalty_rate = settings.TASK_CANCELLATION_PENALTY_RATE
        active_bid_count = len(active_bids)

        # Calculate penalty
        penalty_per_bidder = budget * penalty_rate
        total_penalty = penalty_per_bidder * active_bid_count

        # Verify publisher has sufficient balance
        publisher = await db.users.find_one({"_id": ObjectId(user_id)})
        if publisher["shrimp_food_balance"] < total_penalty:
            raise ValueError("Insufficient balance to pay cancellation penalty")

        # Use transaction for atomicity
        async with await db.client.start_session() as session:
            async with session.start_transaction():
                try:
                    # 1. Update task status
                    await db.tasks.update_one(
                        {"_id": ObjectId(task_id)},
                        {"$set": {
                            "status": TaskStatus.CANCELLED.value,
                            "cancelled_at": datetime.utcnow(),
                            "cancellation_reason": reason,
                            "cancellation_penalty_paid": total_penalty
                        }},
                        session=session
                    )

                    # 2. Publisher pays penalty
                    await db.users.update_one(
                        {"_id": ObjectId(user_id)},
                        {"$inc": {
                            "shrimp_food_balance": -total_penalty,
                            "shrimp_food_frozen": -budget  # Unfreeze budget
                        }},
                        session=session
                    )

                    # 3. Distribute penalty to bidders
                    for bid in active_bids:
                        bidder_id = bid["bidder_id"]

                        # Bidder receives compensation
                        await db.users.update_one(
                            {"_id": bidder_id},
                            {"$inc": {"shrimp_food_balance": penalty_per_bidder}},
                            session=session
                        )

                        # Update bid status
                        await db.bids.update_one(
                            {"_id": bid["_id"]},
                            {"$set": {
                                "status": BidStatus.REJECTED_WITH_COMPENSATION.value,
                                "compensation_amount": penalty_per_bidder,
                                "compensated_at": datetime.utcnow()
                            }},
                            session=session
                        )

                        # Get bidder info for transaction log
                        bidder = await db.users.find_one({"_id": bidder_id}, session=session)

                        # Record transaction log - bidder income
                        await db.transaction_logs.insert_one({
                            "transaction_type": "cancellation_compensation",
                            "user_id": bidder_id,
                            "amount": penalty_per_bidder,
                            "balance_before": bidder["shrimp_food_balance"] - penalty_per_bidder,
                            "balance_after": bidder["shrimp_food_balance"],
                            "related_order_id": ObjectId(task_id),
                            "related_order_type": "task",
                            "description": f"Task cancellation compensation: {task.get('title', 'N/A')}",
                            "created_at": datetime.utcnow()
                        }, session=session)

                    # 4. Record transaction log - publisher expense
                    await db.transaction_logs.insert_one({
                        "transaction_type": "task_cancellation_penalty",
                        "user_id": ObjectId(user_id),
                        "amount": -total_penalty,
                        "balance_before": publisher["shrimp_food_balance"],
                        "balance_after": publisher["shrimp_food_balance"] - total_penalty,
                        "related_order_id": ObjectId(task_id),
                        "related_order_type": "task",
                        "description": f"Task cancellation penalty: {task.get('title', 'N/A')} ({active_bid_count} bidders × {penalty_per_bidder}kg)",
                        "created_at": datetime.utcnow()
                    }, session=session)

                    await session.commit_transaction()

                except Exception as e:
                    await session.abort_transaction()
                    raise ValueError(f"Failed to process cancellation penalty: {str(e)}")

        return await db.tasks.find_one({"_id": ObjectId(task_id)})

    @staticmethod
    async def get_cancellation_estimate(task_id: str, user_id: str) -> dict:
        """
        Preview cancellation penalty

        Returns:
        {
            "can_cancel": bool,
            "reason": str,
            "active_bid_count": int,
            "penalty_per_bidder": float,
            "total_penalty": float,
            "remaining_balance_after_cancel": float
        }
        """
        from app.core.config import settings
        db = get_database()

        task = await db.tasks.find_one({"_id": ObjectId(task_id)})
        if not task:
            raise ValueError("Task not found")

        # Check ownership
        if str(task["publisher_id"]) != user_id:
            raise ValueError("Not authorized")

        # Check if can cancel
        if task["status"] in [TaskStatus.CONTRACTED.value, TaskStatus.IN_PROGRESS.value]:
            return {
                "can_cancel": False,
                "reason": "Task is contracted or in progress",
                "active_bid_count": 0,
                "penalty_per_bidder": 0,
                "total_penalty": 0,
                "remaining_balance_after_cancel": 0
            }

        if task["status"] == TaskStatus.CANCELLED.value:
            return {
                "can_cancel": False,
                "reason": "Task already cancelled",
                "active_bid_count": 0,
                "penalty_per_bidder": 0,
                "total_penalty": 0,
                "remaining_balance_after_cancel": 0
            }

        # Count active bids
        active_bid_count = await db.bids.count_documents({
            "task_id": ObjectId(task_id),
            "status": BidStatus.ACTIVE.value
        })

        # Calculate penalty
        penalty_per_bidder = task["budget"] * settings.TASK_CANCELLATION_PENALTY_RATE
        total_penalty = penalty_per_bidder * active_bid_count

        # Get user balance
        user = await db.users.find_one({"_id": ObjectId(user_id)})
        remaining_balance = user["shrimp_food_balance"] - total_penalty

        return {
            "can_cancel": True,
            "reason": "Free cancellation" if active_bid_count == 0 else f"Penalty required: {total_penalty}kg",
            "active_bid_count": active_bid_count,
            "penalty_per_bidder": penalty_per_bidder,
            "total_penalty": total_penalty,
            "remaining_balance_after_cancel": remaining_balance
        }


task_service = TaskService()
