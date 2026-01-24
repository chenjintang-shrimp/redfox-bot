"""
成绩渲染器 - 用于渲染用户在谱面上的成绩列表
Scores Renderer - Renders user's scores on a beatmap with pagination support
"""

from datetime import datetime
from typing import List, Dict, Any, Tuple, Optional

from backend.scores import get_user_beatmap_all_scores
from backend.beatmap import get_beatmap_info
from backend.user import get_user_info
from renderer.renderer_template import renderer
from utils.strings import format_template


SCORES_PER_PAGE = 10


def _format_mods(mods: List[Dict[str, Any]]) -> str:
    """格式化 mods 列表为字符串"""
    if not mods:
        return "NM"
    return "+".join(mod.get("acronym", "") for mod in mods)


def _format_rank(rank: str) -> str:
    """格式化评级，添加 emoji"""
    from utils.strings import load_strings

    try:
        rank_emojis = load_strings().get("RANK_EMOJIS", {})
        return rank_emojis.get(rank, rank)
    except Exception:
        # Fallback if config fails
        return rank


def _format_datetime(dt_str: str) -> str:
    """格式化日期时间字符串"""
    try:
        # 解析 ISO 格式的日期时间
        dt = datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
        return dt.strftime("%Y-%m-%d %H:%M")
    except (ValueError, AttributeError):
        return dt_str


def _format_accuracy(accuracy: float) -> str:
    """格式化准确率 (API 返回的是 0-1 的小数)"""
    return f"{accuracy * 100:.2f}%"


def _format_score_item(score: Dict[str, Any], index: int) -> str:
    """格式化单条成绩"""
    rank = _format_rank(score.get("rank", "?"))
    total_score = score.get("total_score", score.get("score", 0))
    accuracy = score.get("accuracy", 0)
    max_combo = score.get("max_combo", 0)
    pp = score.get("pp", 0) or 0
    mods = _format_mods(score.get("mods", []))
    created_at = _format_datetime(score.get("ended_at", score.get("created_at", "")))

    # 构建上下文
    context = {
        "index": index,
        "rank": rank,
        "total_score": f"{total_score:,}",
        "accuracy": _format_accuracy(accuracy),
        "max_combo": max_combo,
        "pp": pp,
        "mods": mods,
        "created_at": created_at,
    }

    return format_template("SCORES_LIST_ITEM_TEMPLATE", **context)


def _calculate_pagination(
    total_items: int, page: int, per_page: int = SCORES_PER_PAGE
) -> Tuple[int, int, int]:
    """
    计算分页信息

    Returns:
        (start_index, end_index, total_pages)
    """
    total_pages = max(1, (total_items + per_page - 1) // per_page)
    page = max(1, min(page, total_pages))  # 限制页码范围

    start_index = (page - 1) * per_page
    end_index = min(start_index + per_page, total_items)

    return start_index, end_index, total_pages


@renderer
async def render_user_beatmap_scores(
    user_id: int, beatmap_id: int, page: int = 1, ruleset: Optional[str] = None
) -> str:
    """
    渲染用户在某个谱面上的全部成绩（支持分页）

    Args:
        user_id: 用户 ID
        beatmap_id: 谱面 ID
        page: 页码（从 1 开始）
        ruleset: 游戏模式（可选）

    Returns:
        格式化后的成绩列表字符串
    """
    # 获取数据
    scores = await get_user_beatmap_all_scores(user_id, beatmap_id, ruleset)
    user_info = await get_user_info(user_id)
    beatmap_info = await get_beatmap_info(beatmap_id)

    username = user_info.get("username", "Unknown")

    # 处理空成绩
    if not scores:
        return format_template("SCORES_LIST_EMPTY_TEMPLATE", username=username)

    # 获取谱面信息
    beatmapset = beatmap_info.get("beatmapset", {})
    beatmap_title = beatmapset.get("title", "Unknown")
    beatmap_artist = beatmapset.get("artist", "Unknown")
    beatmap_version = beatmap_info.get("version", "Unknown")
    beatmap_stars = beatmap_info.get("difficulty_rating", 0)
    beatmap_mode = beatmap_info.get("mode", "osu")

    # 计算分页
    total_scores = len(scores)
    start_idx, end_idx, total_pages = _calculate_pagination(total_scores, page)
    current_page = max(1, min(page, total_pages))

    # 构建输出
    lines = []

    # 头部
    header = format_template(
        "SCORES_LIST_HEADER_TEMPLATE",
        username=username,
        beatmap_title=beatmap_title,
        beatmap_version=beatmap_version,
        beatmap_artist=beatmap_artist,
        beatmap_stars=beatmap_stars,
        beatmap_mode=beatmap_mode.upper(),
    )
    lines.append(header)

    # 成绩列表
    for i, score in enumerate(scores[start_idx:end_idx], start=start_idx + 1):
        lines.append(_format_score_item(score, i))

    # 尾部
    footer = format_template(
        "SCORES_LIST_FOOTER_TEMPLATE",
        current_page=current_page,
        total_pages=total_pages,
        total_scores=total_scores,
    )
    lines.append(footer)

    return "\n".join(lines)


async def get_scores_page_count(
    user_id: int, beatmap_id: int, ruleset: Optional[str] = None
) -> int:
    """
    获取成绩的总页数（用于分页按钮控制）

    Args:
        user_id: 用户 ID
        beatmap_id: 谱面 ID
        ruleset: 游戏模式（可选）

    Returns:
        总页数
    """
    try:
        scores = await get_user_beatmap_all_scores(user_id, beatmap_id, ruleset)
        if not scores:
            return 0
        return max(1, (len(scores) + SCORES_PER_PAGE - 1) // SCORES_PER_PAGE)
    except Exception:
        return 0
