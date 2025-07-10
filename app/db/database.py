"""
MongoDB database connection and configuration.
"""
from typing import AsyncGenerator
import motor.motor_asyncio
from app.core.config import settings

# Create MongoDB client
client = motor.motor_asyncio.AsyncIOMotorClient(settings.MONGODB_URL)
database = client[settings.MONGODB_DB_NAME]

# Collections
collection_user = database["User"]
collection_blog = database["Blogs"]
collection_comment = database["Comments"]
collection_reply = database["Replies"]
collection_like = database["Likes"]

# Database dependency
async def get_database() -> AsyncGenerator[motor.motor_asyncio.AsyncIOMotorDatabase, None]:
    """
    Get database dependency.
    Yields:
        AsyncIOMotorDatabase: MongoDB database instance
    """
    try:
        yield database
    finally:
        client.close() 