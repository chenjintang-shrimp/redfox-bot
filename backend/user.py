from backend.database import (
    UserBinding,
    save_user_binding,
    get_user_binding,
    delete_user_binding,
)
from backend.exceptions.user import BindExistError, UserQueryError
from utils.logger import get_logger
from backend.api_client import get_osu_api_client
from utils.strings import get_api_url
from models.context import UserContext


async def get_user_info(user: str | int):
    """
    获取 osu! 用户信息（平台无关）

    Args:
        user: 用户名或用户ID

    Returns:
        用户信息字典
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


async def get_user_binding_by_context(context: UserContext) -> UserBinding | None:
    """
    根据用户上下文获取绑定信息

    Args:
        context: 用户上下文

    Returns:
        UserBinding 或 None
    """
    user_id = int(context.platform_user_id)
    return await get_user_binding(context.platform, user_id)


async def bind_user(context: UserContext, username: str) -> None:
    """
    绑定用户（平台无关）

    Args:
        context: 用户上下文
        username: osu! 用户名

    Raises:
        BindExistError: 用户已绑定
        UserQueryError: 查询 osu! 用户失败
    """
    user_data = await get_user_info(username)
    user_id = int(context.platform_user_id)

    # 检查是否已绑定
    existing = await get_user_binding(context.platform, user_id)
    if existing is not None:
        raise BindExistError(existing.osu_username)

    # 创建新绑定
    new_user = UserBinding(
        id=user_id,
        platform=context.platform,
        osu_id=user_data["id"],
        osu_username=username,
    )
    await save_user_binding(new_user)
    get_logger("backend").info(
        f"Successfully bound {context.platform} user {context.platform_user_id} to osu! user {username}"
    )


async def unbind_user(context: UserContext) -> bool:
    """
    解绑用户（平台无关）

    Args:
        context: 用户上下文

    Returns:
        True if user was unbound, False if no binding existed
    """
    user_id = int(context.platform_user_id)
    deleted = await delete_user_binding(context.platform, user_id)
    if deleted:
        get_logger("backend").info(
            f"Successfully unbound {context.platform} user {context.platform_user_id}"
        )
    else:
        get_logger("backend").info(
            f"No binding found for {context.platform} user {context.platform_user_id}"
        )
    return deleted


async def set_user_gamemode(context: UserContext, gamemode: str | None) -> bool:
    """
    设置用户的默认游戏模式（平台无关）

    Args:
        context: 用户上下文
        gamemode: 游戏模式 (osu/taiko/fruits/mania) 或 None 清除设置

    Returns:
        True if successful, False if user not found
    """
    user_id = int(context.platform_user_id)
    user = await get_user_binding(context.platform, user_id)
    if user is None:
        return False

    user.current_gamemode = gamemode
    await save_user_binding(user)
    get_logger("backend").info(
        f"Set gamemode for {context.platform} user {context.platform_user_id} to {gamemode}"
    )
    return True


async def get_user_gamemode(context: UserContext) -> str | None:
    """
    获取用户的默认游戏模式（平台无关）

    Args:
        context: 用户上下文

    Returns:
        游戏模式 (osu/taiko/fruits/mania) 或 None
    """
    user_id = int(context.platform_user_id)
    user = await get_user_binding(context.platform, user_id)
    if user is None:
        return None
    return user.current_gamemode
