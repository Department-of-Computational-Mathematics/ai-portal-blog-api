import requests
from typing import List, Dict, Optional

KEYCLOAK_URL = "http://keycloak:8080"
REALM = "uni"
CLIENT_ID = "backend"  # Change if using a custom client
CLIENT_SECRET = "moYTzhKnzjkOHYIBrjftYkVbOXZQBuir"  # TODO: Set this securely


def get_keycloak_token() -> Optional[str]:
    resp = requests.post(
        f"{KEYCLOAK_URL}/realms/{REALM}/protocol/openid-connect/token",
        data={
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "grant_type": "client_credentials"
        },
        timeout=10
    )
    if resp.status_code == 200:
        return resp.json().get("access_token")
    return None


def get_all_users() -> List[Dict]:
    token = get_keycloak_token()
    if not token:
        return []
    resp = requests.get(
        f"{KEYCLOAK_URL}/admin/realms/{REALM}/users",
        headers={"Authorization": f"Bearer {token}"},
        timeout=10
    )
    if resp.status_code == 200:
        return resp.json()
    return []


def get_user_by_id(user_id: str) -> Optional[Dict]:
    token = get_keycloak_token()
    if not token:
        return None
    resp = requests.get(
        f"{KEYCLOAK_URL}/admin/realms/{REALM}/users/{user_id}",
        headers={"Authorization": f"Bearer {token}"},
        timeout=10
    )
    if resp.status_code == 200:
        return resp.json()
    return None 


# if __name__ == "__main__":
#     print(get_all_users())