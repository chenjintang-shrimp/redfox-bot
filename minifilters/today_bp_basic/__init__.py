"""
today_bp_basic minifilter

确保今日BP列表渲染时，每个成绩对象都包含必要的 beatmap 和 beatmapset 嵌套对象。
某些 API 端点返回的成绩数据可能缺少这些嵌套对象，通过请求 beatmap API 获取完整信息。
"""

import asyncio

from backend.beatmap import get_beatmap_info


async def _ensure_score_nested_objects(score: dict) -> dict:
    """
    确保单条成绩数据包含嵌套的 beatmap 和 beatmapset 对象

    如果缺少，会通过 API 请求获取完整信息。
    """
    if not isinstance(score, dict):
        return score

    result = dict(score)  # 复制原始数据

    # 如果已经有完整的 beatmap 和 beatmapset，直接返回
    if ("beatmap" in result and isinstance(result.get("beatmap"), dict) and
        "beatmapset" in result and isinstance(result.get("beatmapset"), dict)):
        return result

    # 获取 beatmap_id
    beatmap_id = result.get("beatmap_id") or result.get("id")
    if beatmap_id is None and "beatmap" in result:
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

    return result


async def process(data: dict) -> dict:
    """
    处理今日BP列表数据，确保每个成绩都包含 beatmap 和 beatmapset 嵌套对象

    Args:
        data: 包含 scores 列表的数据

    Returns:
        处理后的数据，scores 列表中的每个成绩都包含完整的嵌套对象
    """
    if not isinstance(data, dict):
        return data

    result = dict(data)  # 复制原始数据

    # 处理 scores 列表
    if "scores" in result and isinstance(result["scores"], list):
        # 并发处理所有成绩
        tasks = [
            _ensure_score_nested_objects(score)
            for score in result["scores"]
        ]
        result["scores"] = await asyncio.gather(*tasks)

    return result
