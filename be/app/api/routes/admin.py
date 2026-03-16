"""Admin API Routes"""
from fastapi import APIRouter, HTTPException, Depends, Request, Query
from typing import List, Optional
from datetime import datetime
from bson import ObjectId

from app.schemas.user import UserResponse
from app.schemas.payment import (
    PlatformWithdrawalCreate,
    PlatformWithdrawalResponse,
    PlatformWithdrawalReview
)
from app.schemas.arbitration import (
    ArbitrationDecision,
    ArbitrationResponse,
    ArbitrationListResponse
)
from app.services.payment_service import payment_service
from app.services.arbitration_service import arbitration_service
from app.core.security import get_current_admin_id
from app.db.mongodb import get_database


router = APIRouter()


# ========== Admin Management Endpoints ==========

@router.post("/users/{user_id}/promote")
async def promote_user_to_admin(
    user_id: str,
    request: Request,
    admin_id: str = Depends(get_current_admin_id)
):
    """
    Promote user to admin (admin only)
    """
    try:
        db = get_database()

        # Verify target user exists
        target_user = await db.users.find_one({"_id": ObjectId(user_id)})
        if not target_user:
            raise HTTPException(status_code=404, detail="User not found")

        # Check if already admin
        if target_user.get("role") == "admin":
            raise HTTPException(status_code=400, detail="User is already an admin")

        # Update user role
        await db.users.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"role": "admin"}}
        )

        # Log operation
        await db.admin_operation_logs.insert_one({
            "operator_id": ObjectId(admin_id),
            "operation_type": "promote",
            "target_user_id": ObjectId(user_id),
            "target_user_phone": target_user["phone_number"],
            "timestamp": datetime.utcnow(),
            "ip_address": request.client.host if request.client else "unknown"
        })

        return {
            "success": True,
            "message": f"User {target_user['phone_number']} promoted to admin"
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to promote user: {str(e)}")


@router.post("/users/{user_id}/demote")
async def demote_admin_to_user(
    user_id: str,
    request: Request,
    admin_id: str = Depends(get_current_admin_id)
):
    """
    Demote admin to regular user (admin only)
    """
    try:
        db = get_database()

        # Verify target user exists
        target_user = await db.users.find_one({"_id": ObjectId(user_id)})
        if not target_user:
            raise HTTPException(status_code=404, detail="User not found")

        # Check if already regular user
        if target_user.get("role") != "admin":
            raise HTTPException(status_code=400, detail="User is not an admin")

        # Prevent self-demotion
        if user_id == admin_id:
            raise HTTPException(status_code=403, detail="Cannot demote yourself")

        # Update user role
        await db.users.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"role": "user"}}
        )

        # Log operation
        await db.admin_operation_logs.insert_one({
            "operator_id": ObjectId(admin_id),
            "operation_type": "demote",
            "target_user_id": ObjectId(user_id),
            "target_user_phone": target_user["phone_number"],
            "timestamp": datetime.utcnow(),
            "ip_address": request.client.host if request.client else "unknown"
        })

        return {
            "success": True,
            "message": f"Admin {target_user['phone_number']} demoted to user"
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to demote admin: {str(e)}")


@router.get("/users/list", response_model=List[UserResponse])
async def list_admins(
    admin_id: str = Depends(get_current_admin_id),
    skip: int = 0,
    limit: int = 50
):
    """
    List all admin users (admin only)
    """
    try:
        db = get_database()

        cursor = db.users.find(
            {"role": "admin"}
        ).sort("created_at", -1).skip(skip).limit(limit)

        admins = await cursor.to_list(length=limit)

        # Convert ObjectIds to strings
        for admin in admins:
            admin["_id"] = str(admin["_id"])

        return [UserResponse(**admin) for admin in admins]

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list admins: {str(e)}")


@router.get("/logs/operations")
async def get_operation_logs(
    admin_id: str = Depends(get_current_admin_id),
    target_user_id: Optional[str] = None,
    skip: int = 0,
    limit: int = 50
):
    """
    Get admin operation logs (admin only)
    """
    try:
        db = get_database()

        # Build query
        query = {}
        if target_user_id:
            query["target_user_id"] = ObjectId(target_user_id)

        cursor = db.admin_operation_logs.find(query).sort("timestamp", -1).skip(skip).limit(limit)
        logs = await cursor.to_list(length=limit)

        # Convert ObjectIds to strings
        for log in logs:
            log["_id"] = str(log["_id"])
            log["operator_id"] = str(log["operator_id"])
            log["target_user_id"] = str(log["target_user_id"])

        return {
            "success": True,
            "logs": logs,
            "total": await db.admin_operation_logs.count_documents(query)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get logs: {str(e)}")


# ========== Platform Withdrawal Endpoints ==========

@router.post("/platform-withdrawal/create", response_model=PlatformWithdrawalResponse)
async def create_platform_withdrawal(
    data: PlatformWithdrawalCreate,
    admin_id: str = Depends(get_current_admin_id)
):
    """
    Create platform withdrawal order (admin only)
    """
    try:
        order = await payment_service.create_platform_withdrawal_order(
            admin_id=admin_id,
            amount_shrimp=data.amount_shrimp,
            withdrawal_method=data.withdrawal_method,
            withdrawal_account=data.withdrawal_account,
            remarks=data.remarks
        )

        # Convert ObjectIds to strings
        order["_id"] = str(order["_id"])
        order["created_by"] = str(order["created_by"])

        return PlatformWithdrawalResponse(**order)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create platform withdrawal: {str(e)}")


@router.get("/platform-withdrawal/{order_no}", response_model=PlatformWithdrawalResponse)
async def get_platform_withdrawal(
    order_no: str,
    admin_id: str = Depends(get_current_admin_id)
):
    """
    Get platform withdrawal order details (admin only)
    """
    db = get_database()

    order = await db.platform_withdrawal_orders.find_one({"order_no": order_no})
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    # Convert ObjectIds to strings
    order["_id"] = str(order["_id"])
    order["created_by"] = str(order["created_by"])
    if order.get("reviewed_by"):
        order["reviewed_by"] = str(order["reviewed_by"])

    return PlatformWithdrawalResponse(**order)


@router.get("/platform-withdrawal/list", response_model=List[PlatformWithdrawalResponse])
async def list_platform_withdrawals(
    admin_id: str = Depends(get_current_admin_id),
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 20
):
    """
    List platform withdrawal orders (admin only)
    """
    db = get_database()

    query = {}
    if status:
        query["status"] = status

    cursor = db.platform_withdrawal_orders.find(query).sort("created_at", -1).skip(skip).limit(limit)
    orders = await cursor.to_list(length=limit)

    # Convert ObjectIds to strings
    for order in orders:
        order["_id"] = str(order["_id"])
        order["created_by"] = str(order["created_by"])
        if order.get("reviewed_by"):
            order["reviewed_by"] = str(order["reviewed_by"])

    return [PlatformWithdrawalResponse(**order) for order in orders]


@router.post("/platform-withdrawal/{order_no}/review", response_model=PlatformWithdrawalResponse)
async def review_platform_withdrawal(
    order_no: str,
    review_data: PlatformWithdrawalReview,
    admin_id: str = Depends(get_current_admin_id)
):
    """
    Review platform withdrawal order (admin only)
    Requires different admin than creator for security
    """
    try:
        order = await payment_service.review_platform_withdrawal_order(
            order_no=order_no,
            approved=review_data.approved,
            reviewer_id=admin_id,
            rejection_reason=review_data.rejection_reason
        )

        # Convert ObjectIds to strings
        order["_id"] = str(order["_id"])
        order["created_by"] = str(order["created_by"])
        if order.get("reviewed_by"):
            order["reviewed_by"] = str(order["reviewed_by"])

        return PlatformWithdrawalResponse(**order)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to review platform withdrawal: {str(e)}")


@router.post("/platform-withdrawal/{order_no}/complete")
async def complete_platform_withdrawal(
    order_no: str,
    transfer_order_no: str,
    admin_id: str = Depends(get_current_admin_id)
):
    """
    Complete platform withdrawal after bank transfer (admin only)
    """
    try:
        order = await payment_service.complete_platform_withdrawal_order(
            order_no=order_no,
            transfer_order_no=transfer_order_no,
            admin_id=admin_id
        )

        # Convert ObjectIds to strings
        order["_id"] = str(order["_id"])
        order["created_by"] = str(order["created_by"])
        if order.get("reviewed_by"):
            order["reviewed_by"] = str(order["reviewed_by"])

        return {
            "success": True,
            "order": PlatformWithdrawalResponse(**order)
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to complete platform withdrawal: {str(e)}")


# ========== Arbitration Management Endpoints ==========

@router.get("/arbitration/pending", response_model=ArbitrationListResponse)
async def get_pending_arbitrations(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    admin_id: str = Depends(get_current_admin_id)
):
    """
    Get pending arbitrations (admin only)

    Returns list of arbitrations awaiting admin review.
    """
    try:
        skip = (page - 1) * page_size
        arbitrations, total = await arbitration_service.get_pending_arbitrations(skip, page_size)

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

            arbitration_responses.append(ArbitrationResponse(**arb))

        return ArbitrationListResponse(
            arbitrations=arbitration_responses,
            total=total,
            page=page,
            page_size=page_size
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get pending arbitrations: {str(e)}"
        )


@router.post("/arbitration/{arbitration_id}/assign")
async def assign_arbitration_to_self(
    arbitration_id: str,
    admin_id: str = Depends(get_current_admin_id)
):
    """
    Claim arbitration case (admin only)

    Admin assigns themselves to review the arbitration case.
    """
    try:
        arbitration = await arbitration_service.assign_arbitration(
            arbitration_id,
            admin_id
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

        return {
            "success": True,
            "message": "Arbitration assigned successfully",
            "arbitration": ArbitrationResponse(**arbitration)
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to assign arbitration: {str(e)}"
        )


@router.post("/arbitration/{arbitration_id}/resolve")
async def resolve_arbitration_case(
    arbitration_id: str,
    decision: ArbitrationDecision,
    admin_id: str = Depends(get_current_admin_id)
):
    """
    Make arbitration decision (admin only)

    Admin decides how to split payment between publisher and claimer.
    Percentages must sum to 100%.
    """
    try:
        # Ensure arbitration_id matches
        if decision.arbitration_id != arbitration_id:
            raise HTTPException(
                status_code=400,
                detail="Arbitration ID mismatch"
            )

        result = await arbitration_service.resolve_arbitration(
            decision,
            admin_id
        )

        # Convert ObjectIds
        result["id"] = str(result.pop("_id"))
        result["contract_id"] = str(result["contract_id"])
        result["task_id"] = str(result["task_id"])
        result["publisher_id"] = str(result["publisher_id"])
        result["claimer_id"] = str(result["claimer_id"])
        result["requester_id"] = str(result["requester_id"])
        if result.get("assigned_admin_id"):
            result["assigned_admin_id"] = str(result["assigned_admin_id"])

        return {
            "success": True,
            "message": "Arbitration resolved successfully",
            "arbitration": ArbitrationResponse(**result)
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to resolve arbitration: {str(e)}"
        )
