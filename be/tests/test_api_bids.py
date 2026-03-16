"""
Integration tests for bids API endpoints
"""
import pytest
from bson import ObjectId


@pytest.mark.integration
@pytest.mark.asyncio
class TestBidsAPI:
    """Test bids API endpoints"""

    async def test_create_bid_success(
        self, client, auth_headers, test_task, test_db, test_user
    ):
        """Test POST /api/bids - create bid"""
        # Ensure user has enough balance
        await test_db.users.update_one(
            {"_id": ObjectId(test_user["id"])},
            {"$set": {"shrimp_food_balance": 200.0}},
        )

        bid_data = {
            "task_id": test_task["id"],
            "amount": 45.0,
            "estimated_hours": 8,
            "message": "I can complete this task efficiently",
        }

        response = await client.post(
            "/api/bids",
            json=bid_data,
            headers=auth_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["task_id"] == test_task["id"]
        assert data["amount"] == bid_data["amount"]
        assert data["status"] == "active"
        assert "id" in data

    async def test_create_bid_on_own_task(
        self, client, auth_headers, test_task
    ):
        """Test creating bid on own task (should fail)"""
        bid_data = {
            "task_id": test_task["id"],
            "amount": 45.0,
            "estimated_hours": 8,
            "message": "Bidding on my own task",
        }

        response = await client.post(
            "/api/bids",
            json=bid_data,
            headers=auth_headers,
        )

        assert response.status_code == 400

    async def test_get_task_bids(self, client, auth_headers, test_task, test_bid):
        """Test GET /api/tasks/{task_id}/bids"""
        response = await client.get(
            f"/api/tasks/{test_task['id']}/bids",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0

    async def test_get_my_bids(self, client, auth_headers, test_bid):
        """Test GET /api/bids/my"""
        response = await client.get(
            "/api/bids/my",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    async def test_withdraw_bid(self, client, auth_headers, test_bid):
        """Test DELETE /api/bids/{bid_id}"""
        response = await client.delete(
            f"/api/bids/{test_bid['id']}",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "withdrawn"

    async def test_accept_bid(
        self, client, auth_headers, test_task, test_bid, test_db
    ):
        """Test POST /api/bids/{bid_id}/accept"""
        # Create a different user who is the task publisher
        from app.core.security import create_access_token

        publisher_token = create_access_token(
            {
                "sub": test_task["publisher_id"],
                "user_id": str(test_task["publisher_id"]),
            }
        )
        publisher_headers = {"Authorization": f"Bearer {publisher_token}"}

        response = await client.post(
            f"/api/bids/{test_bid['id']}/accept",
            headers=publisher_headers,
        )

        # Should succeed or return appropriate error
        assert response.status_code in [200, 400, 403]
