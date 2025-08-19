import requests
from typing import List, Dict, Optional
from pprint import pprint

from app.core.config import settings


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
    return None


def get_all_users() -> List[Dict]:
    token = get_keycloak_token()
    if not token:
        return []
    resp = requests.get(
        f"{settings.KEYCLOAK_URL}/admin/realms/{settings.REALM}/users",
        headers={"Authorization": f"Bearer {token}"},
        timeout=10,
    )
    if resp.status_code == 200:
        return resp.json()
    return []


def get_user_by_id(user_id: str) -> Optional[Dict]:
    token = get_keycloak_token()
    if not token:
        return None
    resp = requests.get(
        f"{settings.KEYCLOAK_URL}/admin/realms/{settings.REALM}/users/{user_id}",
        headers={"Authorization": f"Bearer {token}"},
        timeout=10,
    )
    if resp.status_code == 200:
        return resp.json()
    return None


if __name__ == "__main__":
    pprint(get_all_users())
