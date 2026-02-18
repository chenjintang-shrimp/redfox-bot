from services import UserService
from models.context import UserContext
from renderer.renderer_template import renderer
from renderer.service import render_service
from utils.logger import get_logger
from utils.strings import format_template

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
    return format_template("USER_INFO_TEMPLATE", locale=locale, **user_info.__dict__)


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
    logger.info("[render_user_card_image] 开始渲染")

    # 使用新的渲染服务
    result = await render_service.render(
        view_name="user_card",
        data=data,
        skin=skin,
        width=800,
        height=400,
    )

    # 返回图片数据（保持向后兼容）
    if result.content_type == "image":
        return result.data  # type: ignore
    else:
        # 如果返回的是文本，编码为 bytes
        return result.data.encode("utf-8")  # type: ignore


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
    return format_template("USER_INFO_TEMPLATE", locale=locale, **data)
