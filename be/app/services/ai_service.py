"""AI Service using Claude API"""
from anthropic import Anthropic
from app.core.config import settings
from app.schemas.bid import AIAnalysis
from typing import Tuple, Optional
import json


class AIService:
    """AI service for task analysis and bidding"""

    def __init__(self):
        if settings.ANTHROPIC_API_KEY:
            self.client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        else:
            self.client = None

    async def analyze_task(
        self,
        task_title: str,
        task_description: str,
        task_deliverables: str,
        task_budget: float,
        user_level: str,
        user_completed_tasks: int
    ) -> Tuple[bool, Optional[float], AIAnalysis]:
        """
        Analyze if a task can be completed and suggest bid amount

        Args:
            task_title: Task title
            task_description: Task description
            task_deliverables: Required deliverables
            task_budget: Publisher's budget
            user_level: Lobster's level
            user_completed_tasks: Number of completed tasks

        Returns:
            Tuple of (can_complete, suggested_bid_amount, analysis)
        """

        # If no API key, return mock response
        if not self.client:
            return self._mock_analyze_task(task_budget)

        # Build prompt for Claude
        prompt = f"""You are an AI assistant helping a lobster (AI agent) decide whether to bid on a task.

Task Information:
- Title: {task_title}
- Description: {task_description}
- Required Deliverables: {task_deliverables}
- Publisher's Budget: {task_budget} kg of shrimp food

Lobster's Profile:
- Level: {user_level}
- Completed Tasks: {user_completed_tasks}

Important Notes:
- After completing the task, you can submit deliverables via the platform OR send them directly to the publisher via email if they provided their email address.
- Email delivery is convenient for large files (use cloud storage links like Google Drive, Dropbox) or direct attachments.
- Always confirm the delivery method with the publisher if unclear.

Please analyze:
1. Can this lobster realistically complete this task? Consider the technical requirements and complexity.
2. How many hours would it likely take?
3. What should be the bid amount? (Should not exceed the budget)
4. What is your confidence level in this assessment? (0-1)
5. Provide clear reasoning for your decision. If accepting this task, briefly mention the deliverable submission options available.

Respond in JSON format:
{{
    "can_complete": true/false,
    "feasibility_score": 0.0-1.0,
    "estimated_hours": number,
    "suggested_bid_amount": number or null,
    "confidence": 0.0-1.0,
    "reasoning": "detailed explanation including delivery method reminder"
}}
"""

        try:
            message = self.client.messages.create(
                model=settings.CLAUDE_MODEL,
                max_tokens=1024,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            # Parse response
            response_text = message.content[0].text

            # Try to extract JSON from the response
            try:
                # Find JSON in the response
                start = response_text.find('{')
                end = response_text.rfind('}') + 1
                if start >= 0 and end > start:
                    json_str = response_text[start:end]
                    result = json.loads(json_str)
                else:
                    # If no JSON found, return mock response
                    return self._mock_analyze_task(task_budget)
            except:
                return self._mock_analyze_task(task_budget)

            can_complete = result.get("can_complete", False)
            suggested_bid = result.get("suggested_bid_amount")

            # If suggested bid exceeds budget, don't bid
            if suggested_bid and suggested_bid > task_budget:
                can_complete = False
                suggested_bid = None

            analysis = AIAnalysis(
                feasibility_score=result.get("feasibility_score", 0.5),
                estimated_hours=result.get("estimated_hours", 1.0),
                confidence=result.get("confidence", 0.5),
                reasoning=result.get("reasoning", "AI analysis completed")
            )

            return can_complete, suggested_bid, analysis

        except Exception as e:
            print(f"AI Service Error: {e}")
            return self._mock_analyze_task(task_budget)

    def _mock_analyze_task(self, budget: float) -> Tuple[bool, Optional[float], AIAnalysis]:
        """Mock task analysis for development"""
        import random

        can_complete = random.choice([True, True, False])  # 66% chance of yes

        if can_complete:
            suggested_bid = budget * random.uniform(0.7, 0.95)
            feasibility = random.uniform(0.7, 0.95)
            confidence = random.uniform(0.7, 0.9)
            reasoning = f"This task appears feasible. Based on the requirements, I estimate it will take approximately {random.randint(2, 10)} hours. The suggested bid of {suggested_bid:.1f}kg is competitive while ensuring fair compensation. Upon completion, you can submit deliverables through the platform or send them directly via email if the publisher provided their email address (convenient for large files via cloud storage links)."
        else:
            suggested_bid = None
            feasibility = random.uniform(0.2, 0.5)
            confidence = random.uniform(0.6, 0.8)
            reasoning = "This task may be too complex or outside my current capabilities. I recommend looking for other opportunities that better match my skill set."

        analysis = AIAnalysis(
            feasibility_score=feasibility,
            estimated_hours=random.uniform(1, 20),
            confidence=confidence,
            reasoning=reasoning
        )

        return can_complete, suggested_bid, analysis

    async def analyze_balance(
        self,
        current_balance: float,
        frozen_balance: float,
        pending_tasks: int,
        active_bids: int,
        average_task_budget: float
    ) -> dict:
        """
        Analyze user's balance and provide recharge suggestions

        Args:
            current_balance: Current shrimp food balance
            frozen_balance: Frozen shrimp food
            pending_tasks: Number of pending tasks (user is publisher)
            active_bids: Number of active bids
            average_task_budget: Average budget of tasks user usually posts

        Returns:
            Dict with balance analysis and suggestions
        """

        if not self.client:
            return self._mock_balance_analysis(current_balance, frozen_balance)

        available_balance = current_balance - frozen_balance

        prompt = f"""You are a financial advisor for a lobster (AI agent) in the BotBot marketplace.

Current Financial Status:
- Total Balance: {current_balance} kg shrimp food
- Frozen (in pending transactions): {frozen_balance} kg
- Available Balance: {available_balance} kg
- Active Tasks as Publisher: {pending_tasks}
- Active Bids: {active_bids}
- Average Task Budget: {average_task_budget} kg

Exchange Rate: 1 RMB = 10 kg shrimp food

Please analyze:
1. Is the current balance sufficient for the user's activity level?
2. Should the user recharge? If yes, suggest an amount in RMB.
3. What are the risks of running low on balance?
4. Provide practical financial advice.

Respond in JSON format:
{{
    "balance_status": "healthy/low/critical",
    "should_recharge": true/false,
    "suggested_recharge_rmb": number or null,
    "suggested_recharge_shrimp": number or null,
    "risk_level": "low/medium/high",
    "advice": "practical suggestions"
}}"""

        try:
            message = self.client.messages.create(
                model=settings.CLAUDE_MODEL,
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}]
            )

            response_text = message.content[0].text
            start = response_text.find('{')
            end = response_text.rfind('}') + 1

            if start >= 0 and end > start:
                json_str = response_text[start:end]
                result = json.loads(json_str)
                return result
            else:
                return self._mock_balance_analysis(current_balance, frozen_balance)

        except Exception as e:
            print(f"Balance Analysis Error: {e}")
            return self._mock_balance_analysis(current_balance, frozen_balance)

    async def analyze_earnings(
        self,
        total_earned: float,
        completed_tasks: int,
        current_balance: float,
        average_earnings_per_task: float
    ) -> dict:
        """
        Analyze user's earnings and provide withdrawal suggestions

        Args:
            total_earned: Total shrimp food earned
            completed_tasks: Number of completed tasks
            current_balance: Current balance
            average_earnings_per_task: Average earning per task

        Returns:
            Dict with earnings analysis and withdrawal suggestions
        """

        if not self.client:
            return self._mock_earnings_analysis(total_earned, current_balance)

        prompt = f"""You are a financial advisor for a lobster (AI agent) in the BotBot marketplace.

Earnings Summary:
- Total Earned: {total_earned} kg shrimp food
- Completed Tasks: {completed_tasks}
- Current Balance: {current_balance} kg
- Average Earning per Task: {average_earnings_per_task} kg

Exchange Rate: 10 kg shrimp food = 1 RMB
Minimum Withdrawal: 100 kg shrimp food

Please analyze:
1. Is the performance good compared to task count?
2. Should the user consider withdrawing? If yes, suggest an amount.
3. What's the optimal balance to maintain for continued activity?
4. Provide strategic advice for maximizing earnings.

Respond in JSON format:
{{
    "performance_rating": "excellent/good/average/poor",
    "should_withdraw": true/false,
    "suggested_withdrawal_shrimp": number or null,
    "suggested_withdrawal_rmb": number or null,
    "optimal_balance": number,
    "advice": "strategic suggestions"
}}"""

        try:
            message = self.client.messages.create(
                model=settings.CLAUDE_MODEL,
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}]
            )

            response_text = message.content[0].text
            start = response_text.find('{')
            end = response_text.rfind('}') + 1

            if start >= 0 and end > start:
                json_str = response_text[start:end]
                result = json.loads(json_str)
                return result
            else:
                return self._mock_earnings_analysis(total_earned, current_balance)

        except Exception as e:
            print(f"Earnings Analysis Error: {e}")
            return self._mock_earnings_analysis(total_earned, current_balance)

    async def calculate_task_profitability(
        self,
        task_budget: float,
        estimated_hours: float,
        current_hourly_rate: float
    ) -> dict:
        """
        Calculate if a task is profitable considering the 10% platform fee

        Args:
            task_budget: Task budget in shrimp food
            estimated_hours: Estimated hours to complete
            current_hourly_rate: User's current average hourly rate

        Returns:
            Dict with profitability analysis
        """

        # Platform takes 10% fee
        actual_earning = task_budget * 0.9
        hourly_rate = actual_earning / estimated_hours if estimated_hours > 0 else 0

        if not self.client:
            return self._mock_profitability_analysis(task_budget, actual_earning, hourly_rate, current_hourly_rate)

        prompt = f"""You are a financial advisor for a lobster (AI agent) evaluating a task opportunity.

Task Details:
- Publisher's Budget: {task_budget} kg shrimp food
- Your Earning (after 10% platform fee): {actual_earning} kg
- Estimated Hours: {estimated_hours}
- Calculated Hourly Rate: {hourly_rate:.2f} kg/hour
- Your Current Average Hourly Rate: {current_hourly_rate:.2f} kg/hour

Platform Fee: 10% (charged on task completion)

Please analyze:
1. Is this task profitable compared to your average rate?
2. Should you accept this task?
3. What's the minimum bid you should place to maintain profitability?
4. Consider the platform fee in your calculation.

Respond in JSON format:
{{
    "is_profitable": true/false,
    "profitability_score": 0.0-1.0,
    "recommended_action": "accept/negotiate/decline",
    "minimum_profitable_bid": number,
    "reasoning": "detailed explanation including fee impact"
}}"""

        try:
            message = self.client.messages.create(
                model=settings.CLAUDE_MODEL,
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}]
            )

            response_text = message.content[0].text
            start = response_text.find('{')
            end = response_text.rfind('}') + 1

            if start >= 0 and end > start:
                json_str = response_text[start:end]
                result = json.loads(json_str)
                return result
            else:
                return self._mock_profitability_analysis(task_budget, actual_earning, hourly_rate, current_hourly_rate)

        except Exception as e:
            print(f"Profitability Analysis Error: {e}")
            return self._mock_profitability_analysis(task_budget, actual_earning, hourly_rate, current_hourly_rate)

    async def financial_health_report(
        self,
        balance: float,
        frozen: float,
        total_earned: float,
        total_spent: float,
        completed_tasks_as_claimer: int,
        completed_tasks_as_publisher: int,
        platform_fees_paid: float
    ) -> dict:
        """
        Generate comprehensive financial health report

        Args:
            balance: Current balance
            frozen: Frozen balance
            total_earned: Total earned from completed tasks
            total_spent: Total spent on publishing tasks
            completed_tasks_as_claimer: Tasks completed as worker
            completed_tasks_as_publisher: Tasks published
            platform_fees_paid: Total platform fees paid

        Returns:
            Dict with comprehensive financial analysis
        """

        if not self.client:
            return self._mock_financial_report(balance, total_earned, total_spent, platform_fees_paid)

        net_income = total_earned - total_spent - platform_fees_paid
        available = balance - frozen

        prompt = f"""You are a financial advisor providing a comprehensive report for a lobster (AI agent).

Financial Summary:
- Current Balance: {balance} kg shrimp food
- Available (not frozen): {available} kg
- Total Earned: {total_earned} kg
- Total Spent on Publishing Tasks: {total_spent} kg
- Platform Fees Paid: {platform_fees_paid} kg (10% of completed tasks)
- Net Income: {net_income} kg
- Tasks Completed as Worker: {completed_tasks_as_claimer}
- Tasks Published: {completed_tasks_as_publisher}

Provide a comprehensive financial health assessment:
1. Overall financial health rating
2. Key strengths and weaknesses
3. Recommendations for improvement
4. Warning signs (if any)

Respond in JSON format:
{{
    "health_score": 0.0-100.0,
    "health_grade": "A/B/C/D/F",
    "strengths": ["list of strengths"],
    "weaknesses": ["list of weaknesses"],
    "recommendations": ["list of recommendations"],
    "warnings": ["list of warnings or empty array"],
    "summary": "overall assessment"
}}"""

        try:
            message = self.client.messages.create(
                model=settings.CLAUDE_MODEL,
                max_tokens=1536,
                messages=[{"role": "user", "content": prompt}]
            )

            response_text = message.content[0].text
            start = response_text.find('{')
            end = response_text.rfind('}') + 1

            if start >= 0 and end > start:
                json_str = response_text[start:end]
                result = json.loads(json_str)
                return result
            else:
                return self._mock_financial_report(balance, total_earned, total_spent, platform_fees_paid)

        except Exception as e:
            print(f"Financial Report Error: {e}")
            return self._mock_financial_report(balance, total_earned, total_spent, platform_fees_paid)

    # Mock methods for development
    def _mock_balance_analysis(self, balance: float, frozen: float) -> dict:
        """Mock balance analysis"""
        available = balance - frozen

        if available < 50:
            return {
                "balance_status": "critical",
                "should_recharge": True,
                "suggested_recharge_rmb": 10.0,
                "suggested_recharge_shrimp": 100.0,
                "risk_level": "high",
                "advice": "Your available balance is critically low. Consider recharging 10 RMB (100kg shrimp food) to maintain your activity level and avoid missing task opportunities."
            }
        elif available < 200:
            return {
                "balance_status": "low",
                "should_recharge": True,
                "suggested_recharge_rmb": 5.0,
                "suggested_recharge_shrimp": 50.0,
                "risk_level": "medium",
                "advice": "Your balance is running low. A small recharge of 5 RMB would ensure you don't miss any opportunities."
            }
        else:
            return {
                "balance_status": "healthy",
                "should_recharge": False,
                "suggested_recharge_rmb": None,
                "suggested_recharge_shrimp": None,
                "risk_level": "low",
                "advice": "Your balance looks healthy. Continue monitoring your activity and recharge when needed."
            }

    def _mock_earnings_analysis(self, earned: float, balance: float) -> dict:
        """Mock earnings analysis"""
        if balance > 500:
            return {
                "performance_rating": "excellent",
                "should_withdraw": True,
                "suggested_withdrawal_shrimp": 300.0,
                "suggested_withdrawal_rmb": 30.0,
                "optimal_balance": 200.0,
                "advice": "Great work! You've accumulated substantial earnings. Consider withdrawing 30 RMB while maintaining a working balance of 200kg for ongoing activities."
            }
        else:
            return {
                "performance_rating": "good",
                "should_withdraw": False,
                "suggested_withdrawal_shrimp": None,
                "suggested_withdrawal_rmb": None,
                "optimal_balance": 200.0,
                "advice": "You're making good progress. Keep building your balance before considering withdrawal. Aim for at least 500kg before withdrawing."
            }

    def _mock_profitability_analysis(self, budget: float, actual: float, hourly: float, avg_hourly: float) -> dict:
        """Mock profitability analysis"""
        is_profitable = hourly >= avg_hourly * 0.8

        return {
            "is_profitable": is_profitable,
            "profitability_score": min(hourly / avg_hourly, 1.0) if avg_hourly > 0 else 0.5,
            "recommended_action": "accept" if is_profitable else "decline",
            "minimum_profitable_bid": budget * 0.75,
            "reasoning": f"After the 10% platform fee, you'll earn {actual:.1f}kg. Your hourly rate would be {hourly:.2f}kg/hour compared to your average of {avg_hourly:.2f}kg/hour. {'This meets your profitability threshold.' if is_profitable else 'This is below your average rate.'}"
        }

    def _mock_financial_report(self, balance: float, earned: float, spent: float, fees: float) -> dict:
        """Mock financial report"""
        net = earned - spent - fees
        health_score = min(100, max(0, (balance / 100) * 20 + (net / 100) * 30 + 50))

        if health_score >= 80:
            grade = "A"
        elif health_score >= 60:
            grade = "B"
        elif health_score >= 40:
            grade = "C"
        else:
            grade = "D"

        return {
            "health_score": health_score,
            "health_grade": grade,
            "strengths": ["Consistent earning pattern", "Good balance management"],
            "weaknesses": ["Could optimize fee management"],
            "recommendations": [
                "Consider tasks that offer better rates after fees",
                "Maintain a buffer balance for opportunities"
            ],
            "warnings": [] if balance > 50 else ["Low balance - risk of missing opportunities"],
            "summary": f"Overall financial health is {grade}. You have earned {earned:.1f}kg with net income of {net:.1f}kg after fees."
        }

    async def should_auto_recharge(
        self,
        current_balance: float,
        frozen_balance: float,
        threshold: float,
        recharge_amount: float,
        pending_tasks: int
    ) -> dict:
        """
        Decide if auto-recharge should be triggered

        Args:
            current_balance: Current balance
            frozen_balance: Frozen balance
            threshold: User's recharge threshold
            recharge_amount: User's preferred recharge amount
            pending_tasks: Number of pending tasks

        Returns:
            Dict with decision and reasoning
        """

        available = current_balance - frozen_balance

        # Simple rule-based decision (can be enhanced with AI later)
        should_recharge = available < threshold

        if not self.client or not should_recharge:
            # Fast path: no AI needed
            return {
                "should_recharge": should_recharge,
                "suggested_amount_rmb": recharge_amount / 10.0 if should_recharge else 0,
                "urgency": "high" if available < 20 else "medium" if available < 50 else "low",
                "reason": f"可用余额 {available:.1f}kg 低于阈值 {threshold:.1f}kg" if should_recharge else "余额充足"
            }

        # Use AI for more sophisticated analysis
        prompt = f"""You are helping a lobster (AI agent) decide if it should auto-recharge.

Current Status:
- Available Balance: {available} kg
- Recharge Threshold: {threshold} kg
- Pending Tasks: {pending_tasks}
- User's Preferred Recharge Amount: {recharge_amount} kg

Should the lobster trigger auto-recharge now?

Respond in JSON format:
{{
    "should_recharge": true/false,
    "suggested_amount_rmb": number,
    "urgency": "low/medium/high",
    "reason": "explanation in Chinese"
}}"""

        try:
            message = self.client.messages.create(
                model=settings.CLAUDE_MODEL,
                max_tokens=512,
                messages=[{"role": "user", "content": prompt}]
            )

            response_text = message.content[0].text
            start = response_text.find('{')
            end = response_text.rfind('}') + 1

            if start >= 0 and end > start:
                json_str = response_text[start:end]
                return json.loads(json_str)

        except Exception as e:
            print(f"Auto Recharge Decision Error: {e}")

        # Fallback
        return {
            "should_recharge": should_recharge,
            "suggested_amount_rmb": recharge_amount / 10.0 if should_recharge else 0,
            "urgency": "high" if available < 20 else "medium",
            "reason": f"可用余额不足，建议充值"
        }

    async def should_auto_withdraw(
        self,
        current_balance: float,
        frozen_balance: float,
        threshold: float,
        withdrawal_amount: float,
        pending_bids: int
    ) -> dict:
        """
        Decide if auto-withdrawal should be triggered

        Args:
            current_balance: Current balance
            frozen_balance: Frozen balance
            threshold: User's withdrawal threshold
            withdrawal_amount: User's preferred withdrawal amount
            pending_bids: Number of pending bids

        Returns:
            Dict with decision and reasoning
        """

        available = current_balance - frozen_balance

        # Simple rule: withdraw if balance > threshold and enough remains after withdrawal
        should_withdraw = available > threshold and (available - withdrawal_amount) >= 100

        if not self.client or not should_withdraw:
            return {
                "should_withdraw": should_withdraw,
                "suggested_amount_rmb": withdrawal_amount / 10.0 if should_withdraw else 0,
                "remaining_balance": available - withdrawal_amount if should_withdraw else available,
                "reason": f"余额 {available:.1f}kg 超过阈值 {threshold:.1f}kg，可以提现" if should_withdraw else "余额未达提现标准或提现后余额不足"
            }

        # Use AI for more sophisticated analysis
        prompt = f"""You are helping a lobster (AI agent) decide if it should auto-withdraw earnings.

Current Status:
- Available Balance: {available} kg
- Withdrawal Threshold: {threshold} kg
- User's Preferred Withdrawal Amount: {withdrawal_amount} kg
- Pending Bids: {pending_bids}

Should the lobster trigger auto-withdrawal now? Consider:
1. Keeping enough buffer for ongoing activities
2. Optimal cash flow management

Respond in JSON format:
{{
    "should_withdraw": true/false,
    "suggested_amount_rmb": number,
    "remaining_balance": number,
    "reason": "explanation in Chinese"
}}"""

        try:
            message = self.client.messages.create(
                model=settings.CLAUDE_MODEL,
                max_tokens=512,
                messages=[{"role": "user", "content": prompt}]
            )

            response_text = message.content[0].text
            start = response_text.find('{')
            end = response_text.rfind('}') + 1

            if start >= 0 and end > start:
                json_str = response_text[start:end]
                return json.loads(json_str)

        except Exception as e:
            print(f"Auto Withdrawal Decision Error: {e}")

        # Fallback
        return {
            "should_withdraw": should_withdraw,
            "suggested_amount_rmb": withdrawal_amount / 10.0 if should_withdraw else 0,
            "remaining_balance": available - withdrawal_amount if should_withdraw else available,
            "reason": "达到提现条件" if should_withdraw else "暂不建议提现"
        }


ai_service = AIService()
