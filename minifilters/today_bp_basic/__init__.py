"""
today_bp_basic minifilter

处理今日BP列表数据，主要功能：
- 格式化 mods 显示（例如：DT with settings speed_change: 1.7 -> "DT 1.7x"）

API 返回的数据已经包含 beatmap 和 beatmapset 嵌套对象，
此 minifilter 专注于数据格式化。
"""

from utils.logger import get_logger

logger = get_logger("minifilters.today_bp_basic")

HOOKS: list[str] = ["user_today_bp"]


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


def _format_score_mods(score: dict) -> dict:
    """
    处理单条成绩的 mods 格式化
    """
    if not isinstance(score, dict):
        return score

    result = dict(score)  # 复制原始数据

    # 格式化 mods
    if "mods" in result and isinstance(result["mods"], list):
        result["mods"] = _format_mods(result["mods"])

    return result


async def process(data: dict) -> dict:
    """
    处理今日BP列表数据，格式化 mods 等信息

    Args:
        data: 包含 scores 列表的数据（scores 中已包含 beatmap/beatmapset 嵌套对象）

    Returns:
        处理后的数据
    """
    if not isinstance(data, dict):
        return data

    result = dict(data)  # 复制原始数据

    # 处理 scores 列表
    if "scores" in result and isinstance(result["scores"], list):
        result["scores"] = [_format_score_mods(score) for score in result["scores"]]

    return result
