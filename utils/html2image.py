"""
HTML 转图片工具 - 全局共享 Browser 实例

使用方式:
    # 应用启动时初始化
    await init_browser()
    
    # 任意地方调用（自动使用全局 browser）
    image = await html_to_image(html)
    
    # 应用关闭时清理
    await close_browser()
"""

from typing import TYPE_CHECKING

from utils.logger import get_logger

if TYPE_CHECKING:
    from playwright.async_api import Browser, Playwright

logger = get_logger("utils.html2image")

# 全局实例
_playwright: "Playwright | None" = None
_browser: "Browser | None" = None


async def init_browser() -> None:
    """初始化全局 Browser 实例"""
    global _playwright, _browser

    if _browser is not None:
        return

    from playwright.async_api import async_playwright

    _playwright = await async_playwright().start()
    _browser = await _playwright.chromium.launch()
    logger.info("Browser 已初始化")


async def close_browser() -> None:
    """关闭全局 Browser 实例"""
    global _playwright, _browser

    if _browser is not None:
        await _browser.close()
        _browser = None
        logger.info("Browser 已关闭")

    if _playwright is not None:
        await _playwright.stop()
        _playwright = None
        logger.info("Playwright 已停止")


async def html_to_image(
    html: str,
    width: int = 800,
    height: int = 400,
) -> bytes:
    """
    将 HTML 转换为 PNG 图片

    使用全局 Browser 实例

    Args:
        html: HTML 字符串
        width: 图片宽度
        height: 图片高度

    Returns:
        PNG 图片字节
    """
    if _browser is None:
        raise RuntimeError("Browser 未初始化，请先调用 init_browser()")

    logger.info(f"[html2image] 创建新页面 {width}x{height}")
    page = await _browser.new_page(viewport={"width": width, "height": height})

    try:
        logger.info("[html2image] 设置 HTML 内容")
        await page.set_content(html)
        logger.info("[html2image] 开始截图")
        screenshot = await page.screenshot(type="png", full_page=False)
        logger.info(f"[html2image] 截图完成，大小: {len(screenshot)} bytes")
        return screenshot
    except Exception as e:
        logger.error(f"[html2image] 截图失败: {e}", exc_info=True)
        raise
    finally:
        await page.close()
        logger.info("[html2image] 页面已关闭")
