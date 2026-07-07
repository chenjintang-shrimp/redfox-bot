from dataclasses import asdict

from services import UserService
from models.context import UserContext
from renderer.renderer_template import renderer
from renderer.skin_loader import render_template as render_skin_template
from utils.flt_mgr import apply_minifilters_async
from utils.html2image import html_to_image
from utils.logger import get_logger
from utils.strings import format_template
from utils.variable import DEFAULT_SKIN

logger = get_logger("renderer.user")


# ============ 原有的文字渲染 API ============


@renderer
async def render_user_info(username: str, locale: str = "en") -> str:
    """
    获取用户信息（文字版）

    Args:
        username: osu!用户名
        locale: 语言代码，默认"en"

    Returns:
        用户信息字符串
    """
    user_info = await UserService.get_user_info(username)
    return format_template("USER_INFO_TEMPLATE", context=asdict(user_info), locale=locale)


@renderer
async def render_unbinding_user(context: UserContext, locale: str = "en") -> str:
    """
    解绑用户

    Args:
        context: 用户上下文
        locale: 语言代码，默认"en"

    Returns:
        解绑结果字符串
    """
    deleted = await UserService.unbind_user(context)
    if deleted:
        return format_template("USER_UNBIND_SUCCESS_TEMPLATE", locale=locale)
    else:
        return format_template("USER_NOT_BOUND_TEMPLATE", locale=locale, user="You")


@renderer
async def render_binding_user(
    context: UserContext, username: str, locale: str = "en"
) -> str:
    """
    绑定用户

    Args:
        context: 用户上下文
        username: osu!用户名
        locale: 语言代码，默认"en"

    Returns:
        绑定结果字符串
    """
    user_info = await UserService.bind_user(context, username)
    return format_template(
        "USER_BIND_SUCCESS_TEMPLATE", locale=locale, username=user_info.username
    )


# ============ 新的图片渲染 API ============


@renderer("user_card")
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

    # 应用 minifilters 处理数据（按 renderer 视图名 hook）
    processed_data = await apply_minifilters_async("user_card", data)

    # 渲染 HTML 模板
    html = await render_skin_template(skin, "user_card", processed_data)
    logger.debug(f"[render_user_card_image] HTML 长度: {len(html)} chars")

    # 转换为图片
    image_bytes = await html_to_image(html, width=800, height=None)
    logger.info(
        f"[render_user_card_image] 图片生成完成，大小: {len(image_bytes)} bytes"
    )

    return image_bytes


def render_user_card_text(data: dict, locale: str = "en") -> str:
    """
    渲染用户卡片为文字（使用原有模板）

    注意：此函数不使用 @renderer 装饰器，也不应用 minifilter

    Args:
        data: API 返回的用户数据
        locale: 语言代码，默认"en"

    Returns:
        格式化的文本字符串
    """
    return format_template("USER_INFO_TEMPLATE", context=data, locale=locale)
