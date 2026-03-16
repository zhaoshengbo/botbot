"""Task API Routes"""
from fastapi import APIRouter, HTTPException, status, Depends, Query
from bson import ObjectId
from app.db.mongodb import get_database
from app.schemas.task import TaskCreate, TaskUpdate, TaskResponse, TaskListResponse
from app.services.task_service import task_service
from app.core.security import get_current_user_id
from typing import Optional

router = APIRouter()


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_data: TaskCreate,
    current_user_id: str = Depends(get_current_user_id)
):
    """Create a new task"""
    try:
        task = await task_service.create_task(task_data, current_user_id)
        task["id"] = str(task.pop("_id"))
        task["publisher_id"] = str(task["publisher_id"])

        # Get publisher username
        db = get_database()
        user = await db.users.find_one({"_id": ObjectId(current_user_id)})
        task["publisher_username"] = user.get("username") if user else None

        return TaskResponse(**task)
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


@router.get("", response_model=TaskListResponse)
async def list_tasks(
    status: Optional[str] = Query(None, description="Filter by status"),
    publisher_id: Optional[str] = Query(None, description="Filter by publisher ID"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
):
    """List tasks with filters and pagination"""
    skip = (page - 1) * page_size

    try:
        tasks, total = await task_service.list_tasks(
            status=status,
            publisher_id=publisher_id,
            skip=skip,
            limit=page_size
        )

        # Convert ObjectIds to strings and rename _id to id
        for task in tasks:
            task["id"] = str(task.pop("_id"))
            task["publisher_id"] = str(task["publisher_id"])

        return TaskListResponse(
            tasks=[TaskResponse(**task) for task in tasks],
            total=total,
            page=page,
            page_size=page_size
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(task_id: str):
    """Get task details"""
    task = await task_service.get_task(task_id, increment_view=True)

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    # Convert ObjectIds
    task["id"] = str(task.pop("_id"))
    task["publisher_id"] = str(task["publisher_id"])

    # Get publisher info
    db = get_database()
    user = await db.users.find_one({"_id": ObjectId(task["publisher_id"])})
    task["publisher_username"] = user.get("username") if user else None

    return TaskResponse(**task)


@router.patch("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: str,
    update_data: TaskUpdate,
    current_user_id: str = Depends(get_current_user_id)
):
    """Update task (only by publisher)"""
    try:
        task = await task_service.update_task(task_id, update_data, current_user_id)

        task["id"] = str(task.pop("_id"))
        task["publisher_id"] = str(task["publisher_id"])

        # Get publisher username
        db = get_database()
        user = await db.users.find_one({"_id": ObjectId(current_user_id)})
        task["publisher_username"] = user.get("username") if user else None

        return TaskResponse(**task)
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


@router.delete("/{task_id}", response_model=TaskResponse)
async def cancel_task(
    task_id: str,
    cancellation_reason: Optional[str] = None,
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Cancel task with penalty calculation

    - No bids: Free cancellation
    - Has bids: 3% penalty per bidder
    - Contracted/In progress: Not allowed
    """
    try:
        task = await task_service.cancel_task(task_id, current_user_id, cancellation_reason)

        task["id"] = str(task.pop("_id"))
        task["publisher_id"] = str(task["publisher_id"])

        # Get publisher username
        db = get_database()
        user = await db.users.find_one({"_id": ObjectId(current_user_id)})
        task["publisher_username"] = user.get("username") if user else None

        return TaskResponse(**task)
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


@router.get("/{task_id}/cancellation-estimate")
async def get_cancellation_estimate(
    task_id: str,
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Preview cancellation penalty

    Returns the cost estimate for cancelling this task,
    helping publishers make informed decisions.
    """
    try:
        estimate = await task_service.get_cancellation_estimate(task_id, current_user_id)
        return estimate
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/{task_id}/bids")
async def get_task_bids(task_id: str):
    """Get all bids for a task"""
    from app.services.bid_service import bid_service

    try:
        bids = await bid_service.get_task_bids(task_id)

        # Convert ObjectIds
        db = get_database()
        for bid in bids:
            bid["id"] = str(bid.pop("_id"))
            bid["task_id"] = str(bid["task_id"])
            bid["bidder_id"] = str(bid["bidder_id"])

            # Get bidder username
            user = await db.users.find_one({"_id": ObjectId(bid["bidder_id"])})
            bid["bidder_username"] = user.get("username") if user else None

        return {
            "bids": bids,
            "total": len(bids)
        }
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


@router.get("/my/tasks", response_model=TaskListResponse)
async def get_my_tasks(
    status: Optional[str] = Query(None, description="Filter by status"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user_id: str = Depends(get_current_user_id)
):
    """Get current user's published tasks"""
    skip = (page - 1) * page_size

    tasks, total = await task_service.list_tasks(
        status=status,
        publisher_id=current_user_id,
        skip=skip,
        limit=page_size
    )

    # Convert ObjectIds and rename _id to id
    for task in tasks:
        task["id"] = str(task.pop("_id"))
        task["publisher_id"] = str(task["publisher_id"])

    return TaskListResponse(
        tasks=[TaskResponse(**task) for task in tasks],
        total=total,
        page=page,
        page_size=page_size
    )
