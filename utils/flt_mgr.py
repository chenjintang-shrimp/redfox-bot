"""
FltMgr - Filter Manager
Simple direct-registration filter manager.

Minifilters are directly imported and registered at startup.
No YAML scanning, no topological sort, no dependency resolution.
"""

from typing import Any, Callable

from utils.logger import get_logger

logger = get_logger("utils.flt_mgr")


class FltMgr:
    """
    Filter Manager
    Manages minifilter registration and execution.

    Simple dict-based: hook_name -> list of process functions.
    """

    def __init__(self) -> None:
        self._filters: dict[str, list[Callable[[dict], Any]]] = {}

    def register(self, hook_name: str, process_func: Callable[[dict], Any]) -> None:
        """Register a processor function for a hook."""
        if hook_name not in self._filters:
            self._filters[hook_name] = []
        self._filters[hook_name].append(process_func)
        func_name = getattr(process_func, "__name__", type(process_func).__name__)
        logger.debug(f"[FltMgr] 注册处理器: {func_name} -> [{hook_name}]")

    async def apply_async(self, hook_name: str, data: dict) -> dict:
        """
        Apply all registered filters for the given hook (async).

        Args:
            hook_name: renderer name
            data: original data

        Returns:
            processed data
        """
        import inspect

        chain = self._filters.get(hook_name, [])
        if not chain:
            return data

        result = data.copy()
        for process_func in chain:
            try:
                if inspect.iscoroutinefunction(process_func):
                    result = await process_func(result)
                else:
                    result = process_func(result)
            except Exception as e:
                func_name = getattr(process_func, "__name__", "unknown")
                logger.error(f"[FltMgr] 执行失败 {func_name}: {e}")

        return result

    def apply(self, hook_name: str, data: dict) -> dict:
        """
        Apply all registered filters for the given hook (sync).
        """
        chain = self._filters.get(hook_name, [])
        if not chain:
            return data

        result = data.copy()
        for process_func in chain:
            try:
                result = process_func(result)
            except Exception as e:
                func_name = getattr(process_func, "__name__", "unknown")
                logger.error(f"[FltMgr] 执行失败 {func_name}: {e}")

        return result


_flt_mgr: FltMgr | None = None


def _register_known_filters(flt_mgr: FltMgr) -> None:
    """Directly import and register all known minifilters."""
    from minifilters.beatmap_card_basic import process as beatmap_card_process
    from minifilters.score_card_basic import process as score_card_process
    from minifilters.score_list_basic import process as score_list_process
    from minifilters.today_bp_basic import process as today_bp_process

    # beatmap_card_basic: hooks beatmap_card
    flt_mgr.register("beatmap_card", beatmap_card_process)

    # score_card_basic: hooks user_beatmap_score_card, user_recent_score_card
    flt_mgr.register("user_beatmap_score_card", score_card_process)
    flt_mgr.register("user_recent_score_card", score_card_process)

    # score_list_basic: hooks user_score_list
    flt_mgr.register("user_score_list", score_list_process)

    # today_bp_basic: hooks user_today_bp
    flt_mgr.register("user_today_bp", today_bp_process)

    logger.info("[FltMgr] 已注册 4 个 minifilter")


def get_flt_mgr() -> FltMgr:
    """获取全局 FltMgr 实例（懒加载，完整初始化）"""
    global _flt_mgr
    if _flt_mgr is None:
        _flt_mgr = FltMgr()
        _register_known_filters(_flt_mgr)
    return _flt_mgr


def apply_minifilters(hook_name: str, data: dict) -> dict:
    """
    便捷函数：应用指定 hook 的所有 minifilter（同步版本）

    Args:
        hook_name: renderer 名称
        data: 原始数据

    Returns:
        处理后的数据
    """
    return get_flt_mgr().apply(hook_name, data)


async def apply_minifilters_async(hook_name: str, data: dict) -> dict:
    """
    便捷函数：应用指定 hook 的所有 minifilter（异步版本）

    Args:
        hook_name: renderer 名称
        data: 原始数据

    Returns:
        处理后的数据
    """
    return await get_flt_mgr().apply_async(hook_name, data)


def init_flt_mgr() -> FltMgr:
    """
    主动初始化 FltMgr（建议在 bot 启动时调用）

    Returns:
        初始化完成的 FltMgr 实例
    """
    return get_flt_mgr()
