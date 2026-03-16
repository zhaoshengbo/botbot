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


@router.get("/balance-analysis")
async def get_balance_analysis(
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Get AI analysis of user's balance and recharge suggestions
    """
    db = get_database()

    # Get user
    user = await db.users.find_one({"_id": ObjectId(current_user_id)})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Get pending tasks count
    pending_tasks = await db.tasks.count_documents({
        "publisher_id": ObjectId(current_user_id),
        "status": {"$in": ["open", "bidding", "contracted", "in_progress"]}
    })

    # Get active bids count
    active_bids = await db.bids.count_documents({
        "bidder_id": ObjectId(current_user_id),
        "status": "active"
    })

    # Calculate average task budget
    pipeline = [
        {"$match": {"publisher_id": ObjectId(current_user_id)}},
        {"$group": {"_id": None, "avg_budget": {"$avg": "$budget"}}}
    ]
    avg_result = await db.tasks.aggregate(pipeline).to_list(1)
    average_task_budget = avg_result[0]["avg_budget"] if avg_result else 50.0

    # Analyze balance
    analysis = await ai_service.analyze_balance(
        current_balance=user.get("shrimp_food_balance", 0),
        frozen_balance=user.get("shrimp_food_frozen", 0),
        pending_tasks=pending_tasks,
        active_bids=active_bids,
        average_task_budget=average_task_budget
    )

    return {
        "success": True,
        "current_balance": user.get("shrimp_food_balance", 0),
        "frozen_balance": user.get("shrimp_food_frozen", 0),
        "available_balance": user.get("shrimp_food_balance", 0) - user.get("shrimp_food_frozen", 0),
        "analysis": analysis
    }


@router.get("/earnings-analysis")
async def get_earnings_analysis(
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Get AI analysis of user's earnings and withdrawal suggestions
    """
    db = get_database()

    # Get user
    user = await db.users.find_one({"_id": ObjectId(current_user_id)})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Calculate total earned from transaction logs
    pipeline = [
        {
            "$match": {
                "user_id": ObjectId(current_user_id),
                "transaction_type": {"$in": ["payment", "fee"]}
            }
        },
        {
            "$group": {
                "_id": None,
                "total": {"$sum": "$amount"}
            }
        }
    ]
    earned_result = await db.transaction_logs.aggregate(pipeline).to_list(1)
    total_earned = abs(earned_result[0]["total"]) if earned_result else 0.0

    completed_tasks = user.get("tasks_completed_as_claimer", 0)
    average_earnings = total_earned / completed_tasks if completed_tasks > 0 else 0.0

    # Analyze earnings
    analysis = await ai_service.analyze_earnings(
        total_earned=total_earned,
        completed_tasks=completed_tasks,
        current_balance=user.get("shrimp_food_balance", 0),
        average_earnings_per_task=average_earnings
    )

    return {
        "success": True,
        "total_earned": total_earned,
        "completed_tasks": completed_tasks,
        "average_earnings_per_task": average_earnings,
        "current_balance": user.get("shrimp_food_balance", 0),
        "analysis": analysis
    }


@router.post("/task-profitability")
async def analyze_task_profitability(
    task_id: str,
    estimated_hours: float,
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Analyze if a task is profitable considering the 10% platform fee
    """
    db = get_database()

    # Get task
    try:
        task = await db.tasks.find_one({"_id": ObjectId(task_id)})
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

    # Get user
    user = await db.users.find_one({"_id": ObjectId(current_user_id)})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Calculate user's average hourly rate
    # Get total earned and total hours from completed contracts
    completed_contracts = await db.contracts.find({
        "claimer_id": ObjectId(current_user_id),
        "status": "completed"
    }).to_list(None)

    if completed_contracts:
        total_earned = sum(c.get("amount", 0) * 0.9 for c in completed_contracts)  # After fee
        total_tasks = len(completed_contracts)
        # Estimate average 5 hours per task if no data
        estimated_total_hours = total_tasks * 5
        current_hourly_rate = total_earned / estimated_total_hours if estimated_total_hours > 0 else 10.0
    else:
        current_hourly_rate = 10.0  # Default rate

    # Analyze profitability
    analysis = await ai_service.calculate_task_profitability(
        task_budget=task.get("budget", 0),
        estimated_hours=estimated_hours,
        current_hourly_rate=current_hourly_rate
    )

    return {
        "success": True,
        "task_budget": task.get("budget", 0),
        "your_earning_after_fee": task.get("budget", 0) * 0.9,
        "platform_fee": task.get("budget", 0) * 0.1,
        "estimated_hours": estimated_hours,
        "your_hourly_rate": current_hourly_rate,
        "analysis": analysis
    }


@router.get("/financial-health")
async def get_financial_health_report(
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Get comprehensive financial health report
    """
    db = get_database()

    # Get user
    user = await db.users.find_one({"_id": ObjectId(current_user_id)})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Calculate total earned (as claimer, after fees)
    earned_pipeline = [
        {
            "$match": {
                "claimer_id": ObjectId(current_user_id),
                "status": "completed"
            }
        },
        {
            "$group": {
                "_id": None,
                "total": {"$sum": "$amount"}
            }
        }
    ]
    earned_result = await db.contracts.aggregate(earned_pipeline).to_list(1)
    total_earned_raw = earned_result[0]["total"] if earned_result else 0.0
    total_earned = total_earned_raw * 0.9  # After 10% fee

    # Calculate total spent (as publisher)
    spent_pipeline = [
        {
            "$match": {
                "publisher_id": ObjectId(current_user_id),
                "status": "completed"
            }
        },
        {
            "$group": {
                "_id": None,
                "total": {"$sum": "$amount"}
            }
        }
    ]
    spent_result = await db.contracts.aggregate(spent_pipeline).to_list(1)
    total_spent = spent_result[0]["total"] if spent_result else 0.0

    # Calculate platform fees paid (10% of earned)
    platform_fees_paid = total_earned_raw * 0.1

    # Generate report
    report = await ai_service.financial_health_report(
        balance=user.get("shrimp_food_balance", 0),
        frozen=user.get("shrimp_food_frozen", 0),
        total_earned=total_earned,
        total_spent=total_spent,
        completed_tasks_as_claimer=user.get("tasks_completed_as_claimer", 0),
        completed_tasks_as_publisher=user.get("tasks_completed_as_publisher", 0),
        platform_fees_paid=platform_fees_paid
    )

    return {
        "success": True,
        "financial_summary": {
            "balance": user.get("shrimp_food_balance", 0),
            "frozen": user.get("shrimp_food_frozen", 0),
            "available": user.get("shrimp_food_balance", 0) - user.get("shrimp_food_frozen", 0),
            "total_earned": total_earned,
            "total_spent": total_spent,
            "platform_fees_paid": platform_fees_paid,
            "net_income": total_earned - total_spent,
            "completed_as_claimer": user.get("tasks_completed_as_claimer", 0),
            "completed_as_publisher": user.get("tasks_completed_as_publisher", 0)
        },
        "report": report
    }


@router.post("/auto-recharge")
async def trigger_auto_recharge(
    current_user_id: str = Depends(get_current_user_id)
):
    """
    AI-powered auto-recharge: check if recharge is needed and create order
    """
    db = get_database()

    # Get user
    user = await db.users.find_one({"_id": ObjectId(current_user_id)})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Check if auto-recharge is enabled
    ai_prefs = user.get("ai_preferences", {})
    if not ai_prefs.get("auto_recharge_enabled", False):
        return {
            "success": False,
            "message": "Auto-recharge is not enabled",
            "enabled": False
        }

    # Get pending tasks count
    pending_tasks = await db.tasks.count_documents({
        "publisher_id": ObjectId(current_user_id),
        "status": {"$in": ["open", "bidding", "contracted", "in_progress"]}
    })

    # Get auto-recharge settings
    threshold = ai_prefs.get("auto_recharge_threshold", 50.0)
    recharge_amount = ai_prefs.get("auto_recharge_amount", 100.0)
    payment_method = ai_prefs.get("preferred_payment_method", "alipay")

    # Ask AI if should recharge
    decision = await ai_service.should_auto_recharge(
        current_balance=user.get("shrimp_food_balance", 0),
        frozen_balance=user.get("shrimp_food_frozen", 0),
        threshold=threshold,
        recharge_amount=recharge_amount,
        pending_tasks=pending_tasks
    )

    if not decision.get("should_recharge"):
        return {
            "success": True,
            "recharged": False,
            "reason": decision.get("reason"),
            "current_balance": user.get("shrimp_food_balance", 0)
        }

    # Create recharge order
    from app.services.payment_service import payment_service
    from app.services.alipay_service import alipay_service
    from app.services.wechat_pay_service import wechat_pay_service
    from app.schemas.payment import PaymentMethod, DeviceInfo

    try:
        # Create order
        order = await payment_service.create_recharge_order(
            user_id=current_user_id,
            amount_rmb=decision.get("suggested_amount_rmb", recharge_amount / 10.0),
            payment_method=PaymentMethod.ALIPAY if payment_method == "alipay" else PaymentMethod.WECHAT,
            device_info=DeviceInfo(ip="127.0.0.1", user_agent="AI Agent", device_type="bot")
        )

        # Generate payment info
        if payment_method == "alipay":
            payment_url = await alipay_service.create_page_pay(
                order_no=order["order_no"],
                amount=order["amount_rmb"],
                subject=f"AI自动充值 - {order['amount_shrimp']}kg虾粮"
            )
            payment_info = {"payment_url": payment_url}
        else:
            result = await wechat_pay_service.create_order(
                order_no=order["order_no"],
                amount=order["amount_rmb"],
                description=f"AI自动充值 - {order['amount_shrimp']}kg虾粮",
                client_ip="127.0.0.1"
            )
            payment_info = {"qr_code": result.get("code_url")}

        return {
            "success": True,
            "recharged": True,
            "order_no": order["order_no"],
            "amount_rmb": order["amount_rmb"],
            "amount_shrimp": order["amount_shrimp"],
            "urgency": decision.get("urgency"),
            "reason": decision.get("reason"),
            "payment_info": payment_info
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create recharge order: {str(e)}"
        )


@router.post("/auto-withdraw")
async def trigger_auto_withdraw(
    current_user_id: str = Depends(get_current_user_id)
):
    """
    AI-powered auto-withdrawal: check if withdrawal is needed and create request
    """
    db = get_database()

    # Get user
    user = await db.users.find_one({"_id": ObjectId(current_user_id)})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Check if auto-withdrawal is enabled
    ai_prefs = user.get("ai_preferences", {})
    if not ai_prefs.get("auto_withdrawal_enabled", False):
        return {
            "success": False,
            "message": "Auto-withdrawal is not enabled",
            "enabled": False
        }

    # Check if withdrawal account is configured
    withdrawal_account = ai_prefs.get("withdrawal_account_info")
    if not withdrawal_account:
        return {
            "success": False,
            "message": "Withdrawal account not configured",
            "configured": False
        }

    # Get pending bids count
    pending_bids = await db.bids.count_documents({
        "bidder_id": ObjectId(current_user_id),
        "status": "active"
    })

    # Get auto-withdrawal settings
    threshold = ai_prefs.get("auto_withdrawal_threshold", 500.0)
    withdrawal_amount = ai_prefs.get("auto_withdrawal_amount", 300.0)

    # Ask AI if should withdraw
    decision = await ai_service.should_auto_withdraw(
        current_balance=user.get("shrimp_food_balance", 0),
        frozen_balance=user.get("shrimp_food_frozen", 0),
        threshold=threshold,
        withdrawal_amount=withdrawal_amount,
        pending_bids=pending_bids
    )

    if not decision.get("should_withdraw"):
        return {
            "success": True,
            "withdrawn": False,
            "reason": decision.get("reason"),
            "current_balance": user.get("shrimp_food_balance", 0)
        }

    # Create withdrawal order
    from app.services.payment_service import payment_service
    from app.schemas.payment import WithdrawalMethod, WithdrawalAccount, DeviceInfo

    try:
        # Parse withdrawal account
        account_info = WithdrawalAccount(**withdrawal_account)

        # Determine withdrawal method
        withdrawal_method = WithdrawalMethod.ALIPAY
        if withdrawal_account.get("account_type") == "wechat":
            withdrawal_method = WithdrawalMethod.WECHAT
        elif withdrawal_account.get("account_type") == "bank":
            withdrawal_method = WithdrawalMethod.BANK

        # Create withdrawal order
        order = await payment_service.create_withdrawal_order(
            user_id=current_user_id,
            amount_shrimp=withdrawal_amount,
            withdrawal_method=withdrawal_method,
            withdrawal_account=account_info,
            device_info=DeviceInfo(ip="127.0.0.1", user_agent="AI Agent", device_type="bot")
        )

        return {
            "success": True,
            "withdrawn": True,
            "order_no": order["order_no"],
            "amount_shrimp": order["amount_shrimp"],
            "amount_rmb": order["amount_rmb"],
            "remaining_balance": decision.get("remaining_balance"),
            "reason": decision.get("reason"),
            "status": "pending_review"
        }

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create withdrawal order: {str(e)}"
        )


@router.get("/auto-finance-status")
async def get_auto_finance_status(
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Get current auto-finance configuration and status
    """
    db = get_database()

    user = await db.users.find_one({"_id": ObjectId(current_user_id)})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    ai_prefs = user.get("ai_preferences", {})
    balance = user.get("shrimp_food_balance", 0)
    frozen = user.get("shrimp_food_frozen", 0)
    available = balance - frozen

    return {
        "success": True,
        "current_balance": {
            "total": balance,
            "frozen": frozen,
            "available": available
        },
        "auto_recharge": {
            "enabled": ai_prefs.get("auto_recharge_enabled", False),
            "threshold": ai_prefs.get("auto_recharge_threshold", 50.0),
            "amount": ai_prefs.get("auto_recharge_amount", 100.0),
            "payment_method": ai_prefs.get("preferred_payment_method", "alipay"),
            "will_trigger": available < ai_prefs.get("auto_recharge_threshold", 50.0)
        },
        "auto_withdrawal": {
            "enabled": ai_prefs.get("auto_withdrawal_enabled", False),
            "threshold": ai_prefs.get("auto_withdrawal_threshold", 500.0),
            "amount": ai_prefs.get("auto_withdrawal_amount", 300.0),
            "account_configured": ai_prefs.get("withdrawal_account_info") is not None,
            "will_trigger": available > ai_prefs.get("auto_withdrawal_threshold", 500.0)
        }
    }


@router.get("/evaluate-tasks")
async def evaluate_available_tasks(
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Batch evaluate all available tasks for current lobster
    Returns a list of tasks with AI evaluation results
    """
    db = get_database()

    # Get user
    user = await db.users.find_one({"_id": ObjectId(current_user_id)})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Get all open/bidding tasks
    tasks = await db.tasks.find({
        "status": {"$in": ["open", "bidding"]},
        "publisher_id": {"$ne": ObjectId(current_user_id)}  # Exclude own tasks
    }).to_list(None)

    # Get AI preferences
    ai_prefs = user.get("ai_preferences", {})
    min_confidence = ai_prefs.get("min_confidence_threshold", 0.7)
    max_bid = ai_prefs.get("max_bid_amount", 100.0)

    evaluations = []

    for task in tasks:
        try:
            # Analyze each task
            can_complete, suggested_bid, analysis = await ai_service.analyze_task(
                task_title=task.get("title", ""),
                task_description=task.get("description", ""),
                task_deliverables=task.get("deliverables", ""),
                task_budget=task.get("budget", 0),
                user_level=user.get("level", "Bronze"),
                user_completed_tasks=user.get("tasks_completed_as_claimer", 0)
            )

            # Determine recommendation
            should_bid = (
                can_complete and
                analysis.confidence >= min_confidence and
                suggested_bid is not None and
                suggested_bid <= max_bid
            )

            evaluations.append({
                "task_id": str(task["_id"]),
                "task_title": task.get("title", ""),
                "task_budget": task.get("budget", 0),
                "can_complete": can_complete,
                "suggested_bid_amount": suggested_bid,
                "confidence": analysis.confidence,
                "estimated_hours": analysis.estimated_hours,
                "feasibility_score": analysis.feasibility_score,
                "reasoning": analysis.reasoning,
                "should_bid": should_bid,
                "recommendation": "✅ 推荐接单" if should_bid else ("⚠️ 能力不足" if not can_complete else "❌ 不推荐")
            })

        except Exception as e:
            # Skip tasks that fail evaluation
            evaluations.append({
                "task_id": str(task["_id"]),
                "task_title": task.get("title", ""),
                "error": f"评估失败: {str(e)}"
            })

    # Sort by recommendation
    evaluations.sort(key=lambda x: x.get("should_bid", False), reverse=True)

    return {
        "success": True,
        "total_tasks": len(tasks),
        "recommended_tasks": sum(1 for e in evaluations if e.get("should_bid")),
        "evaluations": evaluations
    }


@router.post("/evaluate-task-batch")
async def evaluate_specific_tasks(
    task_ids: list[str],
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Evaluate specific tasks by IDs
    """
    db = get_database()

    # Get user
    user = await db.users.find_one({"_id": ObjectId(current_user_id)})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Get AI preferences
    ai_prefs = user.get("ai_preferences", {})
    min_confidence = ai_prefs.get("min_confidence_threshold", 0.7)
    max_bid = ai_prefs.get("max_bid_amount", 100.0)

    evaluations = []

    for task_id in task_ids:
        try:
            task = await db.tasks.find_one({"_id": ObjectId(task_id)})
            if not task:
                evaluations.append({
                    "task_id": task_id,
                    "error": "Task not found"
                })
                continue

            # Analyze task
            can_complete, suggested_bid, analysis = await ai_service.analyze_task(
                task_title=task.get("title", ""),
                task_description=task.get("description", ""),
                task_deliverables=task.get("deliverables", ""),
                task_budget=task.get("budget", 0),
                user_level=user.get("level", "Bronze"),
                user_completed_tasks=user.get("tasks_completed_as_claimer", 0)
            )

            should_bid = (
                can_complete and
                analysis.confidence >= min_confidence and
                suggested_bid is not None and
                suggested_bid <= max_bid
            )

            evaluations.append({
                "task_id": task_id,
                "task_title": task.get("title", ""),
                "task_budget": task.get("budget", 0),
                "can_complete": can_complete,
                "suggested_bid_amount": suggested_bid,
                "confidence": analysis.confidence,
                "estimated_hours": analysis.estimated_hours,
                "reasoning": analysis.reasoning,
                "should_bid": should_bid
            })

        except Exception as e:
            evaluations.append({
                "task_id": task_id,
                "error": f"评估失败: {str(e)}"
            })

    return {
        "success": True,
        "evaluations": evaluations
    }
