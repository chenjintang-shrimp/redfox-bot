from backend.expections.user import BindExistError, UserQueryError
from backend.user import bind_user, get_user_info, unbind_user
from frontend.discord.util import UserNotBindError
from utils.strings import format_template


async def render_user_info(username: str):
    """
    获取用户信息
    Args:
        username: osu!用户名
    Returns:
        用户信息字符串
    """
    try:
        user_info = await get_user_info(username)
        return format_template("USER_INFO_TEMPLATE", user_info)
    except UserQueryError as e:
        return format_template(
            "USER_QUERY_ERROR_TEMPLATE",
            {"error_msg": e.error_msg},
        )
    except Exception as e:
        return format_template(
            "RENDERER_ERROR_TEMPLATE",
            {"error_msg": str(e)},
        )


async def render_unbinding_user(discord_id: int):
    """
    Render unbinding user result
    Args:
        discord_id: Discord user ID
    Returns:
        Unbinding result string
    """
    try:
        deleted = await unbind_user(discord_id)
        if deleted:
            return format_template(
                "USER_UNBIND_SUCCESS_TEMPLATE",
                {},
            )
        else:
            return format_template(
                "USER_NOT_BOUND_TEMPLATE",
                {"user": "You"},
            )
    except Exception as e:
        return format_template(
            "RENDERER_ERROR_TEMPLATE",
            {"error_msg": str(e)},
        )


async def render_binding_user(discord_id: int, username: str):
    """
    获取绑定用户信息
    Args:
        discord_id: Discord用户ID
        username: osu!用户名
    Returns:
        绑定用户信息字符串
    """
    try:
        await bind_user(discord_id, username)
        return format_template(
            "USER_BIND_SUCCESS_TEMPLATE",
            {"username": username},
        )
    except BindExistError as e:
        return format_template(
            "USER_BIND_EXISTING_TEMPLATE",
            {"username": e.username},
        )
    except UserQueryError as e:
        return format_template(
            "USER_QUERY_ERROR_TEMPLATE",
            {"error_msg": e.error_msg},
        )
    except UserNotBindError as e:
        return format_template(
            "USER_NOT_BOUND_TEMPLATE",
            {"user": e},
        )
    except Exception as e:
        return format_template(
            "RENDERER_ERROR_TEMPLATE",
            {"error_msg": str(e)},
        )
