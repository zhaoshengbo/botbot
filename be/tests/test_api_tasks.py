"""
Integration tests for tasks API endpoints
"""
import pytest
from bson import ObjectId


@pytest.mark.integration
@pytest.mark.asyncio
class TestTasksAPI:
    """Test tasks API endpoints"""

    async def test_create_task_success(self, client, auth_headers, test_user):
        """Test POST /api/tasks - create task"""
        task_data = {
            "title": "New Test Task",
            "description": "Task description here",
            "deliverables": "Expected deliverables",
            "budget": 100.0,
            "bidding_period_hours": 24,
            "completion_deadline_hours": 168,
        }

        response = await client.post(
            "/api/tasks",
            json=task_data,
            headers=auth_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == task_data["title"]
        assert data["budget"] == task_data["budget"]
        assert data["status"] == "bidding"
        assert "id" in data

    async def test_create_task_insufficient_balance(
        self, client, auth_headers, test_db, test_user
    ):
        """Test creating task with insufficient balance"""
        # Set balance to low amount
        await test_db.users.update_one(
            {"_id": ObjectId(test_user["id"])},
            {"$set": {"shrimp_food_balance": 5.0}},
        )

        task_data = {
            "title": "Expensive Task",
            "description": "Description",
            "deliverables": "Deliverables",
            "budget": 1000.0,  # More than balance
            "bidding_period_hours": 24,
            "completion_deadline_hours": 168,
        }

        response = await client.post(
            "/api/tasks",
            json=task_data,
            headers=auth_headers,
        )

        assert response.status_code == 400

    async def test_create_task_unauthorized(self, client):
        """Test creating task without authentication"""
        task_data = {
            "title": "Test Task",
            "description": "Description",
            "deliverables": "Deliverables",
            "budget": 50.0,
            "bidding_period_hours": 24,
            "completion_deadline_hours": 168,
        }

        response = await client.post("/api/tasks", json=task_data)

        assert response.status_code == 401

    async def test_get_task(self, client, auth_headers, test_task):
        """Test GET /api/tasks/{task_id}"""
        response = await client.get(
            f"/api/tasks/{test_task['id']}",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_task["id"]
        assert data["title"] == test_task["title"]

    async def test_get_task_not_found(self, client, auth_headers):
        """Test getting non-existent task"""
        fake_id = str(ObjectId())
        response = await client.get(
            f"/api/tasks/{fake_id}",
            headers=auth_headers,
        )

        assert response.status_code == 404

    async def test_list_tasks(self, client, auth_headers, test_task):
        """Test GET /api/tasks - list tasks"""
        response = await client.get(
            "/api/tasks",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert "tasks" in data
        assert "total" in data
        assert len(data["tasks"]) > 0

    async def test_list_tasks_with_filters(self, client, auth_headers, test_task):
        """Test listing tasks with status filter"""
        response = await client.get(
            "/api/tasks?status=bidding",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert "tasks" in data
        # All tasks should have status 'bidding'
        for task in data["tasks"]:
            assert task["status"] == "bidding"

    async def test_update_task(self, client, auth_headers, test_task, test_user):
        """Test PATCH /api/tasks/{task_id}"""
        update_data = {
            "title": "Updated Title",
            "description": "Updated description",
        }

        response = await client.patch(
            f"/api/tasks/{test_task['id']}",
            json=update_data,
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == update_data["title"]
        assert data["description"] == update_data["description"]

    async def test_update_task_not_owner(
        self, client, test_task, test_db
    ):
        """Test updating task by non-owner"""
        # Create another user
        from app.core.security import create_access_token

        other_user = await test_db.users.insert_one(
            {
                "phone_number": "+8613900139999",
                "username": "other_user",
                "shrimp_food_balance": 100.0,
            }
        )
        other_token = create_access_token(
            {"sub": "+8613900139999", "user_id": str(other_user.inserted_id)}
        )
        other_headers = {"Authorization": f"Bearer {other_token}"}

        update_data = {"title": "Hacked Title"}

        response = await client.patch(
            f"/api/tasks/{test_task['id']}",
            json=update_data,
            headers=other_headers,
        )

        assert response.status_code == 403

    async def test_cancel_task(self, client, auth_headers, test_task):
        """Test POST /api/tasks/{task_id}/cancel"""
        response = await client.post(
            f"/api/tasks/{test_task['id']}/cancel",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "cancelled"
