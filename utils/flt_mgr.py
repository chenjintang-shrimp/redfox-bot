"""
FltMgr - Filter Manager
Simple direct-registration filter manager.

Minifilters 在启动时由 _register_known_filters 动态扫描 minifilters/ 包发现：
每个子包的 __init__.py 需声明 HOOKS（绑定的 hook 列表）与 process 处理函数。
无 YAML 扫描、无拓扑排序、无依赖解析。
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
    """
    动态扫描 minifilters 包并注册所有 minifilter。

    约定：minifilters/ 下每个子包的 __init__.py 需暴露：
      - HOOKS: list[str]   绑定的 hook 名称列表
      - process: Callable  处理函数（同步或异步均可）
    发现失败的单个 minifilter 不会阻断其它 minifilter 的加载。
    """
    import importlib
    from pathlib import Path

    from minifilters import __file__ as _mf_init

    base_dir = Path(_mf_init).resolve().parent
    count = 0

    for sub in sorted(base_dir.iterdir()):
        if not sub.is_dir() or sub.name.startswith("_"):
            continue
        if not (sub / "__init__.py").exists():
            continue

        module_name = f"minifilters.{sub.name}"
        try:
            module = importlib.import_module(module_name)
        except Exception as e:
            logger.error(f"[FltMgr] 导入 minifilter 失败 {module_name}: {e}")
            continue

        hooks = getattr(module, "HOOKS", None)
        process_func = getattr(module, "process", None)
        if not hooks or process_func is None:
            logger.warning(
                f"[FltMgr] {module_name} 缺少 HOOKS 或 process，跳过"
            )
            continue

        for hook in hooks:
            flt_mgr.register(hook, process_func)
        count += 1

    logger.info(f"[FltMgr] 动态发现并注册 {count} 个 minifilter")


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
