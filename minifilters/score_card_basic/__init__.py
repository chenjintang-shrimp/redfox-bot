"""
score_card_basic minifilter

确保成绩卡片渲染时包含必要的 beatmap 和 beatmapset 嵌套对象。
某些 API 端点返回的成绩数据可能缺少这些嵌套对象，通过请求 beatmap API 获取完整信息。
"""

from backend.beatmap import get_beatmap_info
from utils.logger import get_logger

logger = get_logger("minifilters.score_card_basic")


async def process(data: dict) -> dict:
    """
    处理成绩数据，确保包含 beatmap 和 beatmapset 嵌套对象

    如果数据中缺少 beatmap/beatmapset，会通过 API 请求获取完整信息。

    Args:
        data: 成绩数据（可能缺少 beatmap/beatmapset 嵌套对象）

    Returns:
        处理后的数据，确保包含完整的嵌套对象
    """
    if not isinstance(data, dict):
        return data

    result = dict(data)  # 复制原始数据

    # 如果已经有完整的 beatmap 和 beatmapset，直接返回
    if ("beatmap" in result and isinstance(result.get("beatmap"), dict) and
        "beatmapset" in result and isinstance(result.get("beatmapset"), dict)):
        return result

    # 获取 beatmap_id - 优先使用 beatmap_id 字段，这是 osu! API v2 的标准字段
    beatmap_id = result.get("beatmap_id")
    
    if not beatmap_id and "beatmap" in result:
        beatmap_id = result["beatmap"].get("id")

    if beatmap_id:
        try:
            # 请求 beatmap API 获取完整信息
            beatmap_info = await get_beatmap_info(beatmap_id)

            # 设置 beatmap
            if "beatmap" not in result or not isinstance(result.get("beatmap"), dict):
                result["beatmap"] = {
                    "id": beatmap_info.get("id"),
                    "beatmapset_id": beatmap_info.get("beatmapset_id"),
                    "version": beatmap_info.get("version", "Unknown"),
                    "difficulty_rating": beatmap_info.get("difficulty_rating", 0),
                    "mode": beatmap_info.get("mode", "osu"),
                    "status": beatmap_info.get("status", "ranked"),
                    "total_length": beatmap_info.get("total_length", 0),
                    "hit_length": beatmap_info.get("hit_length", 0),
                    "bpm": beatmap_info.get("bpm", 0),
                    "cs": beatmap_info.get("cs", 0),
                    "drain": beatmap_info.get("drain", 0),
                    "accuracy": beatmap_info.get("accuracy", 0),
                    "ar": beatmap_info.get("ar", 0),
                }

            # 设置 beatmapset
            if "beatmapset" not in result or not isinstance(result.get("beatmapset"), dict):
                beatmapset_info = beatmap_info.get("beatmapset", {})
                result["beatmapset"] = {
                    "id": beatmapset_info.get("id", beatmap_info.get("beatmapset_id")),
                    "title": beatmapset_info.get("title", "Unknown"),
                    "artist": beatmapset_info.get("artist", "Unknown"),
                    "creator": beatmapset_info.get("creator", "Unknown"),
                    "covers": beatmapset_info.get("covers", {}),
                }

        except Exception:
            # API 请求失败，使用默认值
            if "beatmap" not in result or not isinstance(result.get("beatmap"), dict):
                result["beatmap"] = {
                    "id": beatmap_id,
                    "beatmapset_id": result.get("beatmapset_id", 0),
                    "version": result.get("version", "Unknown"),
                    "difficulty_rating": result.get("difficulty_rating", 0),
                }

            if "beatmapset" not in result or not isinstance(result.get("beatmapset"), dict):
                result["beatmapset"] = {
                    "id": result.get("beatmapset_id", 0),
                    "title": result.get("beatmapset_title", "Unknown"),
                    "artist": result.get("beatmapset_artist", "Unknown"),
                    "covers": {},
                }
    else:
        # 无法获取 beatmap_id，设置默认值
        if "beatmap" not in result or not isinstance(result.get("beatmap"), dict):
            result["beatmap"] = {
                "id": 0,
                "beatmapset_id": result.get("beatmapset_id", 0),
                "version": result.get("version", "Unknown"),
                "difficulty_rating": result.get("difficulty_rating", 0),
            }

        if "beatmapset" not in result or not isinstance(result.get("beatmapset"), dict):
            result["beatmapset"] = {
                "id": result.get("beatmapset_id", 0),
                "title": result.get("beatmapset_title", "Unknown"),
                "artist": result.get("beatmapset_artist", "Unknown"),
                "covers": {},
            }

    return result
