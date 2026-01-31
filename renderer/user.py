from backend.user import bind_user, get_user_info, unbind_user
from renderer.renderer_template import renderer
from renderer.skin_loader import render_template as render_skin_template
from utils.html2image import html_to_image
from utils.logger import get_logger
from utils.strings import format_template
from utils.variable import DEFAULT_SKIN

logger = get_logger("renderer.user")


# ============ 原有的文字渲染 API ============


@renderer
async def render_user_info(username: str) -> str:
    """
    获取用户信息（文字版）

    Args:
        username: osu!用户名

    Returns:
        用户信息字符串
    """
    user_info = await get_user_info(username)
    return format_template("USER_INFO_TEMPLATE", user_info)


@renderer
async def render_unbinding_user(discord_id: int) -> str:
    """
    解绑用户

    Args:
        discord_id: Discord user ID

    Returns:
        解绑结果字符串
    """
    deleted = await unbind_user(discord_id)
    if deleted:
        return format_template("USER_UNBIND_SUCCESS_TEMPLATE", {})
    else:
        return format_template("USER_NOT_BOUND_TEMPLATE", {"user": "You"})


@renderer
async def render_binding_user(discord_id: int, username: str) -> str:
    """
    绑定用户

    Args:
        discord_id: Discord用户ID
        username: osu!用户名

    Returns:
        绑定结果字符串
    """
    await bind_user(discord_id, username)
    return format_template("USER_BIND_SUCCESS_TEMPLATE", {"username": username})


# ============ 新的图片渲染 API ============


@renderer
async def render_user_card_image(
    data: dict,
    skin: str | None = None,
) -> bytes:
    """
    渲染用户卡片为图片

    Args:
        data: API 返回的用户数据
        skin: 皮肤名称，默认使用全局配置

    Returns:
        PNG 图片字节
    """
    skin = skin or DEFAULT_SKIN
    logger.info(f"[render_user_card_image] 开始渲染，skin={skin}")

    # 1. 渲染 HTML 模板（内部会应用 minifilters）
    html = await render_skin_template(skin, "user_card", data)
    logger.debug(f"[render_user_card_image] HTML 长度: {len(html)} chars")

    # 3. 转换为图片
    image_bytes = await html_to_image(html, width=800, height=400)
    logger.info(
        f"[render_user_card_image] 图片生成完成，大小: {len(image_bytes)} bytes"
    )

    return image_bytes


def render_user_card_text(data: dict) -> str:
    """
    渲染用户卡片为文字（使用原有模板）

    注意：此函数不使用 @renderer 装饰器，也不应用 minifilter

    Args:
        data: API 返回的用户数据

    Returns:
        格式化的文本字符串
    """
    return format_template("USER_INFO_TEMPLATE", data)
