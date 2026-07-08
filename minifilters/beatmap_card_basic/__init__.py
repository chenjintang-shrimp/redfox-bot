"""
beatmap_card_basic minifilter

处理谱面卡片的数据格式化，将扁平的 BeatmapInfo 字典重组为模板所需的嵌套结构：
- 重建 beatmapset 嵌套对象（模板需要 beatmapset.title/artist/creator/id）
- 映射 od -> accuracy, hp -> drain（模板使用 API 原始字段名）
"""

from utils.logger import get_logger

logger = get_logger("minifilters.beatmap_card_basic")

HOOKS: list[str] = ["beatmap_card"]


def process(data: dict) -> dict:
    """
    处理谱面数据，重组为模板所需的嵌套结构

    Args:
        data: BeatmapInfo 的字典形式（扁平结构）

    Returns:
        处理后的数据（含 beatmapset 嵌套对象及 accuracy/drain 字段）
    """
    if not isinstance(data, dict):
        return data

    result = dict(data)

    # 重建 beatmapset 嵌套对象（模板需要 beatmapset.title/artist/creator/id）
    if "beatmapset" not in result:
        result["beatmapset"] = {
            "id": result.get("beatmapset_id", 0),
            "title": result.get("title", ""),
            "artist": result.get("artist", ""),
            "creator": result.get("creator", ""),
        }
        logger.debug("[beatmap_card_basic] 已重建 beatmapset 嵌套对象")

    # 模板使用 API 原始字段名 accuracy/drain，而 BeatmapInfo 使用 od/hp
    if "accuracy" not in result and "od" in result:
        result["accuracy"] = result["od"]
    if "drain" not in result and "hp" in result:
        result["drain"] = result["hp"]

    return result
