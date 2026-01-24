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
    user_id: int, beatmap_id: int, ruleset: Optional[str] = None
):
    """
    获取用户在某个谱面上的全部成绩

    Args:
        user_id: 用户 ID
        beatmap_id: 谱面 ID
        ruleset: 游戏模式 (可选，默认使用谱面模式)

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

    params = {}
    if ruleset:
        params["ruleset"] = ruleset

    response = await client.get(url, params=params if params else None)
    get_logger("backend").info(
        f"Requesting endpoint {url} for all scores with user_id {user_id} and beatmap_id {beatmap_id} returned {response.status_code}"
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
