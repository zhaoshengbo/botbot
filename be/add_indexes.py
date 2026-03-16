"""
Database Index Creation Script

Run this script to add indexes for bid limits, penalties, and arbitration features.

Usage:
    python add_indexes.py
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings


async def add_indexes():
    """Add database indexes for performance optimization"""
    print("🔍 Connecting to MongoDB...")
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[settings.MONGODB_DB_NAME]

    print("📊 Adding indexes...\n")

    # Tasks collection indexes
    print("1. Creating indexes on 'tasks' collection...")
    await db.tasks.create_index([("status", 1), ("bid_count", 1)])
    print("   ✓ Index: status + bid_count")

    await db.tasks.create_index([("publisher_id", 1), ("status", 1)])
    print("   ✓ Index: publisher_id + status")

    # Bids collection indexes
    print("\n2. Creating indexes on 'bids' collection...")
    await db.bids.create_index([("task_id", 1), ("status", 1)])
    print("   ✓ Index: task_id + status")

    await db.bids.create_index([("bidder_id", 1), ("status", 1)])
    print("   ✓ Index: bidder_id + status")

    # Arbitrations collection indexes
    print("\n3. Creating indexes on 'arbitrations' collection...")
    await db.arbitrations.create_index([("status", 1), ("created_at", -1)])
    print("   ✓ Index: status + created_at (desc)")

    await db.arbitrations.create_index([("contract_id", 1)])
    print("   ✓ Index: contract_id")

    await db.arbitrations.create_index([("assigned_admin_id", 1), ("status", 1)])
    print("   ✓ Index: assigned_admin_id + status")

    await db.arbitrations.create_index([("publisher_id", 1)])
    print("   ✓ Index: publisher_id")

    await db.arbitrations.create_index([("claimer_id", 1)])
    print("   ✓ Index: claimer_id")

    print("\n✅ All indexes created successfully!")

    # List all indexes to verify
    print("\n📋 Current indexes:")
    print("\nTasks collection:")
    indexes = await db.tasks.list_indexes().to_list(None)
    for idx in indexes:
        print(f"   - {idx['name']}: {idx['key']}")

    print("\nBids collection:")
    indexes = await db.bids.list_indexes().to_list(None)
    for idx in indexes:
        print(f"   - {idx['name']}: {idx['key']}")

    print("\nArbitrations collection:")
    indexes = await db.arbitrations.list_indexes().to_list(None)
    for idx in indexes:
        print(f"   - {idx['name']}: {idx['key']}")

    client.close()
    print("\n✨ Done!")


if __name__ == "__main__":
    asyncio.run(add_indexes())
