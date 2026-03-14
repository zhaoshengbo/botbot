"""Contract API Routes"""
from fastapi import APIRouter, HTTPException, status, Depends, Query
from bson import ObjectId
from typing import Optional
from app.db.mongodb import get_database
from app.schemas.contract import (
    ContractCreate,
    ContractResponse,
    ContractListResponse,
    DeliverableSubmit,
    ContractComplete
)
from app.services.contract_service import contract_service
from app.core.security import get_current_user_id

router = APIRouter()


@router.post("/", response_model=ContractResponse, status_code=status.HTTP_201_CREATED)
async def create_contract(
    contract_data: ContractCreate,
    current_user_id: str = Depends(get_current_user_id)
):
    """Create contract by accepting a bid"""
    try:
        contract = await contract_service.create_contract(
            contract_data.bid_id,
            current_user_id
        )

        contract["_id"] = str(contract["_id"])
        contract["task_id"] = str(contract["task_id"])
        contract["publisher_id"] = str(contract["publisher_id"])
        contract["claimer_id"] = str(contract["claimer_id"])

        # Enrich with task and user info
        enriched = await contract_service.get_contract(contract["_id"])
        enriched["_id"] = str(enriched["_id"])
        enriched["task_id"] = str(enriched["task_id"])
        enriched["publisher_id"] = str(enriched["publisher_id"])
        enriched["claimer_id"] = str(enriched["claimer_id"])

        return ContractResponse(**enriched)
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


@router.get("/", response_model=ContractListResponse)
async def list_contracts(
    role: Optional[str] = Query(None, description="Filter by role: publisher or claimer"),
    status: Optional[str] = Query(None, description="Filter by status"),
    current_user_id: str = Depends(get_current_user_id)
):
    """List contracts for current user"""
    try:
        contracts = await contract_service.list_contracts(
            current_user_id,
            role=role,
            status=status
        )

        # Convert ObjectIds
        for contract in contracts:
            contract["_id"] = str(contract["_id"])
            contract["task_id"] = str(contract["task_id"])
            contract["publisher_id"] = str(contract["publisher_id"])
            contract["claimer_id"] = str(contract["claimer_id"])

        return ContractListResponse(
            contracts=[ContractResponse(**c) for c in contracts],
            total=len(contracts)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/{contract_id}", response_model=ContractResponse)
async def get_contract(
    contract_id: str,
    current_user_id: str = Depends(get_current_user_id)
):
    """Get contract details"""
    contract = await contract_service.get_contract(contract_id)

    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract not found"
        )

    # Check if user is part of contract
    if str(contract["publisher_id"]) != current_user_id and str(contract["claimer_id"]) != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this contract"
        )

    contract["_id"] = str(contract["_id"])
    contract["task_id"] = str(contract["task_id"])
    contract["publisher_id"] = str(contract["publisher_id"])
    contract["claimer_id"] = str(contract["claimer_id"])

    return ContractResponse(**contract)


@router.post("/{contract_id}/submit", response_model=ContractResponse)
@router.post("/{contract_id}/deliverables", response_model=ContractResponse)
async def submit_deliverables(
    contract_id: str,
    deliverable_data: DeliverableSubmit,
    current_user_id: str = Depends(get_current_user_id)
):
    """Submit deliverables for a contract"""
    try:
        url = deliverable_data.deliverable_url or deliverable_data.deliverables_url
        contract = await contract_service.submit_deliverables(
            contract_id,
            url,
            current_user_id,
            notes=deliverable_data.notes
        )

        # Enrich
        enriched = await contract_service.get_contract(contract_id)
        enriched["_id"] = str(enriched["_id"])
        enriched["task_id"] = str(enriched["task_id"])
        enriched["publisher_id"] = str(enriched["publisher_id"])
        enriched["claimer_id"] = str(enriched["claimer_id"])

        return ContractResponse(**enriched)
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


@router.post("/{contract_id}/complete", response_model=ContractResponse)
async def complete_contract(
    contract_id: str,
    complete_data: ContractComplete,
    current_user_id: str = Depends(get_current_user_id)
):
    """Complete contract (approve or reject deliverables)"""
    try:
        contract = await contract_service.complete_contract(
            contract_id,
            complete_data.approved,
            current_user_id,
            complete_data.rejection_reason
        )

        # Enrich
        enriched = await contract_service.get_contract(contract_id)
        enriched["_id"] = str(enriched["_id"])
        enriched["task_id"] = str(enriched["task_id"])
        enriched["publisher_id"] = str(enriched["publisher_id"])
        enriched["claimer_id"] = str(enriched["claimer_id"])

        return ContractResponse(**enriched)
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
