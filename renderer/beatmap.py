from backend.beatmap import get_beatmap_info
from backend.exceptions.beatmap import BeatmapNotFoundError
from renderer.renderer_template import renderer, ExceptionHandler
from renderer.skin_loader import render_template as render_skin_template
from utils.flt_mgr import apply_minifilters_async
from utils.html2image import html_to_image
from utils.logger import get_logger
from utils.strings import format_template
from utils.variable import DEFAULT_SKIN

logger = get_logger("renderer.beatmap")


@renderer
async def render_beatmap_info(beatmap_id: int, locale: str = "en"):
    """
    获取谱面信息并渲染

    Args:
        beatmap_id: 谱面ID
        locale: 语言代码，默认"en"
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

        return format_template("BEATMAP_INFO_TEMPLATE", locale=locale, **context)

    except BeatmapNotFoundError:
        return format_template("BEATMAP_NOT_FOUND_TEMPLATE", locale=locale)
    except Exception as e:
        return ExceptionHandler.handle(e, locale=locale)


@renderer("beatmap_card")
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

    # 应用 minifilters 处理数据（按 renderer 视图名 hook）
    processed_data = await apply_minifilters_async("beatmap_card", beatmap_info)

    html = await render_skin_template(skin, "beatmap_card", processed_data)
    logger.debug(f"[render_beatmap_card_image] HTML 长度: {len(html)} chars")

    image_bytes = await html_to_image(html, width=800, height=400)
    logger.info(
        f"[render_beatmap_card_image] 图片生成完成，大小: {len(image_bytes)} bytes"
    )

    return image_bytes
