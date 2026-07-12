"""Card rendering for QQ command help."""

from renderer.backend import render_card_image
from renderer.renderer_template import renderer
from utils.logger import get_logger
from utils.variable import DEFAULT_SKIN

logger = get_logger("renderer.help")


@renderer("help_card")
async def render_help_card_image(data: dict, skin: str | None = None) -> bytes:
    """Render a QQ help overview or command-detail card to PNG."""
    skin = skin or DEFAULT_SKIN
    image = await render_card_image(
        "help_card", data, skin=skin, width=960, height=None
    )
    logger.info(f"[render_help_card_image] 图片生成完成，大小: {len(image)} bytes")
    return image
