"""
Integration tests for AI API endpoints
"""
import pytest
from unittest.mock import AsyncMock, patch


@pytest.mark.integration
@pytest.mark.asyncio
class TestAIAPI:
    """Test AI service API endpoints"""

    async def test_analyze_task(self, client, auth_headers, test_task):
        """Test POST /api/ai/analyze-task"""
        with patch("app.services.ai_service.AIService.analyze_task") as mock_analyze:
            mock_analyze.return_value = {
                "feasibility_score": 0.85,
                "confidence": "high",
                "suggested_bid_amount": 45.0,
                "estimated_hours": 8,
                "reasoning": "Task is within capabilities",
                "recommendation": "proceed",
            }

            response = await client.post(
                "/api/ai/analyze-task",
                json={"task_id": test_task["id"]},
                headers=auth_headers,
            )

            assert response.status_code == 200
            data = response.json()
            assert "feasibility_score" in data
            assert "suggested_bid_amount" in data
            assert "recommendation" in data

    async def test_analyze_task_not_found(self, client, auth_headers):
        """Test analyzing non-existent task"""
        from bson import ObjectId

        fake_id = str(ObjectId())

        with patch("app.services.ai_service.AIService.analyze_task") as mock_analyze:
            mock_analyze.side_effect = Exception("Task not found")

            response = await client.post(
                "/api/ai/analyze-task",
                json={"task_id": fake_id},
                headers=auth_headers,
            )

            assert response.status_code in [404, 500]

    async def test_balance_analysis(self, client, auth_headers, test_user):
        """Test POST /api/ai/balance-analysis"""
        with patch(
            "app.services.ai_service.AIService.analyze_balance"
        ) as mock_analyze:
            mock_analyze.return_value = {
                "current_balance": test_user["shrimp_food_balance"],
                "status": "healthy",
                "recommendation": "Balance is adequate",
                "should_recharge": False,
            }

            response = await client.post(
                "/api/ai/balance-analysis",
                headers=auth_headers,
            )

            assert response.status_code == 200
            data = response.json()
            assert "current_balance" in data
            assert "status" in data
            assert "recommendation" in data

    async def test_earnings_analysis(self, client, auth_headers):
        """Test POST /api/ai/earnings-analysis"""
        with patch(
            "app.services.ai_service.AIService.analyze_earnings"
        ) as mock_analyze:
            mock_analyze.return_value = {
                "total_earned": 500.0,
                "performance_grade": "B",
                "recommendation": "Good performance",
            }

            response = await client.post(
                "/api/ai/earnings-analysis",
                headers=auth_headers,
            )

            assert response.status_code == 200
            data = response.json()
            assert "total_earned" in data
            assert "recommendation" in data

    async def test_auto_bid(self, client, auth_headers, test_task, test_db, test_user):
        """Test POST /api/ai/auto-bid"""
        # Enable auto-bid for user
        from bson import ObjectId

        await test_db.users.update_one(
            {"_id": ObjectId(test_user["id"])},
            {
                "$set": {
                    "ai_preferences.auto_bid_enabled": True,
                    "ai_preferences.auto_bid_max_amount": 100.0,
                }
            },
        )

        with patch("app.services.ai_service.AIService.auto_bid") as mock_auto_bid:
            mock_auto_bid.return_value = {
                "success": True,
                "bids_placed": 1,
                "tasks_evaluated": 3,
            }

            response = await client.post(
                "/api/ai/auto-bid",
                headers=auth_headers,
            )

            assert response.status_code == 200
            data = response.json()
            assert "success" in data

    async def test_auto_recharge(self, client, auth_headers, test_user, test_db):
        """Test POST /api/ai/auto-recharge"""
        # Set low balance to trigger recharge
        from bson import ObjectId

        await test_db.users.update_one(
            {"_id": ObjectId(test_user["id"])},
            {
                "$set": {
                    "shrimp_food_balance": 10.0,
                    "ai_preferences.auto_recharge_enabled": True,
                    "ai_preferences.auto_recharge_threshold": 20.0,
                    "ai_preferences.auto_recharge_amount": 100.0,
                }
            },
        )

        with patch(
            "app.services.ai_service.AIService.auto_recharge"
        ) as mock_recharge:
            mock_recharge.return_value = {
                "should_recharge": True,
                "recharge_initiated": True,
                "order_id": "test_order_123",
            }

            response = await client.post(
                "/api/ai/auto-recharge",
                headers=auth_headers,
            )

            assert response.status_code == 200
            data = response.json()
            assert "should_recharge" in data

    async def test_update_preferences(self, client, auth_headers):
        """Test PATCH /api/ai/preferences"""
        preferences = {
            "auto_bid_enabled": True,
            "auto_bid_max_amount": 80.0,
            "auto_recharge_enabled": False,
        }

        response = await client.patch(
            "/api/ai/preferences",
            json=preferences,
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["auto_bid_enabled"] is True
        assert data["auto_bid_max_amount"] == 80.0
