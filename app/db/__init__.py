"""
Database module for MongoDB integration.
"""
from app.db.database import (
    get_database,
    collection_blog,
    collection_user,
    collection_comment,
    collection_reply,
)

__all__ = [
    "get_database",
    "collection_blog",
    "collection_user",
    "collection_comment",
    "collection_reply",
] 