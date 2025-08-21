from fastapi import HTTPException
import requests
from typing import List, Dict, Optional
from pprint import pprint

from app.core.config import settings
from app.schemas.blog import KeycloakUser

def get_keycloak_token() -> Optional[str]:
    resp = requests.post(
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
        raise HTTPException(
            status_code=401,
            detail="Unauthorized access - invalid client or credentials for keycloak"
        )


def get_all_users() -> List[KeycloakUser]:
    token = get_keycloak_token()
    if not token:
        raise HTTPException(
            status_code=401,
            detail="Unauthorized access - empty token received from Keycloak"
        )
    resp = requests.get(
        f"{settings.KEYCLOAK_URL}/admin/realms/{settings.REALM}/users",
        headers={"Authorization": f"Bearer {token}"},
        timeout=10,
    )
    if resp.status_code == 200:
        return [KeycloakUser(**user) for user in resp.json()]
    raise HTTPException(
        status_code=500,
        detail=f"Internal Server Error. Keycloak returned a {resp.status_code} - {resp.text} error"
    )


def get_user_by_id(user_id: str) -> KeycloakUser:
    token = get_keycloak_token()
    if not token:
        raise HTTPException(
            status_code=401,
            detail="Unauthorized access - empty token received from Keycloak"
        )
    resp = requests.get(
        f"{settings.KEYCLOAK_URL}/admin/realms/{settings.REALM}/users/{user_id}",
        headers={"Authorization": f"Bearer {token}"},
        timeout=10,
    )
    if resp.status_code == 200:
        data = resp.json()
        return KeycloakUser(**data)
    if resp.status_code == 404:
        raise HTTPException(
            status_code=404,
            detail=f"User not found with ID: {user_id}"
        )
    raise HTTPException(
        status_code=500,
        detail=f"Internal Server Error. Keycloak returned a {resp.status_code} - {resp.text} error"
    )


if __name__ == "__main__":
    pprint(get_all_users())
