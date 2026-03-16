"""Migration: Add email field to existing users"""
import asyncio
import sys
import os

# Add parent directory to path to import app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings


async def migrate():
    """Add email field to all existing users"""
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client.get_database()

    print("Starting migration: Adding email field to users...")

    # Add email field to all users that don't have it
    result = await db.users.update_many(
        {"email": {"$exists": False}},
        {"$set": {"email": None}}
    )

    print(f"✅ Migration complete: Updated {result.modified_count} users")
    print(f"   Matched {result.matched_count} users without email field")

    client.close()


if __name__ == "__main__":
    print("=" * 50)
    print("Email Field Migration Script")
    print("=" * 50)
    asyncio.run(migrate())
    print("=" * 50)
