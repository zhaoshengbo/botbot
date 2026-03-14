"""Contract Service"""
from datetime import datetime, timedelta
from typing import List, Optional
from bson import ObjectId
from app.db.mongodb import get_database
from app.schemas.contract import ContractStatus
from app.schemas.task import TaskStatus
from app.services.bid_service import bid_service


class ContractService:
    """Contract management service"""

    @staticmethod
    async def create_contract(bid_id: str, publisher_id: str) -> dict:
        """
        Create contract by accepting a bid

        Args:
            bid_id: Bid ID to accept
            publisher_id: Publisher user ID

        Returns:
            Created contract document
        """
        db = get_database()

        # Accept the bid (this validates everything)
        bid = await bid_service.accept_bid(bid_id, publisher_id)

        # Get task
        task = await db.tasks.find_one({"_id": bid["task_id"]})

        # Calculate deadline
        deadline_at = datetime.utcnow() + timedelta(hours=task["completion_deadline_hours"])

        # Update task with deadline and status
        await db.tasks.update_one(
            {"_id": task["_id"]},
            {
                "$set": {
                    "status": TaskStatus.IN_PROGRESS.value,
                    "deadline_at": deadline_at
                }
            }
        )

        # Create contract
        contract_doc = {
            "task_id": bid["task_id"],
            "publisher_id": task["publisher_id"],
            "claimer_id": bid["bidder_id"],
            "amount": bid["amount"],
            "status": ContractStatus.ACTIVE.value,
            "deliverables_submitted": False,
            "deliverables_url": None,
            "deliverables_submitted_at": None,
            "completed_at": None,
            "created_at": datetime.utcnow()
        }

        result = await db.contracts.insert_one(contract_doc)

        # Update user stats
        await db.users.update_one(
            {"_id": bid["bidder_id"]},
            {"$inc": {"tasks_claimed": 1}}
        )

        contract_doc["_id"] = result.inserted_id
        return contract_doc

    @staticmethod
    async def get_contract(contract_id: str) -> Optional[dict]:
        """Get contract by ID"""
        db = get_database()

        try:
            contract = await db.contracts.find_one({"_id": ObjectId(contract_id)})
        except:
            return None

        if contract:
            # Enrich with task and user info
            task = await db.tasks.find_one({"_id": contract["task_id"]})
            publisher = await db.users.find_one({"_id": contract["publisher_id"]})
            claimer = await db.users.find_one({"_id": contract["claimer_id"]})

            contract["task_title"] = task.get("title") if task else None
            contract["publisher_username"] = publisher.get("username") if publisher else None
            contract["claimer_username"] = claimer.get("username") if claimer else None

        return contract

    @staticmethod
    async def list_contracts(
        user_id: str,
        role: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[dict]:
        """
        List contracts for a user

        Args:
            user_id: User ID
            role: Filter by role ('publisher' or 'claimer')
            status: Filter by status

        Returns:
            List of contracts
        """
        db = get_database()

        query = {}
        if role == "publisher":
            query["publisher_id"] = ObjectId(user_id)
        elif role == "claimer":
            query["claimer_id"] = ObjectId(user_id)
        else:
            # Both roles
            query["$or"] = [
                {"publisher_id": ObjectId(user_id)},
                {"claimer_id": ObjectId(user_id)}
            ]

        if status:
            query["status"] = status

        contracts = await db.contracts.find(query).sort("created_at", -1).to_list(length=100)

        # Enrich with task and user info
        for contract in contracts:
            task = await db.tasks.find_one({"_id": contract["task_id"]})
            publisher = await db.users.find_one({"_id": contract["publisher_id"]})
            claimer = await db.users.find_one({"_id": contract["claimer_id"]})

            contract["task_title"] = task.get("title") if task else None
            contract["publisher_username"] = publisher.get("username") if publisher else None
            contract["claimer_username"] = claimer.get("username") if claimer else None

        return contracts

    @staticmethod
    async def submit_deliverables(contract_id: str, deliverables_url: str, user_id: str, notes: Optional[str] = None) -> dict:
        """Submit deliverables for a contract"""
        db = get_database()

        # Get contract
        try:
            contract = await db.contracts.find_one({"_id": ObjectId(contract_id)})
        except:
            raise ValueError("Invalid contract ID")

        if not contract:
            raise ValueError("Contract not found")

        # Check if claimer
        if str(contract["claimer_id"]) != user_id:
            raise ValueError("Only the claimer can submit deliverables")

        # Check status
        if contract["status"] != ContractStatus.ACTIVE.value:
            raise ValueError("Contract is not active")

        # Update contract
        await db.contracts.update_one(
            {"_id": ObjectId(contract_id)},
            {
                "$set": {
                    "deliverables_submitted": True,
                    "deliverables_url": deliverables_url,
                    "deliverables_submitted_at": datetime.utcnow()
                }
            }
        )

        # Return updated contract
        updated_contract = await db.contracts.find_one({"_id": ObjectId(contract_id)})
        return updated_contract

    @staticmethod
    async def complete_contract(contract_id: str, approved: bool, user_id: str, rejection_reason: Optional[str] = None) -> dict:
        """
        Complete a contract (publisher approves deliverables)

        Args:
            contract_id: Contract ID
            approved: Whether deliverables are approved
            user_id: Publisher user ID
            rejection_reason: Reason if rejected

        Returns:
            Updated contract
        """
        db = get_database()

        # Get contract
        try:
            contract = await db.contracts.find_one({"_id": ObjectId(contract_id)})
        except:
            raise ValueError("Invalid contract ID")

        if not contract:
            raise ValueError("Contract not found")

        # Check if publisher
        if str(contract["publisher_id"]) != user_id:
            raise ValueError("Only the publisher can complete the contract")

        # Check if deliverables submitted
        if not contract.get("deliverables_submitted"):
            raise ValueError("Deliverables not yet submitted")

        # Check status
        if contract["status"] != ContractStatus.ACTIVE.value:
            raise ValueError("Contract is not active")

        if approved:
            # Transfer shrimp food
            await db.users.update_one(
                {"_id": contract["publisher_id"]},
                {
                    "$inc": {
                        "shrimp_food_balance": -contract["amount"],
                        "shrimp_food_frozen": -contract["amount"],
                        "tasks_completed_as_publisher": 1
                    }
                }
            )

            await db.users.update_one(
                {"_id": contract["claimer_id"]},
                {
                    "$inc": {
                        "shrimp_food_balance": contract["amount"],
                        "tasks_completed_as_claimer": 1
                    }
                }
            )

            # Update contract status
            await db.contracts.update_one(
                {"_id": ObjectId(contract_id)},
                {
                    "$set": {
                        "status": ContractStatus.COMPLETED.value,
                        "completed_at": datetime.utcnow()
                    }
                }
            )

            # Update task status
            await db.tasks.update_one(
                {"_id": contract["task_id"]},
                {"$set": {"status": TaskStatus.COMPLETED.value}}
            )
        else:
            # Disputed - need manual resolution
            await db.contracts.update_one(
                {"_id": ObjectId(contract_id)},
                {
                    "$set": {
                        "status": ContractStatus.DISPUTED.value,
                        "rejection_reason": rejection_reason
                    }
                }
            )

        # Return updated contract
        updated_contract = await db.contracts.find_one({"_id": ObjectId(contract_id)})
        return updated_contract


contract_service = ContractService()
