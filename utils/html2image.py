"""
HTML 转图片工具 - 纯函数式

使用方式:
    # 初始化（应用启动时）
    playwright = await async_playwright().start()
    browser = await playwright.chromium.launch()
    
    # 多次转换（复用 browser）
    image = await html_to_image(browser, html)
    image = await html_to_image(browser, html)
    
    # 关闭（应用关闭时）
    await browser.close()
    await playwright.stop()
"""

from typing import TYPE_CHECKING

from utils.logger import get_logger

if TYPE_CHECKING:
    from playwright.async_api import Browser

logger = get_logger("utils.html2image")


async def html_to_image(
    browser: "Browser",
    html: str,
    width: int = 800,
    height: int = 400,
) -> bytes:
    """
    将 HTML 转换为 PNG 图片

    Args:
        browser: Playwright Browser 实例（外部传入，复用）
        html: HTML 字符串
        width: 图片宽度
        height: 图片高度

    Returns:
        PNG 图片字节
    """
    page = await browser.new_page(viewport={"width": width, "height": height})

    try:
        await page.set_content(html)
        screenshot = await page.screenshot(type="png", full_page=False)
        return screenshot
    finally:
        await page.close()
