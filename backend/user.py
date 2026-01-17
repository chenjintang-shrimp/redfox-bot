from utils.logger import get_logger
from utils.strings import format_template
from utils.variable import API_URL
from httpx import AsyncClient


async def get_user_info(user: str):
    async with AsyncClient() as client:
        url = API_URL + f"/api/v2/users/{user}"
        res = await client.get(url)
        get_logger("backend").info(f"Request api {url} get Response {res.status_code}")
        if res.status_code == 404:
            return format_template(
                "USER_QUERY_ERROR_TEMPLATE",
                {"user": user, "error_msg": "User not found"},
            )
        return format_template("USER_INFO_TEMPLATE", res.json())
