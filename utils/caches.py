from typing import Any, Optional
from aiocache import Cache

_cache = Cache(Cache.MEMORY)


async def set_cache(key: str, value: Any, ttl: int = 300) -> None:
    """设置缓存"""
    await _cache.set(key, value, ttl=ttl)


async def get_cache(key: str) -> Optional[Any]:
    """获取缓存"""
    return await _cache.get(key)


async def delete_cache(key: str) -> int:
    """删除缓存，返回删除的键数量"""
    return await _cache.delete(key)


async def exists_cache(key: str) -> bool:
    """检查缓存是否存在"""
    return await _cache.exists(key)


async def clear_cache() -> None:
    """清空所有缓存"""
    await _cache.clear()
