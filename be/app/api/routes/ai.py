"""AI API Routes"""
from fastapi import APIRouter, HTTPException, status, Depends
from bson import ObjectId
from app.db.mongodb import get_database
from app.schemas.bid import AnalyzeTaskRequest, AnalyzeTaskResponse
from app.services.ai_service import ai_service
from app.core.security import get_current_user_id

router = APIRouter()


@router.post("/analyze-task", response_model=AnalyzeTaskResponse)
async def analyze_task(
    request: AnalyzeTaskRequest,
    current_user_id: str = Depends(get_current_user_id)
):
    """Analyze if user can complete a task and get bid suggestion"""
    db = get_database()

    # Get task
    try:
        task = await db.tasks.find_one({"_id": ObjectId(request.task_id)})
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid task ID"
        )

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    # Get user info
    user = await db.users.find_one({"_id": ObjectId(current_user_id)})

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Analyze task
    can_complete, suggested_bid, analysis = await ai_service.analyze_task(
        task_title=task.get("title", ""),
        task_description=task.get("description", ""),
        task_deliverables=task.get("deliverables", ""),
        task_budget=task.get("budget", 0),
        user_level=user.get("level", "Bronze"),
        user_completed_tasks=user.get("tasks_completed_as_claimer", 0)
    )

    # Determine if should bid based on AI preferences
    ai_prefs = user.get("ai_preferences", {})
    min_confidence = ai_prefs.get("min_confidence_threshold", 0.7)
    max_bid = ai_prefs.get("max_bid_amount", 100.0)

    should_bid = (
        can_complete and
        analysis.confidence >= min_confidence and
        suggested_bid is not None and
        suggested_bid <= max_bid
    )

    return AnalyzeTaskResponse(
        can_complete=can_complete,
        suggested_bid_amount=suggested_bid,
        analysis=analysis,
        should_bid=should_bid
    )
