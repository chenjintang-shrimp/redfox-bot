"""
score_card_basic minifilter

处理成绩卡片的数据格式化，包括：
- Mods 格式化（如 DT settings 1.3 -> DT 1.3x）
- 获取 beatmap 信息（如果数据中只有 beatmap_id）
"""

from backend.beatmap import get_beatmap_info
from utils.logger import get_logger

logger = get_logger("minifilters.score_card_basic")


def _format_mods(mods: list) -> list:
    """
    格式化 mods 列表

    例如：
    - DT with settings speed_change: 1.7 -> "DT 1.7x"
    - HR without settings -> "HR"
    """
    if not mods:
        return []

    formatted = []
    for mod in mods:
        if isinstance(mod, dict):
            acronym = mod.get("acronym", "")
            settings = mod.get("settings", {})

            if settings:
                # 处理 speed_change 设置
                if "speed_change" in settings:
                    formatted.append(f"{acronym} {settings['speed_change']}x")
                else:
                    formatted.append(acronym)
            else:
                formatted.append(acronym)
        elif isinstance(mod, str):
            formatted.append(mod)

    return formatted


async def process(data: dict) -> dict:
    """
    处理成绩数据，格式化 mods 等信息

    Args:
        data: 成绩数据（已包含 beatmap/beatmapset 嵌套对象）

    Returns:
        处理后的数据
    """
    if not isinstance(data, dict):
        return data

    result = dict(data)  # 复制原始数据

    # 如果只有 beatmap_id 而没有 beatmap 对象，获取谱面信息
    if "beatmap" not in result and "beatmap_id" in result:
        beatmap_id = result["beatmap_id"]
        try:
            beatmap_info = await get_beatmap_info(beatmap_id)
            result["beatmap"] = beatmap_info
            # 将 beatmapset 从 beatmap 中提取到根级别（模板需要）
            if "beatmapset" in beatmap_info:
                result["beatmapset"] = beatmap_info["beatmapset"]
            logger.debug(f"[score_card_basic] 已获取 beatmap 信息: {beatmap_id}")
        except Exception as e:
            logger.warning(f"[score_card_basic] 获取 beatmap 信息失败: {beatmap_id}, {e}")

    # 格式化 mods
    if "mods" in result and isinstance(result["mods"], list):
        result["mods"] = _format_mods(result["mods"])

    if "accuracy" in result:
        result["accuracy"] *= 100

    return result
