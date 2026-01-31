from typing import TYPE_CHECKING

from minifilters import apply_minifilter
from renderer.skin_loader import render_template
from utils.html2image import html_to_image

if TYPE_CHECKING:
    from playwright.async_api import Browser


async def render_user_card(
    browser: "Browser",
    data: dict,
    skin: str = "default",
) -> bytes:
    """
    渲染用户卡片为图片

    Args:
        browser: Playwright Browser 实例（外部传入，复用）
        data: API 返回的用户数据
        skin: 皮肤名称，默认 "default"

    Returns:
        PNG 图片字节
    """
    # 1. 应用 minifilter（如果有）
    processed = apply_minifilter("user_card", data)

    # 2. 渲染 HTML 模板
    html = render_template(skin, "user_card", processed)

    # 3. 转换为图片
    return await html_to_image(browser, html, width=800, height=400)
