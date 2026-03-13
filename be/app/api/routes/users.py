"""User API Routes"""
from fastapi import APIRouter, HTTPException, status, Depends
from bson import ObjectId
from app.db.mongodb import get_database
from app.schemas.user import UserResponse, UserUpdate
from app.core.security import get_current_user_id

router = APIRouter()


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: str):
    """Get user profile by ID"""
    db = get_database()

    try:
        user = await db.users.find_one({"_id": ObjectId(user_id)})
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID"
        )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    user["_id"] = str(user["_id"])
    return UserResponse(**user)


@router.patch("/me", response_model=UserResponse)
async def update_current_user(
    update_data: UserUpdate,
    current_user_id: str = Depends(get_current_user_id)
):
    """Update current user profile"""
    db = get_database()

    # Build update dict
    update_dict = update_data.model_dump(exclude_unset=True)

    if not update_dict:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields to update"
        )

    # Update user
    result = await db.users.update_one(
        {"_id": ObjectId(current_user_id)},
        {"$set": update_dict}
    )

    if result.modified_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found or no changes made"
        )

    # Return updated user
    user = await db.users.find_one({"_id": ObjectId(current_user_id)})
    user["_id"] = str(user["_id"])
    return UserResponse(**user)


@router.get("/me/balance", response_model=dict)
async def get_balance(current_user_id: str = Depends(get_current_user_id)):
    """Get current user's shrimp food balance"""
    db = get_database()

    user = await db.users.find_one(
        {"_id": ObjectId(current_user_id)},
        {"shrimp_food_balance": 1, "shrimp_food_frozen": 1}
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return {
        "balance": user.get("shrimp_food_balance", 0),
        "frozen": user.get("shrimp_food_frozen", 0),
        "available": user.get("shrimp_food_balance", 0) - user.get("shrimp_food_frozen", 0)
    }
