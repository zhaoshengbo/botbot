"""Bid Service"""
from datetime import datetime
from typing import List, Optional
from bson import ObjectId
from app.db.mongodb import get_database
from app.schemas.bid import BidCreate, BidStatus, AIAnalysis
from app.schemas.task import TaskStatus


class BidService:
    """Bid management service"""

    @staticmethod
    async def create_bid(
        task_id: str,
        bid_data: BidCreate,
        bidder_id: str,
        ai_analysis: Optional[AIAnalysis] = None
    ) -> dict:
        """
        Create a new bid

        Args:
            task_id: Task ID
            bid_data: Bid creation data
            bidder_id: Bidder user ID
            ai_analysis: Optional AI analysis result

        Returns:
            Created bid document
        """
        db = get_database()

        # Get task
        try:
            task = await db.tasks.find_one({"_id": ObjectId(task_id)})
        except:
            raise ValueError("Invalid task ID")

        if not task:
            raise ValueError("Task not found")

        # Check task status
        if task["status"] != TaskStatus.BIDDING.value:
            raise ValueError("Task is not accepting bids")

        # Check bidding period
        if task.get("bidding_ends_at") and datetime.utcnow() > task["bidding_ends_at"]:
            raise ValueError("Bidding period has ended")

        # Check if bidding on own task
        if str(task["publisher_id"]) == bidder_id:
            raise ValueError("Cannot bid on your own task")

        # Check if bid amount exceeds budget
        if bid_data.amount > task["budget"]:
            raise ValueError("Bid amount exceeds task budget")

        # Check if already bid
        existing_bid = await db.bids.find_one({
            "task_id": ObjectId(task_id),
            "bidder_id": ObjectId(bidder_id),
            "status": BidStatus.ACTIVE.value
        })
        if existing_bid:
            raise ValueError("You have already bid on this task")

        # Create bid
        bid_doc = {
            "task_id": ObjectId(task_id),
            "bidder_id": ObjectId(bidder_id),
            "amount": bid_data.amount,
            "message": bid_data.message,
            "ai_analysis": ai_analysis.model_dump() if ai_analysis else None,
            "status": BidStatus.ACTIVE.value,
            "created_at": datetime.utcnow()
        }

        result = await db.bids.insert_one(bid_doc)

        # Increment bid count on task
        await db.tasks.update_one(
            {"_id": ObjectId(task_id)},
            {"$inc": {"bid_count": 1}}
        )

        bid_doc["_id"] = result.inserted_id
        return bid_doc

    @staticmethod
    async def get_task_bids(task_id: str) -> List[dict]:
        """Get all bids for a task"""
        db = get_database()

        try:
            bids = await db.bids.find({"task_id": ObjectId(task_id)}).sort("created_at", -1).to_list(length=100)
        except:
            raise ValueError("Invalid task ID")

        # Enrich with bidder info
        for bid in bids:
            bidder = await db.users.find_one(
                {"_id": bid["bidder_id"]},
                {"username": 1, "level": 1, "rating_as_claimer": 1}
            )
            bid["bidder_username"] = bidder.get("username") if bidder else None
            bid["bidder_level"] = bidder.get("level") if bidder else None
            bid["bidder_rating"] = bidder.get("rating_as_claimer", {}).get("average") if bidder else None

        return bids

    @staticmethod
    async def get_user_bids(user_id: str, status: Optional[str] = None) -> List[dict]:
        """Get user's bids"""
        db = get_database()

        query = {"bidder_id": ObjectId(user_id)}
        if status:
            query["status"] = status

        bids = await db.bids.find(query).sort("created_at", -1).to_list(length=100)

        # Enrich with task info
        for bid in bids:
            task = await db.tasks.find_one(
                {"_id": bid["task_id"]},
                {"title": 1, "status": 1, "budget": 1}
            )
            bid["task_title"] = task.get("title") if task else None
            bid["task_status"] = task.get("status") if task else None

        return bids

    @staticmethod
    async def withdraw_bid(bid_id: str, user_id: str) -> dict:
        """Withdraw a bid"""
        db = get_database()

        # Get bid
        try:
            bid = await db.bids.find_one({"_id": ObjectId(bid_id)})
        except:
            raise ValueError("Invalid bid ID")

        if not bid:
            raise ValueError("Bid not found")

        # Check ownership
        if str(bid["bidder_id"]) != user_id:
            raise ValueError("Not authorized to withdraw this bid")

        # Check if can withdraw
        if bid["status"] != BidStatus.ACTIVE.value:
            raise ValueError("Can only withdraw active bids")

        # Get task
        task = await db.tasks.find_one({"_id": bid["task_id"]})
        if task["status"] != TaskStatus.BIDDING.value:
            raise ValueError("Cannot withdraw bid after bidding period")

        # Update bid status
        await db.bids.update_one(
            {"_id": ObjectId(bid_id)},
            {"$set": {"status": BidStatus.WITHDRAWN.value}}
        )

        # Decrement bid count
        await db.tasks.update_one(
            {"_id": bid["task_id"]},
            {"$inc": {"bid_count": -1}}
        )

        # Return updated bid
        updated_bid = await db.bids.find_one({"_id": ObjectId(bid_id)})
        return updated_bid

    @staticmethod
    async def accept_bid(bid_id: str, publisher_id: str) -> dict:
        """
        Accept a bid and create contract
        This will be called from contract service
        """
        db = get_database()

        # Get bid
        try:
            bid = await db.bids.find_one({"_id": ObjectId(bid_id)})
        except:
            raise ValueError("Invalid bid ID")

        if not bid:
            raise ValueError("Bid not found")

        # Check bid status
        if bid["status"] != BidStatus.ACTIVE.value:
            raise ValueError("Bid is not active")

        # Get task
        task = await db.tasks.find_one({"_id": bid["task_id"]})
        if not task:
            raise ValueError("Task not found")

        # Check ownership
        if str(task["publisher_id"]) != publisher_id:
            raise ValueError("Not authorized to accept this bid")

        # Check task status
        if task["status"] not in [TaskStatus.BIDDING.value, TaskStatus.OPEN.value]:
            raise ValueError("Task is not accepting bids")

        # Update bid status
        await db.bids.update_one(
            {"_id": ObjectId(bid_id)},
            {"$set": {"status": BidStatus.ACCEPTED.value}}
        )

        # Reject all other bids
        await db.bids.update_many(
            {
                "task_id": bid["task_id"],
                "_id": {"$ne": ObjectId(bid_id)},
                "status": BidStatus.ACTIVE.value
            },
            {"$set": {"status": BidStatus.REJECTED.value}}
        )

        # Update task status
        await db.tasks.update_one(
            {"_id": bid["task_id"]},
            {"$set": {"status": TaskStatus.CONTRACTED.value}}
        )

        return bid


bid_service = BidService()
