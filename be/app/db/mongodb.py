"""MongoDB Database Connection"""
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.core.config import settings


class MongoDB:
    """MongoDB connection manager"""

    client: AsyncIOMotorClient = None
    db: AsyncIOMotorDatabase = None


mongodb = MongoDB()


async def connect_to_mongo():
    """Connect to MongoDB"""
    mongodb.client = AsyncIOMotorClient(settings.MONGODB_URL)
    mongodb.db = mongodb.client[settings.MONGODB_DB_NAME]

    # Create indexes
    await create_indexes()

    print(f"Connected to MongoDB: {settings.MONGODB_DB_NAME}")


async def close_mongo_connection():
    """Close MongoDB connection"""
    if mongodb.client:
        mongodb.client.close()
        print("Closed MongoDB connection")


async def create_indexes():
    """Create database indexes"""
    db = mongodb.db

    # Users collection indexes
    await db.users.create_index("phone_number", unique=True)
    await db.users.create_index("username")
    await db.users.create_index("level")

    # Tasks collection indexes
    await db.tasks.create_index("publisher_id")
    await db.tasks.create_index("status")
    await db.tasks.create_index("created_at")
    await db.tasks.create_index([("status", 1), ("created_at", -1)])

    # Bids collection indexes
    await db.bids.create_index("task_id")
    await db.bids.create_index("bidder_id")
    await db.bids.create_index([("task_id", 1), ("status", 1)])
    await db.bids.create_index([("bidder_id", 1), ("status", 1)])

    # Contracts collection indexes
    await db.contracts.create_index("task_id", unique=True)
    await db.contracts.create_index("publisher_id")
    await db.contracts.create_index("claimer_id")
    await db.contracts.create_index("status")

    # Ratings collection indexes
    await db.ratings.create_index("contract_id")
    await db.ratings.create_index("ratee_id")
    await db.ratings.create_index([("ratee_id", 1), ("rating_type", 1)])


def get_database() -> AsyncIOMotorDatabase:
    """Get database instance"""
    return mongodb.db
