from backend.database import (
    UserBinding,
    Platform,
    save_user_binding,
    get_osu_user_by_qq_id,
    delete_osu_user_by_qq_id,
)
from backend.exceptions.user import BindExistError, UserQueryError
from utils.logger import get_logger
from backend.api_client import get_osu_api_client
from utils.strings import get_api_url


async def get_user_info(user: str | int):
    """
    Args:
        user: 用户名或用户ID

    Returns:
        格式化的用户信息字符串
    """
    api_client = get_osu_api_client()

    url = get_api_url("user_info", user_id=user)

    response = await api_client.get(url)

    if response.status_code == 404:
        raise UserQueryError(
            str(user),
            "User not found",
            response.status_code,
        )

    if response.status_code != 200:
        get_logger("backend").error(
            f"API error: {response.status_code} - {response.text}"
        )
        raise UserQueryError(
            str(user),
            f"API returned {response.status_code} when requesting endpoint {url}",
            response.status_code,
        )
    return response.json()


async def bind_user_qq(qq_id: int, username: str):
    """
    绑定QQ用户
    Args:
        qq_id: QQ号
        username: osu!用户名
    """
    user_data = await get_user_info(username)

    current_user = await get_osu_user_by_qq_id(qq_id)
    if current_user is not None:
        raise BindExistError(current_user.osu_username)
    else:
        new_user = UserBinding(
            id=qq_id,
            platform=Platform.QQ,
            osu_id=user_data["id"],
            osu_username=username,
        )
        await save_user_binding(new_user)
        get_logger("backend").info(f"Successfully bound QQ {qq_id} to osu! user {username}")
        return None


async def unbind_user_qq(qq_id: int) -> bool:
    """
    解绑QQ用户
    Args:
        qq_id: QQ号
    Returns:
        True if user was unbound, False if no binding existed
    """
    deleted = await delete_osu_user_by_qq_id(qq_id)
    if deleted:
        get_logger("backend").info(f"Successfully unbound QQ user {qq_id}")
    else:
        get_logger("backend").info(f"No binding found for QQ user {qq_id}")
    return deleted


async def set_user_gamemode_qq(qq_id: int, gamemode: str | None) -> bool:
    """
    设置QQ用户的默认游戏模式
    Args:
        qq_id: QQ号
        gamemode: 游戏模式 (osu/taiko/fruits/mania) 或 None 清除设置
    Returns:
        True if successful, False if user not found
    """
    user = await get_osu_user_by_qq_id(qq_id)
    if user is None:
        return False

    user.current_gamemode = gamemode
    await save_user_binding(user)
    get_logger("backend").info(f"Set gamemode for QQ user {qq_id} to {gamemode}")
    return True


async def get_user_gamemode_qq(qq_id: int) -> str | None:
    """
    获取QQ用户的默认游戏模式
    Args:
        qq_id: QQ号
    Returns:
        游戏模式 (osu/taiko/fruits/mania) 或 None
    """
    user = await get_osu_user_by_qq_id(qq_id)
    if user is None:
        return None
    return user.current_gamemode
