from fastapi import HTTPException
import httpx
from typing import List, Dict, Optional
from pprint import pprint

from app.core.config import settings
from app.schemas.blog import KeycloakUser
from app.core.exceptions import *

async def get_keycloak_token() -> Optional[str]:
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{settings.KEYCLOAK_URL}/realms/{settings.REALM}/protocol/openid-connect/token",
            data={
                "client_id": settings.CLIENT_ID,
                "client_secret": settings.CLIENT_SECRET,
                "grant_type": "client_credentials",
            },
            timeout=10,
        )
        if resp.status_code == 200:
            return resp.json().get("access_token")
        if resp.status_code == 401:
            raise KeycloakAuthenticationException()
        return None


async def get_all_users() -> List[KeycloakUser]:
    token = await get_keycloak_token()
    if not token:
        raise KeycloakTokenException()
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{settings.KEYCLOAK_URL}/admin/realms/{settings.REALM}/users",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10,
        )
        if resp.status_code == 200:
            return [KeycloakUser(**user) for user in resp.json()]
        raise KeycloakServiceException(resp.status_code, resp.text)


async def get_user_by_id(user_id: str) -> KeycloakUser:
    token = await get_keycloak_token()
    if not token:
        raise KeycloakTokenException()
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{settings.KEYCLOAK_URL}/admin/realms/{settings.REALM}/users/{user_id}",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10,
        )
        if resp.status_code == 200:
            data = resp.json()
            return KeycloakUser(**data)
        if resp.status_code == 404:
            raise KeycloakUserNotFoundException(user_id)
        raise InternalServerException

async def get_all_users_safely() -> List[KeycloakUser]:
    """Fetch all users from Keycloak safely. No HTTPException is raised.

    Returns:
        list[KeycloakUser]: A list of KeycloakUser objects or an empty list if an error occurs.
    """
    try:
        return await get_all_users()
    except HTTPException as e:
        print(f"\nError fetching users from keycloak:\n{e}\n")
        return []

async def get_user_by_id_safely(user_id: str, *, default_username: str = "", default_profile_pic_url: str = "", default_first_name: str = "", default_last_name: str = "") -> KeycloakUser:
    """Fetch a user by ID from Keycloak safely. No HTTPException is raised.

    Args:
        user_id (str): The ID of the user to fetch.
        default_username (str, optional): The default username to return if the user is not found. Defaults to "".
        default_profile_pic_url (str, optional): The default profile picture URL to return if the user is not found. Defaults to "".

    Returns:
        KeycloakUser: A KeycloakUser object or a user with default values if not found.
    """
    try:
        return await get_user_by_id(user_id)
    except HTTPException as e:
        print(f"\nError fetching user {user_id} from keycloak:\n{e}\n")
        # Provide in the exact format as the Keycloak response
        return KeycloakUser(**{
            "username": default_username,
            "attributes": {
                "profilePicUrl": [default_profile_pic_url]
            },
            "firstName": default_first_name,
            "lastName": default_last_name
        })

async def check_keycloak_health() -> Dict:
    """
    Check Keycloak service health by attempting to get a token.
    Returns health status with response time and additional metrics.
    """
    import time
    
    try:
        start_time = time.time()
        token = await get_keycloak_token()
        response_time = round((time.time() - start_time) * 1000, 2)  # Convert to milliseconds
        
        if token:
            return {
                "status": "healthy",
                "response_time_ms": response_time,
                "authenticated": True,
                "service": "keycloak"
            }
        else:
            return {
                "status": "unhealthy",
                "response_time_ms": response_time,
                "authenticated": False,
                "service": "keycloak",
                "error": "Failed to obtain token"
            }
    except Exception as e:
        return {
            "status": "unhealthy",
            "response_time_ms": None,
            "authenticated": False,
            "service": "keycloak",
            "error": str(e)
        }

if __name__ == "__main__":
    import asyncio
    async def main():
        users = await get_all_users()
        pprint(users)
    asyncio.run(main())
