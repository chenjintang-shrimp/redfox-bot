"""
成绩渲染器 - 用于渲染用户在谱面上的成绩列表
Scores Renderer - Renders user's scores on a beatmap with pagination support
"""

from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any, Tuple, Optional

from backend.scores import get_user_beatmap_all_scores, get_user_scores, ScoreQueryError
from backend.beatmap import get_beatmap_info
from backend.user import get_user_info
from renderer.renderer_template import renderer
from renderer.skin_loader import render_template as render_skin_template
from utils.flt_mgr import apply_minifilters_async
from utils.html2image import html_to_image
from utils.logger import get_logger
from utils.strings import format_template
from utils.variable import DEFAULT_SKIN

logger = get_logger("renderer.scores")


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


def _format_score_item(score: Dict[str, Any], index: int, locale: str = "en") -> str:
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

    return format_template("SCORES_LIST_ITEM_TEMPLATE", locale=locale, **context)


def _format_user_score_item(score: Dict[str, Any], index: int, locale: str = "en") -> str:
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

    return format_template("USER_SCORES_LIST_ITEM_TEMPLATE", locale=locale, **context)


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
    user_id: int,
    beatmap_id: int,
    page: int = 1,
    ruleset: Optional[str] = None,
    locale: str = "en",
) -> str:
    """
    渲染用户在某个谱面上的全部成绩（支持分页）

    Args:
        user_id: 用户 ID
        beatmap_id: 谱面 ID
        page: 页码（从 1 开始）
        ruleset: 游戏模式（可选）
        locale: 语言代码，默认"en"

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
        return format_template("SCORES_LIST_EMPTY_TEMPLATE", locale=locale, username=username)

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
        locale=locale,
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
        lines.append(_format_score_item(score, i, locale=locale))

    # 尾部
    footer = format_template(
        "SCORES_LIST_FOOTER_TEMPLATE",
        locale=locale,
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
    locale: str = "en",
    mode: str | None = None,
) -> str:
    """
    渲染用户特定类型的成绩列表 (best/recent/etc)

    Args:
        user_id: 用户 ID
        type: 成绩类型
        include_fails: 是否包含失败成绩
        page: 页码
        limit: API请求限制数量
        locale: 语言代码，默认"en"
        mode: 游戏模式 (osu/taiko/fruits/mania)

    Returns:
        格式化后的成绩列表
    """
    scores = await get_user_scores(
        user_id, type, include_fails=include_fails, limit=limit, mode=mode
    )
    user_info = await get_user_info(user_id)
    username = user_info.get("username", "Unknown")

    if not scores:
        return format_template(
            "USER_SCORES_EMPTY_TEMPLATE", locale=locale, username=username, type=type
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
        "USER_SCORES_LIST_HEADER_TEMPLATE", locale=locale, username=username, type=type
    )
    lines.append(header)

    for i, score in enumerate(scores[start_idx:end_idx], start=start_idx + 1):
        lines.append(_format_user_score_item(score, i, locale=locale))

    footer = format_template(
        "SCORES_LIST_FOOTER_TEMPLATE",
        locale=locale,
        current_page=current_page,
        total_pages=total_pages,
        total_scores=total_scores,
    )
    lines.append(footer)

    return "\n".join(lines)


@renderer
async def render_user_recent_score(
    user_id: int, type: str, include_fails: bool = False, locale: str = "en"
) -> str:
    """
    渲染用户最新的单条成绩 (p/r)

    Args:
        user_id: 用户 ID
        type: 成绩类型
        include_fails: 是否包含失败成绩
        locale: 语言代码，默认"en"

    Returns:
        格式化后的单条成绩详情
    """
    # 获取 limit=1 的成绩
    scores = await get_user_scores(user_id, type, include_fails=include_fails, limit=1)
    user_info = await get_user_info(user_id)
    username = user_info.get("username", "Unknown")

    if not scores:
        return format_template(
            "USER_SCORES_EMPTY_TEMPLATE", locale=locale, username=username, type=type
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

    return format_template("USER_SCORE_SINGLE_TEMPLATE", locale=locale, **context)


async def get_user_scores_page_count(
    user_id: int, type: str, include_fails: bool = False, limit: int = 100, mode: str | None = None
) -> int:
    try:
        scores = await get_user_scores(
            user_id, type, include_fails=include_fails, limit=limit, mode=mode
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
async def render_user_today_bp(
    user_id: int, page: int = 1, limit: int = 100, locale: str = "en"
) -> str:
    """
    渲染用户今日（24小时内）刷新的BP

    Args:
        user_id: 用户 ID
        page: 页码（从 1 开始）
        limit: API请求限制数量
        locale: 语言代码，默认"en"

    Returns:
        格式化后的今日BP列表字符串
    """
    # 获取用户的best成绩
    scores = await get_user_scores(user_id, "best", include_fails=False, limit=limit)
    user_info = await get_user_info(user_id)
    username = user_info.get("username", "Unknown")

    if not scores:
        return format_template("TODAY_BP_EMPTY_TEMPLATE", locale=locale, username=username)

    # 过滤24小时内的成绩
    today_scores = [score for score in scores if _is_today_score(score)]

    if not today_scores:
        return format_template("TODAY_BP_EMPTY_TEMPLATE", locale=locale, username=username)

    total_scores = len(today_scores)
    start_idx, end_idx, total_pages = _calculate_pagination(total_scores, page)
    current_page = max(1, min(page, total_pages))

    lines = []

    header = format_template("TODAY_BP_HEADER_TEMPLATE", locale=locale, username=username)
    lines.append(header)

    for i, score in enumerate(today_scores[start_idx:end_idx], start=start_idx + 1):
        lines.append(_format_user_score_item(score, i, locale=locale))

    footer = format_template(
        "SCORES_LIST_FOOTER_TEMPLATE",
        locale=locale,
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


# ============ 图片渲染 API ============


@renderer("user_beatmap_score_card")
async def render_user_beatmap_score_card(
    user_id: int,
    beatmap_id: int,
    skin: str | None = None,
    limit: int = 100,
) -> bytes:
    """
    渲染用户在指定谱面上的最佳成绩为图片

    Args:
        user_id: 用户 ID
        beatmap_id: 谱面 ID
        skin: 皮肤名称，默认使用全局配置
        limit: 查询数量

    Returns:
        PNG 图片字节

    Raises:
        ScoreQueryError: 查询成绩失败
    """
    skin = skin or DEFAULT_SKIN
    logger.info(
        f"[render_user_beatmap_score_card] 开始渲染，user_id={user_id}, beatmap_id={beatmap_id}, skin={skin}"
    )

    # 获取用户在该谱面上的所有成绩
    scores = await get_user_beatmap_all_scores(user_id, beatmap_id, limit=limit)
    if not scores:
        # 没有成绩，抛出异常让 decorator 处理
        from backend.user import get_user_info

        user_info = await get_user_info(user_id)
        raise ScoreQueryError(
            user_info.get("username", str(user_id)),
            beatmap_id,
            "No scores found on this beatmap",
            404,
        )

    # 获取第一条成绩
    score = scores[0]

    # API 返回的成绩数据中没有 beatmap_id，需要手动添加
    # 因为我们已经知道 beatmap_id（用户传入的）
    if "beatmap_id" not in score:
        score["beatmap_id"] = beatmap_id
        logger.debug(f"[render_user_beatmap_score_card] 添加 beatmap_id: {beatmap_id}")

    logger.debug(
        f"[render_user_beatmap_score_card] 原始成绩数据键: {list(score.keys())}"
    )
    logger.debug(
        f"[render_user_beatmap_score_card] beatmap_id: {score.get('beatmap_id')}"
    )

    # 应用 minifilters 处理数据（按 renderer 视图名 hook）
    processed_score = await apply_minifilters_async("user_beatmap_score_card", score)

    # 渲染模板
    html = await render_skin_template(skin, "score_card", processed_score)
    logger.debug(f"[render_user_beatmap_score_card] HTML 长度: {len(html)} chars")

    image_bytes = await html_to_image(html, width=800, height=300)
    logger.info(
        f"[render_user_beatmap_score_card] 图片生成完成，大小: {len(image_bytes)} bytes"
    )

    return image_bytes


@renderer("user_recent_score_card")
async def render_user_recent_score_card(
    user_id: int,
    include_fails: bool = False,
    skin: str | None = None,
    mode: str | None = None,
) -> bytes:
    """
    渲染用户最近的一条成绩为图片

    Args:
        user_id: 用户 ID
        include_fails: 是否包含失败成绩
        skin: 皮肤名称，默认使用全局配置
        mode: 游戏模式 (osu/taiko/fruits/mania)

    Returns:
        PNG 图片字节

    Raises:
        ScoreQueryError: 查询成绩失败
    """
    skin = skin or DEFAULT_SKIN
    logger.info(
        f"[render_user_recent_score_card] 开始渲染，user_id={user_id}, include_fails={include_fails}, mode={mode}, skin={skin}"
    )

    # 获取用户最近成绩
    scores = await get_user_scores(
        user_id, "recent", include_fails=include_fails, limit=1, mode=mode
    )
    if not scores:
        # 没有成绩，抛出异常让 decorator 处理
        from backend.user import get_user_info

        user_info = await get_user_info(user_id)
        raise ScoreQueryError(
            user_info.get("username", str(user_id)), 0, "No recent scores found", 404
        )

    # 获取第一条成绩
    score = scores[0]
    logger.debug(
        f"[render_user_recent_score_card] 原始成绩数据键: {list(score.keys())}"
    )
    logger.debug(
        f"[render_user_recent_score_card] beatmap_id: {score.get('beatmap_id')}, id: {score.get('id')}"
    )

    # 应用 minifilters 处理数据（按 renderer 视图名 hook）
    processed_score = await apply_minifilters_async("user_recent_score_card", score)

    # 渲染模板
    html = await render_skin_template(skin, "score_card", processed_score)
    logger.debug(f"[render_user_recent_score_card] HTML 长度: {len(html)} chars")

    image_bytes = await html_to_image(html, width=800, height=300)
    logger.info(
        f"[render_user_recent_score_card] 图片生成完成，大小: {len(image_bytes)} bytes"
    )

    return image_bytes


@renderer("user_score_list")
async def render_user_score_list_image(
    user_id: int,
    username: str,
    score_type: str = "recent",
    include_fails: bool = False,
    skin: str | None = None,
    count: int = 100,
    mode: str | None = None,
) -> bytes:
    """
    渲染用户成绩列表为图片（长图模式，不分页）

    Args:
        user_id: 用户 ID
        username: 用户名
        score_type: 成绩类型 ("recent" 或 "best")
        include_fails: 是否包含失败成绩
        skin: 皮肤名称，默认使用全局配置
        count: 成绩数量，默认100条
        mode: 游戏模式 (osu/taiko/fruits/mania)

    Returns:
        PNG 图片字节

    Raises:
        ScoreQueryError: 查询成绩失败
    """
    skin = skin or DEFAULT_SKIN
    logger.info(
        f"[render_user_score_list_image] 开始渲染，user_id={user_id}, type={score_type}, mode={mode}, skin={skin}"
    )

    # 获取所有成绩（限制20个，与yumu保持一致）
    scores = await get_user_scores(
        user_id,
        score_type,
        include_fails=include_fails,
        limit=count,
        mode=mode,
    )
    if not scores:
        raise ScoreQueryError(username, 0, f"No {score_type} scores found", 404)

    # 检查第一条成绩的字段
    logger.debug(
        f"[render_user_score_list_image] 第一条成绩数据键: {list(scores[0].keys())}"
    )
    logger.debug(
        f"[render_user_score_list_image] beatmap_id: {scores[0].get('beatmap_id')}, id: {scores[0].get('id')}"
    )
    logger.debug(f"[render_user_score_list_image] beatmap: {scores[0].get('beatmap')}")
    logger.debug(
        f"[render_user_score_list_image] beatmapset: {scores[0].get('beatmapset')}"
    )

    # 确定标题
    title_map = {
        ("recent", False): "Recent Passed Scores",
        ("recent", True): "Recent Scores",
        ("best", False): "Best Scores",
    }
    title = title_map.get((score_type, include_fails), "Scores")

    data = {
        "scores": scores,
        "username": username,
        "title": title,
    }

    # 应用 minifilters 处理数据（按 renderer 视图名 hook）
    processed_data = await apply_minifilters_async("user_score_list", data)

    # 渲染模板
    html = await render_skin_template(skin, "score_list", processed_data)
    logger.debug(f"[render_user_score_list_image] HTML 长度: {len(html)} chars")

    # 动态计算高度（根据成绩数量）
    height = 100 + len(scores) * 80 + 50
    height = max(400, min(height, 3000))  # 最大高度 3000，防止过长

    image_bytes = await html_to_image(html, width=800, height=height)
    logger.info(
        f"[render_user_score_list_image] 图片生成完成，大小: {len(image_bytes)} bytes, 包含 {len(scores)} 条成绩"
    )

    return image_bytes


async def render_score_list_image(
    scores: list,
    username: str,
    title: str,
    page: int = 1,
    total_pages: int = 1,
    skin: str | None = None,
) -> bytes:
    """
    渲染成绩列表为图片（直接传入成绩列表）

    Args:
        scores: 成绩列表
        username: 用户名
        title: 列表标题
        page: 当前页码
        total_pages: 总页数
        skin: 皮肤名称，默认使用全局配置

    Returns:
        PNG 图片字节
    """
    skin = skin or DEFAULT_SKIN
    logger.info(f"[render_score_list_image] 开始渲染，skin={skin}")

    data = {
        "scores": scores,
        "username": username,
        "title": title,
        "page": page,
        "total_pages": total_pages,
    }

    # 应用 minifilters 处理数据（复用 user_score_list 的 hook）
    processed_data = await apply_minifilters_async("user_score_list", data)

    html = await render_skin_template(skin, "score_list", processed_data)
    logger.debug(f"[render_score_list_image] HTML 长度: {len(html)} chars")

    # 动态计算高度
    height = 100 + len(scores) * 80 + 50
    height = max(400, min(height, 1200))

    image_bytes = await html_to_image(html, width=800, height=height)
    logger.info(
        f"[render_score_list_image] 图片生成完成，大小: {len(image_bytes)} bytes"
    )

    return image_bytes


@renderer("user_today_bp")
async def render_user_today_bp_image(
    user_id: int,
    username: str,
    skin: str | None = None,
    mode: str | None = None,
) -> bytes:
    """
    渲染用户今日BP为图片

    Args:
        user_id: 用户 ID
        username: 用户名
        skin: 皮肤名称，默认使用全局配置
        mode: 游戏模式 (osu/taiko/fruits/mania)

    Returns:
        PNG 图片字节

    Raises:
        ScoreQueryError: 查询成绩失败
    """
    skin = skin or DEFAULT_SKIN
    logger.info(
        f"[render_user_today_bp_image] 开始渲染，user_id={user_id}, mode={mode}, skin={skin}"
    )

    # 获取 best 成绩
    scores = await get_user_scores(user_id, "best", include_fails=False, limit=100, mode=mode)

    # 检查第一条成绩的字段
    if scores:
        logger.debug(
            f"[render_user_today_bp_image] 第一条成绩数据键: {list(scores[0].keys())}"
        )
        logger.debug(
            f"[render_user_today_bp_image] beatmap_id: {scores[0].get('beatmap_id')}, id: {scores[0].get('id')}"
        )

    # 过滤今日成绩（24小时内）
    def _is_today(score):
        try:
            time_str = score.get("ended_at") or score.get("created_at")
            if not time_str:
                return False
            score_time = datetime.fromisoformat(time_str.replace("Z", "+00:00"))
            return datetime.now(timezone.utc) - score_time <= timedelta(hours=24)
        except Exception:
            return False

    today_scores = [s for s in scores if _is_today(s)]

    if not today_scores:
        raise ScoreQueryError(
            username, 0, "No new best scores in the last 24 hours", 404
        )

    # 获取总页数
    total_pages = await get_today_bp_page_count(user_id)

    data = {
        "scores": today_scores[:5],
        "username": username,
        "page": 1,
        "total_pages": total_pages,
    }

    # 应用 minifilters 处理数据（按 renderer 视图名 hook）
    processed_data = await apply_minifilters_async("user_today_bp", data)

    # 渲染模板
    html = await render_skin_template(skin, "today_bp", processed_data)
    logger.debug(f"[render_user_today_bp_image] HTML 长度: {len(html)} chars")

    # 动态计算高度
    height = 120 + len(today_scores[:5]) * 90 + 50
    height = max(400, min(height, 1200))

    image_bytes = await html_to_image(html, width=800, height=height)
    logger.info(
        f"[render_user_today_bp_image] 图片生成完成，大小: {len(image_bytes)} bytes"
    )

    return image_bytes


async def render_today_bp_image(
    scores: list,
    username: str,
    page: int = 1,
    total_pages: int = 1,
    skin: str | None = None,
) -> bytes:
    """
    渲染今日BP为图片（直接传入成绩列表）

    Args:
        scores: 今日BP列表
        username: 用户名
        page: 当前页码
        total_pages: 总页数
        skin: 皮肤名称，默认使用全局配置

    Returns:
        PNG 图片字节
    """
    skin = skin or DEFAULT_SKIN
    logger.info(f"[render_today_bp_image] 开始渲染，skin={skin}")

    data = {
        "scores": scores,
        "username": username,
        "page": page,
        "total_pages": total_pages,
    }

    # 应用 minifilters 处理数据（复用 user_today_bp 的 hook）
    processed_data = await apply_minifilters_async("user_today_bp", data)

    html = await render_skin_template(skin, "today_bp", processed_data)
    logger.debug(f"[render_today_bp_image] HTML 长度: {len(html)} chars")

    # 动态计算高度
    height = 120 + len(scores) * 90 + 50
    height = max(400, min(height, 1200))

    image_bytes = await html_to_image(html, width=800, height=height)
    logger.info(f"[render_today_bp_image] 图片生成完成，大小: {len(image_bytes)} bytes")

    return image_bytes
