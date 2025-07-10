from fastapi import HTTPException, Header
from typing import Optional


async def get_current_user_id(x_user_id: Optional[str] = Header(None)) -> str:
    """
    Extract user_id from request headers.
    This assumes the JWT token is decoded by a middleware/gateway 
    and the user_id is passed in the X-User-ID header.

    NOTE: X-User-ID is a custom header used to pass the user ID.
    This mapping to 'x_user_id' is done automatically by FastAPI.
    X-User-ID is case-insensitive, so it can be sent as 'X-User-ID' or 'x-user-id'.
    """
    if not x_user_id:
        raise HTTPException(
            status_code=401, 
            detail="User authentication required. X-User-ID header missing."
        )
    return x_user_id
