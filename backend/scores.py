from typing import Optional
from backend.api_client import get_osu_api_client
from backend.user import get_user_info
from backend.expections import ScoreQueryError
from utils.logger import get_logger
from utils.strings import get_api_url


async def get_user_beatmap_score(user_id: int, beatmap_id: int):
    client = get_osu_api_client()
    try:
        user_info = await get_user_info(user_id)
        username = user_info.get("username", str(user_id))
    except Exception:
        username = str(user_id)

    url = get_api_url(
        "beatmap_scores",
        beatmap_id=beatmap_id,
        user_id=user_id,
    )
    response = await client.get(url)
    get_logger("backend").info(
        f"Requesting endpoint {url} with user_id {user_id} and beatmap_id {beatmap_id} returned {response.status_code}"
    )
    if response.status_code != 200:
        get_logger("backend").error(
            f"API error: {response.status_code} - {response.text}"
        )
        raise ScoreQueryError(
            username,
            beatmap_id,
            f"API returned {response.status_code} when requesting endpoint {url}",
            response.status_code,
        )

    return response.json()


async def get_user_beatmap_all_scores(
    user_id: int, beatmap_id: int, ruleset: Optional[str] = None, limit: int = 100
):
    """
    获取用户在某个谱面上的全部成绩（支持分页获取所有成绩）

    Args:
        user_id: 用户 ID
        beatmap_id: 谱面 ID
        ruleset: 游戏模式 (可选，默认使用谱面模式)
        limit: 每次请求的最大数量

    Returns:
        成绩列表
    """
    client = get_osu_api_client()
    try:
        user_info = await get_user_info(user_id)
        username = user_info.get("username", str(user_id))
    except Exception:
        username = str(user_id)

    url = get_api_url(
        "beatmap_all_scores",
        beatmap_id=beatmap_id,
        user_id=user_id,
    )

    all_scores = []
    offset = 0

    while True:
        params: dict[str, int | str] = {"limit": limit, "offset": offset}
        if ruleset:
            params["ruleset"] = ruleset

        response = await client.get(url, params=params)
        get_logger("backend").info(
            f"Requesting endpoint {url} for all scores with user_id {user_id} and beatmap_id {beatmap_id} (offset={offset}) returned {response.status_code}"
        )

        if response.status_code != 200:
            get_logger("backend").error(
                f"API error: {response.status_code} - {response.text}"
            )
            raise ScoreQueryError(
                username,
                beatmap_id,
                f"API returned {response.status_code} when requesting endpoint {url}",
                response.status_code,
            )

        data = response.json()

        # 处理响应格式
        if isinstance(data, dict) and "scores" in data:
            scores = data["scores"]
        elif isinstance(data, list):
            scores = data
        else:
            scores = []

        if not scores:
            break

        all_scores.extend(scores)

        # 如果返回的数量小于 limit，说明已经获取完所有成绩
        if len(scores) < limit:
            break

        offset += limit

    get_logger("backend").info(
        f"Total scores fetched for user {user_id} on beatmap {beatmap_id}: {len(all_scores)}"
    )

    return all_scores


async def get_user_beatmap_best_score(user_id: int, beatmap_id: int):
    client = get_osu_api_client()
    try:
        user_info = await get_user_info(user_id)
        username = user_info.get("username", str(user_id))
    except Exception:
        username = str(user_id)

    url = get_api_url(
        "beatmap_best_scores",
        beatmap_id=beatmap_id,
        user_id=user_id,
    )
    response = await client.get(url)
    if response.status_code != 200:
        get_logger("backend").error(
            f"API error: {response.status_code} - {response.text}"
        )
        raise ScoreQueryError(
            username,
            beatmap_id,
            f"API returned {response.status_code} when requesting endpoint {url}",
            response.status_code,
        )

    return response.json()


async def get_user_scores(
    user_id: int,
    type: str,
    include_fails: bool = False,
    mode: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
):
    """
    获取用户的成绩列表 (best/recent/firsts/pinned)

    Args:
        user_id: 用户 ID
        type: 成绩类型 (best, recent, firsts, pinned)
        include_fails: 是否包含失败成绩
        mode: 游戏模式 (可选)
        limit: 返回数量
        offset: 偏移量

    Returns:
        成绩列表
    """
    client = get_osu_api_client()
    try:
        user_info = await get_user_info(user_id)
        username = user_info.get("username", str(user_id))
    except Exception:
        username = str(user_id)

    url = get_api_url(
        "user_scores",
        user_id=user_id,
        type=type,
    )

    params = {
        "include_fails": str(include_fails).lower(),
        "limit": limit,
        "offset": offset,
    }
    if mode:
        params["mode"] = mode

    response = await client.get(url, params=params)
    get_logger("backend").info(
        f"Requesting endpoint {url} with user_id {user_id} and type {type} returned {response.status_code}"
    )
    if response.status_code != 200:
        get_logger("backend").error(
            f"API error: {response.status_code} - {response.text}"
        )
        raise ScoreQueryError(
            username,
            0,  # No specific beatmap_id
            f"API returned {response.status_code} when requesting endpoint {url}",
            response.status_code,
        )

    return response.json()
