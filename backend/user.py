from backend.database import OsuUser, get_osu_user_by_discord_id, save_osu_user
from utils.logger import get_logger
from utils.strings import format_template
from backend.api_client import api_get


async def get_user_info(user: str):
    """
    Args:
        user: 用户名或用户ID

    Returns:
        格式化的用户信息字符串
    """
    try:
        # 使用新的API调用器
        response = await api_get(f"/api/v2/users/{user}")

        if response.status_code == 404:
            return format_template(
                "USER_QUERY_ERROR_TEMPLATE",
                {"user": user, "error_msg": "User not found"},
            )

        if response.status_code != 200:
            get_logger("backend").error(
                f"API error: {response.status_code} - {response.text}"
            )
            return format_template(
                "USER_QUERY_ERROR_TEMPLATE",
                {"user": user, "error_msg": f"API error: {response.status_code}"},
            )

        return format_template("USER_INFO_TEMPLATE", response.json())

    except Exception as e:
        get_logger("backend").error(f"Error getting user info: {e}")
        return format_template(
            "USER_QUERY_ERROR_TEMPLATE",
            {"user": user, "error_msg": str(e)},
        )


async def bind_user(user_id: int, username: str):
    """
    绑定用户
    Args:
        user_id: 用户在聊天频道中的ID
        username: osu!用户名
    """
    try:
        # 使用新的API调用器获取用户信息
        response = await api_get(f"/api/v2/users/{username}")

        if response.status_code == 404:
            return format_template(
                "USER_QUERY_ERROR_TEMPLATE",
                {"user": username, "error_msg": "User not found"},
            )

        if response.status_code != 200:
            get_logger("backend").error(
                f"API error: {response.status_code} - {response.text}"
            )
            return format_template(
                "USER_QUERY_ERROR_TEMPLATE",
                {"user": username, "error_msg": f"API error: {response.status_code}"},
            )

        user_data = response.json()
        
        current_user = await get_osu_user_by_discord_id(user_id)
        if current_user is not None:
            return format_template(
                "USER_BIND_EXISTING_TEMPLATE",
                {"username": current_user.osu_username},
            )
        else:
            new_user = OsuUser(
                discord_id=user_id,
                osu_id=user_data["id"],
                osu_username=username,
            )
            await save_osu_user(new_user)
            get_logger("backend").info(f"Successfully retrieved user data for {username}")
            return format_template(
                "USER_BIND_SUCCESS_TEMPLATE",
                {"username": username},
            )
    except Exception as e:
        get_logger("backend").error(f"Error binding user: {e}")
        return format_template(
            "USER_QUERY_ERROR_TEMPLATE",
            {"user": username, "error_msg": str(e)},
        )
