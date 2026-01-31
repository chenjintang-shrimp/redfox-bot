from backend.beatmap import get_beatmap_info
from backend.expections.beatmap import BeatmapNotFoundError
from renderer.renderer_template import renderer, ExceptionHandler
from renderer.skin_loader import render_template as render_skin_template
from utils.html2image import html_to_image
from utils.logger import get_logger
from utils.strings import format_template
from utils.variable import DEFAULT_SKIN

logger = get_logger("renderer.beatmap")


@renderer
async def render_beatmap_info(beatmap_id: int):
    """
    获取谱面信息并渲染
    """
    try:
        beatmap_info = await get_beatmap_info(beatmap_id)

        # 提取需要的信息
        beatmapset = beatmap_info.get("beatmapset", {})

        # 计算长度 (mm:ss)
        total_length = beatmap_info.get("total_length", 0)
        minutes = total_length // 60
        seconds = total_length % 60
        length_str = f"{minutes:02d}:{seconds:02d}"

        context = {
            "title": beatmapset.get("title", "?"),
            "version": beatmap_info.get("version", "?"),
            "artist": beatmapset.get("artist", "?"),
            "creator": beatmapset.get("creator", "?"),
            "stars": beatmap_info.get("difficulty_rating", 0),
            "length": length_str,
            "status": beatmap_info.get("status", "unknown").title(),
            "bpm": beatmap_info.get("bpm", 0),
            "cs": beatmap_info.get("cs", 0),
            "ar": beatmap_info.get("ar", 0),
            "od": beatmap_info.get(
                "accuracy", 0
            ),  # OD depends on mode, usually accuracy in API
            "hp": beatmap_info.get("drain", 0),
            "url": beatmap_info.get("url", ""),
        }

        return format_template("BEATMAP_INFO_TEMPLATE", **context)

    except BeatmapNotFoundError:
        return format_template("BEATMAP_NOT_FOUND_TEMPLATE")
    except Exception as e:
        return ExceptionHandler.handle(e)


async def render_beatmap_card_image(
    beatmap_info: dict,
    skin: str | None = None,
) -> bytes:
    """
    渲染谱面卡片为图片

    Args:
        beatmap_info: API 返回的谱面数据
        skin: 皮肤名称，默认使用全局配置

    Returns:
        PNG 图片字节
    """
    skin = skin or DEFAULT_SKIN
    logger.info(f"[render_beatmap_card_image] 开始渲染，skin={skin}")

    html = await render_skin_template(skin, "beatmap_card", beatmap_info)
    logger.debug(f"[render_beatmap_card_image] HTML 长度: {len(html)} chars")

    image_bytes = await html_to_image(html, width=800, height=400)
    logger.info(
        f"[render_beatmap_card_image] 图片生成完成，大小: {len(image_bytes)} bytes"
    )

    return image_bytes
