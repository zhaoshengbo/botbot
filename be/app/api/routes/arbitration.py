"""Arbitration API Routes"""
from fastapi import APIRouter, HTTPException, status, Depends, Query
from app.schemas.arbitration import (
    ArbitrationRequest,
    ArbitrationDecision,
    ArbitrationResponse,
    ArbitrationListResponse
)
from app.services.arbitration_service import arbitration_service
from app.core.security import get_current_user_id
from app.db.mongodb import get_database
from bson import ObjectId

router = APIRouter()


@router.post("", response_model=ArbitrationResponse, status_code=status.HTTP_201_CREATED)
async def create_arbitration_request(
    request: ArbitrationRequest,
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Submit arbitration request

    User can request arbitration when there's a dispute over deliverables.
    Contract must be in DISPUTED status.
    """
    try:
        arbitration = await arbitration_service.create_arbitration(
            request,
            current_user_id
        )

        # Convert ObjectIds to strings
        arbitration["id"] = str(arbitration.pop("_id"))
        arbitration["contract_id"] = str(arbitration["contract_id"])
        arbitration["task_id"] = str(arbitration["task_id"])
        arbitration["publisher_id"] = str(arbitration["publisher_id"])
        arbitration["claimer_id"] = str(arbitration["claimer_id"])
        arbitration["requester_id"] = str(arbitration["requester_id"])
        if arbitration.get("assigned_admin_id"):
            arbitration["assigned_admin_id"] = str(arbitration["assigned_admin_id"])

        return ArbitrationResponse(**arbitration)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/my-cases", response_model=ArbitrationListResponse)
async def get_my_arbitration_cases(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Get user's arbitration cases

    Returns all arbitrations where the current user is either publisher or claimer.
    """
    try:
        skip = (page - 1) * page_size
        arbitrations, total = await arbitration_service.get_user_arbitrations(
            current_user_id,
            skip,
            page_size
        )

        # Convert ObjectIds
        db = get_database()
        arbitration_responses = []
        for arb in arbitrations:
            arb["id"] = str(arb.pop("_id"))
            arb["contract_id"] = str(arb["contract_id"])
            arb["task_id"] = str(arb["task_id"])
            arb["publisher_id"] = str(arb["publisher_id"])
            arb["claimer_id"] = str(arb["claimer_id"])
            arb["requester_id"] = str(arb["requester_id"])
            if arb.get("assigned_admin_id"):
                arb["assigned_admin_id"] = str(arb["assigned_admin_id"])

            # Get usernames
            publisher = await db.users.find_one(
                {"_id": ObjectId(arb["publisher_id"])},
                {"username": 1}
            )
            claimer = await db.users.find_one(
                {"_id": ObjectId(arb["claimer_id"])},
                {"username": 1}
            )
            arb["publisher_username"] = publisher.get("username") if publisher else None
            arb["claimer_username"] = claimer.get("username") if claimer else None

            arbitration_responses.append(ArbitrationResponse(**arb))

        return ArbitrationListResponse(
            arbitrations=arbitration_responses,
            total=total,
            page=page,
            page_size=page_size
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/{arbitration_id}", response_model=ArbitrationResponse)
async def get_arbitration_details(
    arbitration_id: str,
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Get arbitration details

    User can view arbitration if they are the publisher or claimer.
    """
    try:
        db = get_database()
        arbitration = await db.arbitrations.find_one({"_id": ObjectId(arbitration_id)})

        if not arbitration:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Arbitration not found"
            )

        # Verify user is involved
        if (str(arbitration["publisher_id"]) != current_user_id and
            str(arbitration["claimer_id"]) != current_user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view this arbitration"
            )

        # Convert ObjectIds
        arbitration["id"] = str(arbitration.pop("_id"))
        arbitration["contract_id"] = str(arbitration["contract_id"])
        arbitration["task_id"] = str(arbitration["task_id"])
        arbitration["publisher_id"] = str(arbitration["publisher_id"])
        arbitration["claimer_id"] = str(arbitration["claimer_id"])
        arbitration["requester_id"] = str(arbitration["requester_id"])
        if arbitration.get("assigned_admin_id"):
            arbitration["assigned_admin_id"] = str(arbitration["assigned_admin_id"])

        # Get task title
        task = await db.tasks.find_one({"_id": ObjectId(arbitration["task_id"])}, {"title": 1})
        arbitration["task_title"] = task.get("title") if task else None

        # Get usernames
        publisher = await db.users.find_one(
            {"_id": ObjectId(arbitration["publisher_id"])},
            {"username": 1}
        )
        claimer = await db.users.find_one(
            {"_id": ObjectId(arbitration["claimer_id"])},
            {"username": 1}
        )
        arbitration["publisher_username"] = publisher.get("username") if publisher else None
        arbitration["claimer_username"] = claimer.get("username") if claimer else None

        return ArbitrationResponse(**arbitration)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
