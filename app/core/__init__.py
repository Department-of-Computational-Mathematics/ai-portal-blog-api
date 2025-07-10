"""
Core module containing application configuration and settings.
"""

from app.core.config import settings
from app.core.security import get_current_user_id

__all__ = ["settings", "get_current_user_id"]