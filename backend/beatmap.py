from backend.api_client import get_osu_api_client
from utils.logger import get_logger
from utils.strings import get_api_url
from utils.caches import get_cache, set_cache

from backend.expections.beatmap import BeatmapNotFoundError


async def get_beatmap_info(beatmap_id: int):
    """
    获取谱面详细信息（带缓存，24小时）

    Args:
        beatmap_id: 谱面 ID

    Returns:
        谱面信息字典
    """
    cache_key = f"beatmap:info:{beatmap_id}"

    # 先查缓存
    cached = await get_cache(cache_key)
    if cached:
        get_logger("backend").debug(f"Cache hit for beatmap {beatmap_id}")
        return cached

    # 缓存未命中，请求 API
    client = get_osu_api_client()
    url = get_api_url("beatmap_info", beatmap_id=beatmap_id)

    response = await client.get(url)
    get_logger("backend").info(
        f"Requesting endpoint {url} for beatmap_id {beatmap_id} returned {response.status_code}"
    )

    if response.status_code != 200:
        get_logger("backend").error(
            f"API error: {response.status_code} - {response.text}"
        )
        raise BeatmapNotFoundError(beatmap_id)

    data = response.json()

    # 写入缓存，24小时
    await set_cache(cache_key, data, ttl=86400)

    return data
