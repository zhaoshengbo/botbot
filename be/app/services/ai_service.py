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

Please analyze:
1. Can this lobster realistically complete this task? Consider the technical requirements and complexity.
2. How many hours would it likely take?
3. What should be the bid amount? (Should not exceed the budget)
4. What is your confidence level in this assessment? (0-1)
5. Provide clear reasoning for your decision.

Respond in JSON format:
{{
    "can_complete": true/false,
    "feasibility_score": 0.0-1.0,
    "estimated_hours": number,
    "suggested_bid_amount": number or null,
    "confidence": 0.0-1.0,
    "reasoning": "detailed explanation"
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
            reasoning = f"This task appears feasible. Based on the requirements, I estimate it will take approximately {random.randint(2, 10)} hours. The suggested bid of {suggested_bid:.1f}kg is competitive while ensuring fair compensation."
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


ai_service = AIService()
