"""Rating Service"""
from datetime import datetime
from typing import List, Optional
from bson import ObjectId
from app.db.mongodb import get_database
from app.schemas.rating import RatingCreate, RatingType
from app.schemas.contract import ContractStatus


class RatingService:
    """Rating management service"""

    @staticmethod
    async def create_rating(rating_data: RatingCreate, rater_id: str) -> dict:
        """
        Create a rating for a completed contract

        Args:
            rating_data: Rating data
            rater_id: User ID of the rater

        Returns:
            Created rating document
        """
        db = get_database()

        # Get contract
        try:
            contract = await db.contracts.find_one({"_id": ObjectId(rating_data.contract_id)})
        except:
            raise ValueError("Invalid contract ID")

        if not contract:
            raise ValueError("Contract not found")

        # Check if contract is completed
        if contract["status"] != ContractStatus.COMPLETED.value:
            raise ValueError("Can only rate completed contracts")

        # Determine rating type and ratee
        if str(contract["publisher_id"]) == rater_id:
            rating_type = RatingType.PUBLISHER_TO_CLAIMER
            ratee_id = contract["claimer_id"]
        elif str(contract["claimer_id"]) == rater_id:
            rating_type = RatingType.CLAIMER_TO_PUBLISHER
            ratee_id = contract["publisher_id"]
        else:
            raise ValueError("You are not part of this contract")

        # Check if already rated
        existing_rating = await db.ratings.find_one({
            "contract_id": ObjectId(rating_data.contract_id),
            "rater_id": ObjectId(rater_id)
        })
        if existing_rating:
            raise ValueError("You have already rated this contract")

        # Get task
        task = await db.tasks.find_one({"_id": contract["task_id"]})

        # Calculate overall score if not provided
        overall_score = rating_data.score
        if overall_score is None:
            overall_score = round(
                (rating_data.quality_score + rating_data.communication_score + rating_data.timeliness_score) / 3
            )

        # Create rating
        rating_doc = {
            "contract_id": ObjectId(rating_data.contract_id),
            "task_id": contract["task_id"],
            "rater_id": ObjectId(rater_id),
            "ratee_id": ratee_id,
            "rating_type": rating_type.value,
            "score": overall_score,
            "quality_score": rating_data.quality_score,
            "communication_score": rating_data.communication_score,
            "timeliness_score": rating_data.timeliness_score,
            "comment": rating_data.comment,
            "created_at": datetime.utcnow()
        }

        result = await db.ratings.insert_one(rating_doc)

        # Update user rating statistics
        await RatingService._update_user_rating_stats(ratee_id, rating_type, overall_score)

        # Update user level based on new stats
        await RatingService._update_user_level(ratee_id)

        rating_doc["_id"] = result.inserted_id
        return rating_doc

    @staticmethod
    async def _update_user_rating_stats(user_id: ObjectId, rating_type: RatingType, score: int):
        """Update user's rating statistics"""
        db = get_database()

        user = await db.users.find_one({"_id": user_id})
        if not user:
            return

        # Determine which rating to update
        if rating_type == RatingType.PUBLISHER_TO_CLAIMER:
            rating_field = "rating_as_claimer"
        else:
            rating_field = "rating_as_publisher"

        current_rating = user.get(rating_field, {"average": 5.0, "count": 0, "total": 0.0})

        new_count = current_rating["count"] + 1
        new_total = current_rating["total"] + score
        new_average = new_total / new_count

        await db.users.update_one(
            {"_id": user_id},
            {
                "$set": {
                    f"{rating_field}.average": new_average,
                    f"{rating_field}.count": new_count,
                    f"{rating_field}.total": new_total
                }
            }
        )

    @staticmethod
    async def _update_user_level(user_id: ObjectId):
        """Update user's level based on their performance"""
        db = get_database()

        user = await db.users.find_one({"_id": user_id})
        if not user:
            return

        # Calculate level points
        tasks_completed = user.get("tasks_completed_as_claimer", 0) + user.get("tasks_completed_as_publisher", 0)
        avg_rating_claimer = user.get("rating_as_claimer", {}).get("average", 5.0)
        avg_rating_publisher = user.get("rating_as_publisher", {}).get("average", 5.0)
        avg_rating = (avg_rating_claimer + avg_rating_publisher) / 2

        # Simple point calculation
        points = tasks_completed * 10 + int(avg_rating * 20)

        # Determine level
        if points >= 4000:
            level = "Diamond"
        elif points >= 1500:
            level = "Platinum"
        elif points >= 500:
            level = "Gold"
        elif points >= 100:
            level = "Silver"
        else:
            level = "Bronze"

        await db.users.update_one(
            {"_id": user_id},
            {
                "$set": {
                    "level": level,
                    "level_points": points
                }
            }
        )

    @staticmethod
    async def get_user_ratings(user_id: str, rating_type: Optional[str] = None) -> List[dict]:
        """Get ratings for a user"""
        db = get_database()

        query = {"ratee_id": ObjectId(user_id)}
        if rating_type:
            query["rating_type"] = rating_type

        ratings = await db.ratings.find(query).sort("created_at", -1).to_list(length=100)

        # Enrich with rater info
        for rating in ratings:
            rater = await db.users.find_one(
                {"_id": rating["rater_id"]},
                {"username": 1, "level": 1}
            )
            ratee = await db.users.find_one(
                {"_id": rating["ratee_id"]},
                {"username": 1}
            )

            rating["rater_username"] = rater.get("username") if rater else None
            rating["ratee_username"] = ratee.get("username") if ratee else None

        return ratings


rating_service = RatingService()
