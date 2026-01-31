"""
成绩渲染器 - 用于渲染用户在谱面上的成绩列表
Scores Renderer - Renders user's scores on a beatmap with pagination support
"""

from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any, Tuple, Optional

from backend.scores import get_user_beatmap_all_scores, get_user_scores
from backend.beatmap import get_beatmap_info
from backend.user import get_user_info
from renderer.renderer_template import renderer
from utils.strings import format_template


SCORES_PER_PAGE = 10


def _format_mods(mods: List[Dict[str, Any] | str]) -> str:
    """格式化 mods 列表为字符串"""
    if not mods:
        return "NM"

    formatted_mods = []
    for mod in mods:
        if isinstance(mod, dict):
            formatted_mods.append(mod.get("acronym", ""))
        elif isinstance(mod, str):
            formatted_mods.append(mod)

    return "+".join(formatted_mods)


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


def _format_user_score_item(score: Dict[str, Any], index: int) -> str:
    """格式化用户成绩列表中的单条成绩"""
    beatmap = score.get("beatmap", {})
    beatmapset = score.get("beatmapset", {})

    # 优先从 beatmapset 获取 title/version，如果失败则尝试 beatmap
    title = beatmapset.get("title", beatmap.get("beatmapset", {}).get("title", "?"))
    version = beatmap.get("version", "?")

    rank = _format_rank(score.get("rank", "?"))
    pp = score.get("pp", 0) or 0
    accuracy = score.get("accuracy", 0)
    mods = _format_mods(score.get("mods", []))
    created_at = _format_datetime(score.get("ended_at", score.get("created_at", "")))

    context = {
        "index": index,
        "rank": rank,
        "pp": pp,
        "accuracy": _format_accuracy(accuracy),
        "beatmap_title": title,
        "beatmap_version": version,
        "mods": mods,
        "created_at": created_at,
    }

    return format_template("USER_SCORES_LIST_ITEM_TEMPLATE", **context)


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

    # 按 score_id 去重（防止 API 返回重复数据）
    seen_ids = set()
    unique_scores = []
    for score in scores:
        score_id = score.get("id") or score.get("score_id")
        if score_id and score_id not in seen_ids:
            seen_ids.add(score_id)
            unique_scores.append(score)
        elif not score_id:
            # 如果没有 id，保留该成绩
            unique_scores.append(score)
    scores = unique_scores

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


@renderer
async def render_user_score_list(
    user_id: int,
    type: str,
    include_fails: bool = False,
    page: int = 1,
    limit: int = 100,
) -> str:
    """
    渲染用户特定类型的成绩列表 (best/recent/etc)

    Args:
        user_id: 用户 ID
        type: 成绩类型
        include_fails: 是否包含失败成绩
        page: 页码
        limit: API请求限制数量

    Returns:
        格式化后的成绩列表
    """
    scores = await get_user_scores(
        user_id, type, include_fails=include_fails, limit=limit
    )
    user_info = await get_user_info(user_id)
    username = user_info.get("username", "Unknown")

    if not scores:
        return format_template(
            "USER_SCORES_EMPTY_TEMPLATE", username=username, type=type
        )

    # 如果是 best 类型 (bp)，需要过滤 24 小时内刷新的
    # 但根据最新指示，recent 已经默认 24h，所以这里只需对 best 做可能的过滤
    # "t" 命令要求 24h 内刷新的 bp。API 返回的 best 是按 pp 排序的。
    # 我们需要在内存中过滤，因为 API 不支持时间范围过滤 best。
    if type == "best":
        # 过滤 updated_at 或 created_at 在 24 小时内的
        # 注意：这里需要 datetime 计算，暂时略过复杂实现，直接显示 API 返回的 best
        # 如果需要严格实现 "t" (today's bp)，可以在这里 filter
        pass

    total_scores = len(scores)
    start_idx, end_idx, total_pages = _calculate_pagination(total_scores, page)
    current_page = max(1, min(page, total_pages))

    lines = []

    header = format_template(
        "USER_SCORES_LIST_HEADER_TEMPLATE", username=username, type=type
    )
    lines.append(header)

    for i, score in enumerate(scores[start_idx:end_idx], start=start_idx + 1):
        lines.append(_format_user_score_item(score, i))

    footer = format_template(
        "SCORES_LIST_FOOTER_TEMPLATE",
        current_page=current_page,
        total_pages=total_pages,
        total_scores=total_scores,
    )
    lines.append(footer)

    return "\n".join(lines)


@renderer
async def render_user_recent_score(
    user_id: int, type: str, include_fails: bool = False
) -> str:
    """
    渲染用户最新的单条成绩 (p/r)

    Args:
        user_id: 用户 ID
        type: 成绩类型
        include_fails: 是否包含失败成绩

    Returns:
        格式化后的单条成绩详情
    """
    # 获取 limit=1 的成绩
    scores = await get_user_scores(user_id, type, include_fails=include_fails, limit=1)
    user_info = await get_user_info(user_id)
    username = user_info.get("username", "Unknown")

    if not scores:
        return format_template(
            "USER_SCORES_EMPTY_TEMPLATE", username=username, type=type
        )

    score = scores[0]
    beatmap = score.get("beatmap", {})
    beatmapset = score.get("beatmapset", {})

    # 构建上下文
    context = {
        "username": username,
        "type": type,
        "beatmap_title": beatmapset.get("title", "?"),
        "beatmap_version": beatmap.get("version", "?"),
        "beatmap_artist": beatmapset.get("artist", "?"),
        "beatmap_stars": beatmap.get("difficulty_rating", 0),
        "beatmap_mode": beatmap.get("mode", "osu"),
        "rank_emoji": _format_rank(score.get("rank", "?")),
        "rank": score.get("rank", "?"),
        "pp": score.get("pp", 0) or 0,
        "accuracy": _format_accuracy(score.get("accuracy", 0)),
        "mods": _format_mods(score.get("mods", [])),
        "max_combo": score.get("max_combo", 0),
        "max_combo_beatmap": beatmap.get("max_combo", 0)
        or "?",  # API 可能不返回 max_combo
        "total_score": f"{score.get('total_score', 0):,}",
        "created_at": _format_datetime(
            score.get("ended_at", score.get("created_at", ""))
        ),
        "beatmap_url": f"https://osu.ppy.sh/b/{beatmap.get('id', 0)}",  # 假设这是官网链接
    }

    return format_template("USER_SCORE_SINGLE_TEMPLATE", **context)


async def get_user_scores_page_count(
    user_id: int, type: str, include_fails: bool = False, limit: int = 100
) -> int:
    try:
        scores = await get_user_scores(
            user_id, type, include_fails=include_fails, limit=limit
        )
        if not scores:
            return 0
        return max(1, (len(scores) + SCORES_PER_PAGE - 1) // SCORES_PER_PAGE)
    except Exception:
        return 0


def _is_today_score(score: Dict[str, Any]) -> bool:
    """检查成绩是否在24小时内"""
    try:
        # 获取成绩时间
        time_str = score.get("ended_at") or score.get("created_at")
        if not time_str:
            return False

        # 解析时间
        score_time = datetime.fromisoformat(time_str.replace("Z", "+00:00"))

        # 获取当前时间（UTC）
        now = datetime.now(timezone.utc)

        # 计算时间差
        time_diff = now - score_time

        # 检查是否在24小时内
        return time_diff <= timedelta(hours=24)
    except (ValueError, TypeError):
        return False


@renderer
async def render_user_today_bp(user_id: int, page: int = 1, limit: int = 100) -> str:
    """
    渲染用户今日（24小时内）刷新的BP

    Args:
        user_id: 用户 ID
        page: 页码（从 1 开始）
        limit: API请求限制数量

    Returns:
        格式化后的今日BP列表字符串
    """
    # 获取用户的best成绩
    scores = await get_user_scores(user_id, "best", include_fails=False, limit=limit)
    user_info = await get_user_info(user_id)
    username = user_info.get("username", "Unknown")

    if not scores:
        return format_template("TODAY_BP_EMPTY_TEMPLATE", username=username)

    # 过滤24小时内的成绩
    today_scores = [score for score in scores if _is_today_score(score)]

    if not today_scores:
        return format_template("TODAY_BP_EMPTY_TEMPLATE", username=username)

    total_scores = len(today_scores)
    start_idx, end_idx, total_pages = _calculate_pagination(total_scores, page)
    current_page = max(1, min(page, total_pages))

    lines = []

    header = format_template("TODAY_BP_HEADER_TEMPLATE", username=username)
    lines.append(header)

    for i, score in enumerate(today_scores[start_idx:end_idx], start=start_idx + 1):
        lines.append(_format_user_score_item(score, i))

    footer = format_template(
        "SCORES_LIST_FOOTER_TEMPLATE",
        current_page=current_page,
        total_pages=total_pages,
        total_scores=total_scores,
    )
    lines.append(footer)

    return "\n".join(lines)


async def get_today_bp_page_count(user_id: int, limit: int = 100) -> int:
    """
    获取今日BP的总页数

    Args:
        user_id: 用户 ID
        limit: API请求限制数量

    Returns:
        总页数
    """
    try:
        scores = await get_user_scores(
            user_id, "best", include_fails=False, limit=limit
        )
        if not scores:
            return 0

        # 过滤24小时内的成绩
        today_scores = [score for score in scores if _is_today_score(score)]

        if not today_scores:
            return 0

        return max(1, (len(today_scores) + SCORES_PER_PAGE - 1) // SCORES_PER_PAGE)
    except Exception:
        return 0
