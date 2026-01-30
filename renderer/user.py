from backend.user import bind_user, get_user_info, unbind_user
from renderer.renderer_template import renderer
from utils.strings import format_template


@renderer
async def render_user_info(username: str):
    """
    获取用户信息并渲染
    """
    user_info = await get_user_info(username)
    return format_template("USER_INFO_TEMPLATE", user_info)


@renderer
async def render_unbinding_user(discord_id: int):
    """
    解绑用户并渲染结果
    """
    deleted = await unbind_user(discord_id)
    if deleted:
        return format_template("USER_UNBIND_SUCCESS_TEMPLATE")
    else:
        return format_template("USER_NOT_BOUND_TEMPLATE", {"user": "You"})


@renderer
async def render_binding_user(discord_id: int, username: str):
    """
    绑定用户并渲染结果
    """
    await bind_user(discord_id, username)
    return format_template("USER_BIND_SUCCESS_TEMPLATE", {"username": username})
