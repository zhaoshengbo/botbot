"""Rating API Routes"""
from fastapi import APIRouter, HTTPException, status, Depends, Query, Path
from bson import ObjectId
from typing import Optional
from app.db.mongodb import get_database
from app.schemas.rating import RatingCreate, RatingResponse, RatingListResponse
from app.services.rating_service import rating_service
from app.core.security import get_current_user_id

router = APIRouter()


@router.post("/", response_model=RatingResponse, status_code=status.HTTP_201_CREATED)
async def create_rating(
    rating_data: RatingCreate,
    current_user_id: str = Depends(get_current_user_id)
):
    """Submit a rating for a completed contract"""
    try:
        rating = await rating_service.create_rating(rating_data, current_user_id)

        rating["id"] = str(rating.pop("_id"))
        rating["contract_id"] = str(rating["contract_id"])
        rating["task_id"] = str(rating["task_id"])
        rating["rater_id"] = str(rating["rater_id"])
        rating["ratee_id"] = str(rating["ratee_id"])

        # Get user info
        db = get_database()
        rater = await db.users.find_one({"_id": ObjectId(current_user_id)})
        ratee = await db.users.find_one({"_id": ObjectId(rating["ratee_id"])})

        rating["rater_username"] = rater.get("username") if rater else None
        rating["ratee_username"] = ratee.get("username") if ratee else None

        return RatingResponse(**rating)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/users/{user_id}/ratings", response_model=RatingListResponse)
async def get_user_ratings(
    user_id: str = Path(..., description="User ID"),
    rating_type: Optional[str] = Query(None, description="Filter by rating type")
):
    """Get ratings for a specific user"""
    try:
        ratings = await rating_service.get_user_ratings(user_id, rating_type)

        # Convert ObjectIds
        for rating in ratings:
            rating["id"] = str(rating.pop("_id"))
            rating["contract_id"] = str(rating["contract_id"])
            rating["task_id"] = str(rating["task_id"])
            rating["rater_id"] = str(rating["rater_id"])
            rating["ratee_id"] = str(rating["ratee_id"])

        return RatingListResponse(
            ratings=[RatingResponse(**r) for r in ratings],
            total=len(ratings)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/my-ratings", response_model=RatingListResponse)
async def get_my_ratings(
    rating_type: Optional[str] = Query(None, description="Filter by rating type"),
    current_user_id: str = Depends(get_current_user_id)
):
    """Get ratings for current user"""
    try:
        ratings = await rating_service.get_user_ratings(current_user_id, rating_type)

        # Convert ObjectIds
        for rating in ratings:
            rating["id"] = str(rating.pop("_id"))
            rating["contract_id"] = str(rating["contract_id"])
            rating["task_id"] = str(rating["task_id"])
            rating["rater_id"] = str(rating["rater_id"])
            rating["ratee_id"] = str(rating["ratee_id"])

        return RatingListResponse(
            ratings=[RatingResponse(**r) for r in ratings],
            total=len(ratings)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
