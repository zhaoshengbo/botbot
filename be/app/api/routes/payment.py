"""Payment API Routes"""
from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import HTMLResponse, Response
from typing import List, Optional
from datetime import datetime
from bson import ObjectId

from app.schemas.payment import (
    RechargeCreate,
    RechargeResponse,
    RechargePaymentInfo,
    WithdrawalCreate,
    WithdrawalResponse,
    WithdrawalReview,
    TransactionLogResponse,
    PlatformStatsResponse,
    PaymentMethod,
    RechargeStatus,
    WithdrawalStatus
)
from app.services.payment_service import payment_service
from app.services.alipay_service import alipay_service
from app.services.wechat_pay_service import wechat_pay_service
from app.core.security import get_current_user_id, get_current_admin_id
from app.db.mongodb import get_database

router = APIRouter()


# ========== Recharge Endpoints ==========

@router.post("/recharge/create", response_model=dict)
async def create_recharge_order(
    data: RechargeCreate,
    user_id: str = Depends(get_current_user_id)
):
    """
    Create recharge order and return payment information
    """
    try:
        # Create recharge order
        order = await payment_service.create_recharge_order(
            user_id=user_id,
            amount_rmb=data.amount_rmb,
            payment_method=data.payment_method,
            device_info=data.device_info
        )

        # Generate payment info based on payment method
        payment_info = {}

        if data.payment_method == PaymentMethod.ALIPAY:
            # Create Alipay payment
            payment_url = await alipay_service.create_page_pay(
                order_no=order["order_no"],
                amount=order["amount_rmb"],
                subject=f"BotBot虾粮充值 - {order['amount_shrimp']}kg"
            )
            payment_info = {
                "order_no": order["order_no"],
                "payment_method": "alipay",
                "payment_url": payment_url
            }

        elif data.payment_method == PaymentMethod.WECHAT:
            # Create WeChat payment
            result = await wechat_pay_service.create_order(
                order_no=order["order_no"],
                amount=order["amount_rmb"],
                description=f"BotBot虾粮充值 - {order['amount_shrimp']}kg",
                client_ip=data.device_info.ip if data.device_info else "127.0.0.1"
            )
            payment_info = {
                "order_no": order["order_no"],
                "payment_method": "wechat",
                "qr_code": result.get("code_url")
            }

        return {
            "success": True,
            "order": {
                "order_no": order["order_no"],
                "amount_rmb": order["amount_rmb"],
                "amount_shrimp": order["amount_shrimp"],
                "status": order["payment_status"]
            },
            "payment_info": payment_info
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create recharge order: {str(e)}")


@router.get("/recharge/{order_no}", response_model=RechargeResponse)
async def get_recharge_order(
    order_no: str,
    user_id: str = Depends(get_current_user_id)
):
    """
    Get recharge order details
    """
    db = get_database()

    order = await db.recharge_orders.find_one({"order_no": order_no})
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    # Verify ownership
    if str(order["user_id"]) != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")

    # Convert ObjectId to string
    order["_id"] = str(order["_id"])
    order["user_id"] = str(order["user_id"])

    return RechargeResponse(**order)


@router.get("/recharge/list", response_model=List[RechargeResponse])
async def list_recharge_orders(
    user_id: str = Depends(get_current_user_id),
    skip: int = 0,
    limit: int = 20
):
    """
    List user's recharge orders
    """
    db = get_database()

    cursor = db.recharge_orders.find(
        {"user_id": ObjectId(user_id)}
    ).sort("created_at", -1).skip(skip).limit(limit)

    orders = await cursor.to_list(length=limit)

    # Convert ObjectIds to strings
    for order in orders:
        order["_id"] = str(order["_id"])
        order["user_id"] = str(order["user_id"])

    return [RechargeResponse(**order) for order in orders]


# ========== Alipay Callback Endpoints ==========

@router.post("/alipay/notify")
async def alipay_notify(request: Request):
    """
    Alipay async notification callback
    This endpoint does not require authentication
    """
    try:
        # Get form data
        form_data = await request.form()
        params = dict(form_data)

        # Verify signature
        if not await alipay_service.verify_notify(params):
            print("Alipay signature verification failed")
            return Response(content="fail", media_type="text/plain")

        # Extract order info
        out_trade_no = params.get("out_trade_no")
        trade_no = params.get("trade_no")
        trade_status = params.get("trade_status")
        total_amount = float(params.get("total_amount", 0))

        # Check trade status
        if trade_status not in ["TRADE_SUCCESS", "TRADE_FINISHED"]:
            return Response(content="success", media_type="text/plain")

        # Get order
        db = get_database()
        order = await db.recharge_orders.find_one({"order_no": out_trade_no})
        if not order:
            print(f"Order not found: {out_trade_no}")
            return Response(content="fail", media_type="text/plain")

        # Verify amount
        if abs(order["amount_rmb"] - total_amount) > 0.01:
            print(f"Amount mismatch: {order['amount_rmb']} != {total_amount}")
            return Response(content="fail", media_type="text/plain")

        # Complete recharge
        await payment_service.complete_recharge_order(
            order_no=out_trade_no,
            payment_channel_order_no=trade_no,
            payment_time=datetime.utcnow()
        )

        return Response(content="success", media_type="text/plain")

    except Exception as e:
        print(f"Alipay notify error: {e}")
        return Response(content="fail", media_type="text/plain")


@router.get("/alipay/return")
async def alipay_return(request: Request):
    """
    Alipay sync return (user redirected after payment)
    """
    # This is just a redirect page, actual processing is done in notify
    return HTMLResponse(content="""
    <html>
        <head><title>Payment Result</title></head>
        <body>
            <h1>Payment processing...</h1>
            <p>Please wait while we confirm your payment.</p>
            <script>
                setTimeout(function() {
                    window.location.href = '/';
                }, 3000);
            </script>
        </body>
    </html>
    """)


# ========== WeChat Pay Callback Endpoints ==========

@router.post("/wechat/notify")
async def wechat_notify(request: Request):
    """
    WeChat Pay async notification callback
    This endpoint does not require authentication
    """
    try:
        # Get XML data
        xml_data = await request.body()

        # Verify and parse notification
        result = await wechat_pay_service.verify_notify(xml_data.decode('utf-8'))
        if not result:
            print("WeChat Pay signature verification failed")
            return Response(
                content=wechat_pay_service.generate_fail_xml("Signature verification failed"),
                media_type="application/xml"
            )

        # Extract order info
        out_trade_no = result.get("out_trade_no")
        transaction_id = result.get("transaction_id")
        total_fee = result.get("total_fee")

        # Get order
        db = get_database()
        order = await db.recharge_orders.find_one({"order_no": out_trade_no})
        if not order:
            print(f"Order not found: {out_trade_no}")
            return Response(
                content=wechat_pay_service.generate_fail_xml("Order not found"),
                media_type="application/xml"
            )

        # Verify amount
        if abs(order["amount_rmb"] - total_fee) > 0.01:
            print(f"Amount mismatch: {order['amount_rmb']} != {total_fee}")
            return Response(
                content=wechat_pay_service.generate_fail_xml("Amount mismatch"),
                media_type="application/xml"
            )

        # Complete recharge
        await payment_service.complete_recharge_order(
            order_no=out_trade_no,
            payment_channel_order_no=transaction_id,
            payment_time=datetime.utcnow()
        )

        return Response(
            content=wechat_pay_service.generate_success_xml(),
            media_type="application/xml"
        )

    except Exception as e:
        print(f"WeChat Pay notify error: {e}")
        return Response(
            content=wechat_pay_service.generate_fail_xml(str(e)),
            media_type="application/xml"
        )


# ========== Withdrawal Endpoints ==========

@router.post("/withdrawal/create", response_model=WithdrawalResponse)
async def create_withdrawal_order(
    data: WithdrawalCreate,
    user_id: str = Depends(get_current_user_id)
):
    """
    Create withdrawal request
    """
    try:
        order = await payment_service.create_withdrawal_order(
            user_id=user_id,
            amount_shrimp=data.amount_shrimp,
            withdrawal_method=data.withdrawal_method,
            withdrawal_account=data.withdrawal_account,
            device_info=data.device_info
        )

        # Convert ObjectIds to strings
        order["_id"] = str(order["_id"])
        order["user_id"] = str(order["user_id"])

        return WithdrawalResponse(**order)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create withdrawal: {str(e)}")


@router.get("/withdrawal/{order_no}", response_model=WithdrawalResponse)
async def get_withdrawal_order(
    order_no: str,
    user_id: str = Depends(get_current_user_id)
):
    """
    Get withdrawal order details
    """
    db = get_database()

    order = await db.withdrawal_orders.find_one({"order_no": order_no})
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    # Verify ownership
    if str(order["user_id"]) != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")

    # Convert ObjectIds to strings
    order["_id"] = str(order["_id"])
    order["user_id"] = str(order["user_id"])

    return WithdrawalResponse(**order)


@router.get("/withdrawal/list", response_model=List[WithdrawalResponse])
async def list_withdrawal_orders(
    user_id: str = Depends(get_current_user_id),
    skip: int = 0,
    limit: int = 20
):
    """
    List user's withdrawal orders
    """
    db = get_database()

    cursor = db.withdrawal_orders.find(
        {"user_id": ObjectId(user_id)}
    ).sort("created_at", -1).skip(skip).limit(limit)

    orders = await cursor.to_list(length=limit)

    # Convert ObjectIds to strings
    for order in orders:
        order["_id"] = str(order["_id"])
        order["user_id"] = str(order["user_id"])

    return [WithdrawalResponse(**order) for order in orders]


@router.post("/withdrawal/{order_no}/cancel")
async def cancel_withdrawal(
    order_no: str,
    user_id: str = Depends(get_current_user_id)
):
    """
    Cancel withdrawal (only PENDING status)
    """
    try:
        order = await payment_service.cancel_withdrawal_order(order_no, user_id)

        # Convert ObjectIds to strings
        order["_id"] = str(order["_id"])
        order["user_id"] = str(order["user_id"])

        return {
            "success": True,
            "order": WithdrawalResponse(**order)
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to cancel withdrawal: {str(e)}")


# ========== Admin Endpoints ==========
# Note: These endpoints need proper admin authentication
# For now, using regular user authentication as placeholder

@router.post("/admin/withdrawal/{order_no}/review", response_model=WithdrawalResponse)
async def review_withdrawal(
    order_no: str,
    review_data: WithdrawalReview,
    admin_id: str = Depends(get_current_admin_id)
):
    """
    Review withdrawal request (admin only)
    """
    try:
        order = await payment_service.review_withdrawal_order(
            order_no=order_no,
            approved=review_data.approved,
            rejection_reason=review_data.rejection_reason,
            reviewer_id=admin_id
        )

        # Convert ObjectIds to strings
        order["_id"] = str(order["_id"])
        order["user_id"] = str(order["user_id"])

        return WithdrawalResponse(**order)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to review withdrawal: {str(e)}")


@router.post("/admin/withdrawal/{order_no}/complete")
async def complete_withdrawal(
    order_no: str,
    transfer_order_no: str,
    admin_id: str = Depends(get_current_admin_id)
):
    """
    Complete withdrawal after transfer (admin only)
    """
    try:
        order = await payment_service.complete_withdrawal_order(
            order_no=order_no,
            transfer_order_no=transfer_order_no
        )

        # Convert ObjectIds to strings
        order["_id"] = str(order["_id"])
        order["user_id"] = str(order["user_id"])

        return {
            "success": True,
            "order": WithdrawalResponse(**order)
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to complete withdrawal: {str(e)}")


@router.get("/admin/stats/platform", response_model=PlatformStatsResponse)
async def get_platform_stats(
    admin_id: str = Depends(get_current_admin_id)
):
    """
    Get platform statistics (admin only)
    """
    try:
        stats = await payment_service.get_platform_account()
        return PlatformStatsResponse(**stats)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")


# ========== Transaction Log Endpoints ==========

@router.get("/transaction-logs", response_model=List[TransactionLogResponse])
async def get_transaction_logs(
    user_id: str = Depends(get_current_user_id),
    skip: int = 0,
    limit: int = 20
):
    """
    Get user's transaction logs
    """
    db = get_database()

    cursor = db.transaction_logs.find(
        {"user_id": ObjectId(user_id)}
    ).sort("created_at", -1).skip(skip).limit(limit)

    logs = await cursor.to_list(length=limit)

    # Convert ObjectIds to strings
    for log in logs:
        log["_id"] = str(log["_id"])
        if log.get("user_id"):
            log["user_id"] = str(log["user_id"])

    return [TransactionLogResponse(**log) for log in logs]
