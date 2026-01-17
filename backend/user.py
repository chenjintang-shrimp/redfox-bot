from backend.database import OsuUser, get_osu_user_by_discord_id, save_osu_user, delete_osu_user_by_discord_id
from backend.expections.user import BindExistError, UserQueryError
from utils.logger import get_logger
from backend.api_client import get_osu_api_client


async def get_user_info(user: str | int):
    """
    Args:
        user: 用户名或用户ID

    Returns:
        格式化的用户信息字符串
    """
    # 使用新的API调用器
    api_client = get_osu_api_client()

    response = await api_client.get(f"/api/v2/users/{user}")

    if response.status_code == 404:
        raise UserQueryError(
            str(user),
            "User not found",
        )

    if response.status_code != 200:
        get_logger("backend").error(
            f"API error: {response.status_code} - {response.text}"
        )
        raise UserQueryError(
            str(user),
            f"API returned {response.status_code} when requesting endpoint /api/v2/users/{str(user)}",
        )
    return response.json()

async def bind_user(user_id: int, username: str):
    """
    绑定用户
    Args:
        user_id: 用户在聊天频道中的ID
        username: osu!用户名
    """
    # 使用新的API调用器获取用户信息
    api_client = get_osu_api_client()
    response = await api_client.get(f"/api/v2/users/{username}")

    if response.status_code == 404:
        raise UserQueryError(
            username,
            "User not found",
        )

    if response.status_code != 200:
        get_logger("backend").error(
            f"API error: {response.status_code} - {response.text}"
        )
        raise UserQueryError(
            username,
            f"API returned {response.status_code} when requesting endpoint /api/v2/users/{username}",
        )

    user_data = response.json()
    
    current_user = await get_osu_user_by_discord_id(user_id)
    if current_user is not None:
        raise BindExistError(
            current_user.osu_username
        )
    else:
        new_user = OsuUser(
            discord_id=user_id,
            osu_id=user_data["id"],
            osu_username=username,
        )
        await save_osu_user(new_user)
        get_logger("backend").info(f"Successfully retrieved user data for {username}")
        return None


async def unbind_user(discord_id: int) -> bool:
    """
    Unbind user
    Args:
        discord_id: Discord user ID
    Returns:
        True if user was unbound, False if no binding existed
    """
    deleted = await delete_osu_user_by_discord_id(discord_id)
    if deleted:
        get_logger("backend").info(f"Successfully unbound Discord user {discord_id}")
    else:
        get_logger("backend").info(f"No binding found for Discord user {discord_id}")
    return deleted
