"""Task Service"""
from datetime import datetime, timedelta
from typing import Optional, List, Dict
from bson import ObjectId
from app.db.mongodb import get_database
from app.schemas.task import TaskCreate, TaskUpdate, TaskStatus


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
            "bidding_period_hours": task_data.bidding_period_hours,
            "completion_deadline_hours": task_data.completion_deadline_hours,
            "status": TaskStatus.BIDDING.value,
            "created_at": now,
            "bidding_ends_at": bidding_ends_at,
            "deadline_at": None,
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

        # Enrich with publisher info
        for task in tasks:
            publisher = await db.users.find_one(
                {"_id": task["publisher_id"]},
                {"username": 1}
            )
            task["publisher_username"] = publisher.get("username") if publisher else None

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
    async def cancel_task(task_id: str, user_id: str) -> dict:
        """Cancel task (only by publisher)"""
        db = get_database()

        # Get task
        task = await db.tasks.find_one({"_id": ObjectId(task_id)})
        if not task:
            raise ValueError("Task not found")

        # Check ownership
        if str(task["publisher_id"]) != user_id:
            raise ValueError("Not authorized to cancel this task")

        # Can only cancel if not yet contracted
        if task["status"] in [TaskStatus.CONTRACTED.value, TaskStatus.IN_PROGRESS.value, TaskStatus.COMPLETED.value]:
            raise ValueError("Cannot cancel task in current status")

        # Update status
        await db.tasks.update_one(
            {"_id": ObjectId(task_id)},
            {"$set": {"status": TaskStatus.CANCELLED.value}}
        )

        # Release frozen funds
        await db.users.update_one(
            {"_id": ObjectId(user_id)},
            {"$inc": {"shrimp_food_frozen": -task["budget"]}}
        )

        # Reject all active bids
        await db.bids.update_many(
            {"task_id": ObjectId(task_id), "status": "active"},
            {"$set": {"status": "rejected"}}
        )

        # Return updated task
        updated_task = await db.tasks.find_one({"_id": ObjectId(task_id)})
        return updated_task


task_service = TaskService()
