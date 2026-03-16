"""
Pytest configuration and shared fixtures for testing
"""
import asyncio
import pytest
import pytest_asyncio
from typing import AsyncGenerator, Generator
from httpx import AsyncClient
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId

from app.main import app
from app.core.config import get_settings
from app.core.security import create_access_token, get_password_hash
from app.db.mongodb import get_database


# Configure test settings
settings = get_settings()


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an event loop for the test session"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def test_db() -> AsyncGenerator:
    """Create a test database and clean it up after tests"""
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client.get_database()

    # Clean up before tests
    await db.users.delete_many({})
    await db.tasks.delete_many({})
    await db.bids.delete_many({})
    await db.contracts.delete_many({})
    await db.ratings.delete_many({})
    await db.transactions.delete_many({})
    await db.recharges.delete_many({})
    await db.withdrawals.delete_many({})

    yield db

    # Clean up after tests
    await db.users.delete_many({})
    await db.tasks.delete_many({})
    await db.bids.delete_many({})
    await db.contracts.delete_many({})
    await db.ratings.delete_many({})
    await db.transactions.delete_many({})
    await db.recharges.delete_many({})
    await db.withdrawals.delete_many({})

    client.close()


@pytest_asyncio.fixture(scope="function")
async def client(test_db) -> AsyncGenerator:
    """Create an async HTTP client for testing API endpoints"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest_asyncio.fixture
async def test_user(test_db):
    """Create a test user"""
    user_data = {
        "_id": ObjectId(),
        "phone_number": "+8613800138000",
        "username": "test_user",
        "level": "bronze",
        "shrimp_food_balance": 100.0,
        "frozen_balance": 0.0,
        "total_earned": 0.0,
        "total_spent": 0.0,
        "tasks_published": 0,
        "tasks_completed": 0,
        "rating_as_publisher": 5.0,
        "rating_as_claimer": 5.0,
        "rating_count_as_publisher": 0,
        "rating_count_as_claimer": 0,
        "ai_preferences": {
            "auto_bid_enabled": False,
            "auto_bid_max_amount": 50.0,
            "auto_recharge_enabled": False,
            "auto_recharge_threshold": 20.0,
            "auto_recharge_amount": 100.0,
            "auto_withdraw_enabled": False,
            "auto_withdraw_threshold": 500.0,
            "auto_withdraw_amount": 300.0,
        },
        "is_active": True,
        "is_admin": False,
    }

    result = await test_db.users.insert_one(user_data)
    user_data["id"] = str(result.inserted_id)
    return user_data


@pytest_asyncio.fixture
async def test_admin(test_db):
    """Create a test admin user"""
    admin_data = {
        "_id": ObjectId(),
        "phone_number": "+8613900139000",
        "username": "test_admin",
        "level": "diamond",
        "shrimp_food_balance": 1000.0,
        "frozen_balance": 0.0,
        "total_earned": 5000.0,
        "total_spent": 1000.0,
        "tasks_published": 50,
        "tasks_completed": 100,
        "rating_as_publisher": 4.8,
        "rating_as_claimer": 4.9,
        "rating_count_as_publisher": 45,
        "rating_count_as_claimer": 95,
        "ai_preferences": {},
        "is_active": True,
        "is_admin": True,
    }

    result = await test_db.users.insert_one(admin_data)
    admin_data["id"] = str(result.inserted_id)
    return admin_data


@pytest.fixture
def auth_token(test_user) -> str:
    """Create a valid JWT token for test user"""
    token = create_access_token(
        data={"sub": test_user["phone_number"], "user_id": test_user["id"]}
    )
    return token


@pytest.fixture
def admin_token(test_admin) -> str:
    """Create a valid JWT token for admin user"""
    token = create_access_token(
        data={"sub": test_admin["phone_number"], "user_id": test_admin["id"]}
    )
    return token


@pytest.fixture
def auth_headers(auth_token) -> dict:
    """Create authorization headers with test user token"""
    return {"Authorization": f"Bearer {auth_token}"}


@pytest.fixture
def admin_headers(admin_token) -> dict:
    """Create authorization headers with admin token"""
    return {"Authorization": f"Bearer {admin_token}"}


@pytest_asyncio.fixture
async def test_task(test_db, test_user):
    """Create a test task"""
    from datetime import datetime, timedelta

    task_data = {
        "_id": ObjectId(),
        "title": "Test Task",
        "description": "This is a test task description",
        "deliverables": "Test deliverables",
        "budget": 50.0,
        "publisher_id": ObjectId(test_user["id"]),
        "publisher_username": test_user["username"],
        "status": "bidding",
        "bid_count": 0,
        "bidding_deadline": datetime.utcnow() + timedelta(hours=24),
        "completion_deadline": datetime.utcnow() + timedelta(days=7),
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }

    result = await test_db.tasks.insert_one(task_data)
    task_data["id"] = str(result.inserted_id)
    return task_data


@pytest_asyncio.fixture
async def test_bid(test_db, test_task, test_user):
    """Create a test bid"""
    from datetime import datetime

    bid_data = {
        "_id": ObjectId(),
        "task_id": ObjectId(test_task["id"]),
        "bidder_id": ObjectId(test_user["id"]),
        "bidder_username": test_user["username"],
        "amount": 45.0,
        "estimated_hours": 8,
        "message": "I can complete this task",
        "ai_analysis": {
            "feasibility_score": 0.85,
            "confidence": "high",
            "reasoning": "Task matches skill set",
        },
        "status": "active",
        "created_at": datetime.utcnow(),
    }

    result = await test_db.bids.insert_one(bid_data)
    bid_data["id"] = str(result.inserted_id)
    return bid_data


@pytest_asyncio.fixture
async def mock_ai_response():
    """Mock AI service response"""
    return {
        "feasibility_score": 0.8,
        "confidence": "high",
        "suggested_bid_amount": 45.0,
        "estimated_hours": 8,
        "reasoning": "Task is well within capabilities",
        "recommendation": "proceed",
    }
