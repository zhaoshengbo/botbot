"""Bid API Routes"""
from fastapi import APIRouter, HTTPException, status, Depends, Path, Query
from bson import ObjectId
from typing import Optional
from app.db.mongodb import get_database
from app.schemas.bid import BidCreate, BidResponse, BidListResponse
from app.services.bid_service import bid_service
from app.services.ai_service import ai_service
from app.core.security import get_current_user_id

router = APIRouter()


@router.post("/", response_model=BidResponse, status_code=status.HTTP_201_CREATED)
async def create_bid_v2(
    bid_data: BidCreate,
    current_user_id: str = Depends(get_current_user_id)
):
    """Submit a bid on a task (v2 - cleaner API)"""
    db = get_database()

    try:
        bid = await bid_service.create_bid(bid_data.task_id, bid_data, current_user_id, None)

        bid["_id"] = str(bid["_id"])
        bid["task_id"] = str(bid["task_id"])
        bid["bidder_id"] = str(bid["bidder_id"])

        # Get bidder username
        user = await db.users.find_one({"_id": ObjectId(current_user_id)})
        bid["bidder_username"] = user.get("username") if user else None

        return BidResponse(**bid)
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


@router.post("/{bid_id}/accept")
async def accept_bid(
    bid_id: str = Path(..., description="Bid ID"),
    current_user_id: str = Depends(get_current_user_id)
):
    """Accept a bid and create a contract"""
    try:
        from app.services.contract_service import contract_service

        contract = await contract_service.create_contract(bid_id, current_user_id)

        return {
            "message": "Bid accepted successfully",
            "contract_id": str(contract["_id"]),
            "bid_id": bid_id
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


@router.post("/{task_id}/bids", response_model=BidResponse, status_code=status.HTTP_201_CREATED)
async def create_bid(
    task_id: str = Path(..., description="Task ID"),
    bid_data: BidCreate = ...,
    use_ai: bool = Query(False, description="Use AI analysis before bidding"),
    current_user_id: str = Depends(get_current_user_id)
):
    """Submit a bid on a task"""
    db = get_database()

    ai_analysis = None

    # If AI requested, analyze task first
    if use_ai:
        try:
            task = await db.tasks.find_one({"_id": ObjectId(task_id)})
            if not task:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Task not found"
                )

            user = await db.users.find_one({"_id": ObjectId(current_user_id)})

            can_complete, suggested_bid, analysis = await ai_service.analyze_task(
                task_title=task.get("title", ""),
                task_description=task.get("description", ""),
                task_deliverables=task.get("deliverables", ""),
                task_budget=task.get("budget", 0),
                user_level=user.get("level", "Bronze"),
                user_completed_tasks=user.get("tasks_completed_as_claimer", 0)
            )

            if not can_complete:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="AI analysis suggests you may not be able to complete this task"
                )

            ai_analysis = analysis

        except HTTPException:
            raise
        except Exception as e:
            # AI failed, continue without it
            pass

    try:
        bid = await bid_service.create_bid(task_id, bid_data, current_user_id, ai_analysis)

        bid["_id"] = str(bid["_id"])
        bid["task_id"] = str(bid["task_id"])
        bid["bidder_id"] = str(bid["bidder_id"])

        # Get bidder username
        user = await db.users.find_one({"_id": ObjectId(current_user_id)})
        bid["bidder_username"] = user.get("username") if user else None

        return BidResponse(**bid)
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


@router.get("/{task_id}/bids", response_model=BidListResponse)
async def get_task_bids(
    task_id: str = Path(..., description="Task ID")
):
    """Get all bids for a task"""
    try:
        bids = await bid_service.get_task_bids(task_id)

        # Convert ObjectIds
        for bid in bids:
            bid["_id"] = str(bid["_id"])
            bid["task_id"] = str(bid["task_id"])
            bid["bidder_id"] = str(bid["bidder_id"])

        return BidListResponse(
            bids=[BidResponse(**bid) for bid in bids],
            total=len(bids)
        )
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


@router.get("/my-bids", response_model=BidListResponse)
async def get_my_bids(
    status: Optional[str] = Query(None, description="Filter by status"),
    current_user_id: str = Depends(get_current_user_id)
):
    """Get current user's bids"""
    try:
        bids = await bid_service.get_user_bids(current_user_id, status)

        # Convert ObjectIds
        for bid in bids:
            bid["_id"] = str(bid["_id"])
            bid["task_id"] = str(bid["task_id"])
            bid["bidder_id"] = str(bid["bidder_id"])

        return BidListResponse(
            bids=[BidResponse(**bid) for bid in bids],
            total=len(bids)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.delete("/{bid_id}", response_model=BidResponse)
async def withdraw_bid(
    bid_id: str = Path(..., description="Bid ID"),
    current_user_id: str = Depends(get_current_user_id)
):
    """Withdraw a bid"""
    try:
        bid = await bid_service.withdraw_bid(bid_id, current_user_id)

        bid["_id"] = str(bid["_id"])
        bid["task_id"] = str(bid["task_id"])
        bid["bidder_id"] = str(bid["bidder_id"])

        db = get_database()
        user = await db.users.find_one({"_id": ObjectId(current_user_id)})
        bid["bidder_username"] = user.get("username") if user else None

        return BidResponse(**bid)
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
