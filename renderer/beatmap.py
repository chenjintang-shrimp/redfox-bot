from backend.beatmap import get_beatmap_info
from backend.exceptions.beatmap import BeatmapNotFoundError
from renderer.backend import render_card_image
from renderer.renderer_template import renderer, handle_exception
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

        return format_template("BEATMAP_INFO_TEMPLATE", context=context, locale=locale)

    except BeatmapNotFoundError:
        return format_template("BEATMAP_NOT_FOUND_TEMPLATE", locale=locale)
    except Exception as e:
        return handle_exception(e, locale=locale)


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

    image_bytes = await render_card_image(
        "beatmap_card", beatmap_info, skin=skin, width=800, height=None
    )
    logger.info(
        f"[render_beatmap_card_image] 图片生成完成，大小: {len(image_bytes)} bytes"
    )

    return image_bytes
