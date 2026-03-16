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

    # Initialize super admin if configured
    if settings.SUPER_ADMIN_PHONE:
        await mongodb.db.users.update_one(
            {"phone_number": settings.SUPER_ADMIN_PHONE},
            {"$set": {"role": "admin"}},
            upsert=False
        )
        print(f"Super admin initialized: {settings.SUPER_ADMIN_PHONE}")

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
    await db.users.create_index("role")

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

    # Recharge orders indexes
    await db.recharge_orders.create_index("order_no", unique=True)
    await db.recharge_orders.create_index([("user_id", 1), ("created_at", -1)])
    await db.recharge_orders.create_index([("payment_status", 1), ("created_at", -1)])
    await db.recharge_orders.create_index("payment_channel_order_no")

    # Withdrawal orders indexes
    await db.withdrawal_orders.create_index("order_no", unique=True)
    await db.withdrawal_orders.create_index([("user_id", 1), ("created_at", -1)])
    await db.withdrawal_orders.create_index([("status", 1), ("created_at", -1)])

    # Transaction logs indexes
    await db.transaction_logs.create_index([("user_id", 1), ("created_at", -1)])
    await db.transaction_logs.create_index([("transaction_type", 1), ("created_at", -1)])
    await db.transaction_logs.create_index("related_order_id")

    # Platform withdrawal orders indexes
    await db.platform_withdrawal_orders.create_index("order_no", unique=True)
    await db.platform_withdrawal_orders.create_index([("status", 1), ("created_at", -1)])
    await db.platform_withdrawal_orders.create_index("created_by")

    # Admin operation logs indexes
    await db.admin_operation_logs.create_index([("operator_id", 1), ("timestamp", -1)])
    await db.admin_operation_logs.create_index([("target_user_id", 1), ("timestamp", -1)])


def get_database() -> AsyncIOMotorDatabase:
    """Get database instance"""
    return mongodb.db
