from typing import Dict, Any
import httpx
from utils.variable import API_URL, OAUTH_APP_ID, OAUTH_SECRET, OAUTH_REDIRECT_URI


async def exchange_code_for_token(code: str) -> Dict[str, Any]:
    url = f"{API_URL}/oauth/token"
    payload = {
        "client_id": OAUTH_APP_ID,
        "client_secret": OAUTH_SECRET,
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": OAUTH_REDIRECT_URI,
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, data=payload)
        response.raise_for_status()
        return response.json()


async def get_user_info(access_token: str) -> Dict[str, Any]:
    url = f"{API_URL}/api/v2/me"
    headers = {"Authorization": f"Bearer {access_token}"}

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        response.raise_for_status()
        return response.json()


async def refresh_access_token(refresh_token: str) -> Dict[str, Any]:
    url = f"{API_URL}/oauth/token"
    payload = {
        "client_id": OAUTH_APP_ID,
        "client_secret": OAUTH_SECRET,
        "refresh_token": refresh_token,
        "grant_type": "refresh_token",
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, data=payload)
        response.raise_for_status()
        return response.json()
