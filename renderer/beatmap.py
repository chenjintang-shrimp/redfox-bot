from backend.beatmap import get_beatmap_info
from backend.expections.beatmap import BeatmapNotFoundError
from renderer.renderer_template import renderer, ExceptionHandler
from utils.strings import format_template


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
        return format_template("BEATMAP_NOT_FOUND_TEMPLATE", {})
    except Exception as e:
        return ExceptionHandler.handle(e)
