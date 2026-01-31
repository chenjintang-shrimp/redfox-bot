"""
FltMgr - Filter Manager
minifilter 管理器，负责拓扑排序和依赖解析

启动时预分析所有链条，运行时直接调用
"""

import importlib
from collections import deque
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

import yaml

from utils.logger import get_logger
from utils.variable import working_dir

logger = get_logger("utils.flt_mgr")


@dataclass
class MinifilterInfo:
    """minifilter 信息"""

    name: str
    version: str
    description: str
    hooks: list[str]  # 要 hook 的 renderer 名称
    depends: list[str]  # 依赖的其他 minifilter
    module_path: str  # 模块路径，如 "minifilters.user_card_basic"
    process_func: Callable[[dict], dict] | None = None  # 加载后填充


class FltMgr:
    """
    Filter Manager
    管理所有 minifilter 的加载、排序和执行

    启动时：scan → build_chains → load_processors → compile_chains
    运行时：直接调用预编译的链
    """

    def __init__(self):
        self._minifilters: dict[str, MinifilterInfo] = {}  # name -> info
        self._hooks: dict[str, list[str]] = {}  # hook_name -> [minifilter_names]
        self._sorted_chains: dict[str, list[str]] = {}  # hook_name -> [sorted_names]
        # 预编译的执行链: hook_name -> 可直接调用的函数列表
        self._compiled_chains: dict[str, list[Callable[[dict], dict]]] = {}

    def scan(self, package_path: Path | None = None) -> None:
        """
        扫描 minifilters 目录，加载所有配置
        """
        if package_path is None:
            package_path = working_dir / "minifilters"

        logger.info(f"[FltMgr] 开始扫描目录: {package_path}")

        for subdir in package_path.iterdir():
            if not subdir.is_dir():
                continue

            config_file = subdir / "minifilter.yaml"
            if not config_file.exists():
                logger.debug(f"[FltMgr] 跳过 {subdir.name}: 无配置文件")
                continue

            try:
                self._load_minifilter(subdir)
            except Exception as e:
                logger.error(f"[FltMgr] 加载 {subdir.name} 失败: {e}")

        logger.info(f"[FltMgr] 扫描完成，共加载 {len(self._minifilters)} 个 minifilter")

    def _load_minifilter(self, subdir: Path) -> None:
        """加载单个 minifilter"""
        config_file = subdir / "minifilter.yaml"

        with open(config_file, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)

        name = config["name"]

        info = MinifilterInfo(
            name=name,
            version=config.get("version", "0.0.1"),
            description=config.get("description", ""),
            hooks=config.get("hooks", []),
            depends=config.get("depends", []),
            module_path=f"minifilters.{subdir.name}",
        )

        self._minifilters[name] = info

        # 注册到 hooks
        for hook in info.hooks:
            if hook not in self._hooks:
                self._hooks[hook] = []
            self._hooks[hook].append(name)

        logger.info(f"[FltMgr] 已加载: {name} (hooks: {info.hooks}, depends: {info.depends})")

    def build_chains(self) -> None:
        """
        为每个 hook 构建执行链（拓扑排序）
        如果有循环依赖，该 hook 的所有 minifilter 都被禁用
        """
        logger.info("[FltMgr] 开始构建执行链")

        for hook_name, minifilter_names in self._hooks.items():
            try:
                sorted_names = self._topological_sort(minifilter_names)
                self._sorted_chains[hook_name] = sorted_names
                logger.info(f"[FltMgr] 执行链 [{hook_name}]: {' -> '.join(sorted_names)}")
            except ValueError as e:
                logger.error(f"[FltMgr] 循环依赖 detected [{hook_name}]: {e}")
                logger.error(f"[FltMgr] 禁用该 hook 的所有 minifilter: {minifilter_names}")
                self._sorted_chains[hook_name] = []  # 空链 = 禁用

    def _topological_sort(self, names: list[str]) -> list[str]:
        """
        拓扑排序（Kahn 算法）

        Args:
            names: 需要排序的 minifilter 名称列表

        Returns:
            排序后的名称列表

        Raises:
            ValueError: 存在循环依赖
        """
        # 构建子图（只包含指定的 minifilters）
        subgraph = {name: set() for name in names}

        for name in names:
            info = self._minifilters[name]
            # 只保留在列表内的依赖
            valid_deps = [d for d in info.depends if d in names]
            subgraph[name] = set(valid_deps)

        # 计算入度
        in_degree = {name: 0 for name in names}
        for deps in subgraph.values():
            for dep in deps:
                in_degree[dep] += 1

        # 找入度为0的节点
        queue = deque([name for name in names if in_degree[name] == 0])
        result = []

        while queue:
            node = queue.popleft()
            result.append(node)

            # 移除该节点的出边
            for other, deps in subgraph.items():
                if node in deps:
                    in_degree[other] -= 1
                    if in_degree[other] == 0:
                        queue.append(other)

        # 检查循环依赖
        if len(result) != len(names):
            unresolved = set(names) - set(result)
            raise ValueError(f"存在循环依赖，无法解析: {unresolved}")

        return result

    def load_processors(self) -> None:
        """
        加载所有 minifilter 的 process 函数
        """
        logger.info("[FltMgr] 开始加载处理器")

        for name, info in self._minifilters.items():
            try:
                module = importlib.import_module(info.module_path)
                info.process_func = module.process
                logger.info(f"[FltMgr] 已加载处理器: {name}")
            except Exception as e:
                logger.error(f"[FltMgr] 加载处理器失败 {name}: {e}")

    def compile_chains(self) -> None:
        """
        预编译所有执行链
        将名称列表转换为可直接调用的函数列表
        """
        logger.info("[FltMgr] 开始编译执行链")

        for hook_name, chain_names in self._sorted_chains.items():
            compiled = []
            for name in chain_names:
                info = self._minifilters[name]
                if info.process_func is not None:
                    compiled.append(info.process_func)
                else:
                    logger.warning(f"[FltMgr] 编译跳过 {name}: 处理器未加载")

            self._compiled_chains[hook_name] = compiled
            logger.info(f"[FltMgr] 已编译 [{hook_name}]: {len(compiled)} 个处理器")

    def apply(self, hook_name: str, data: dict) -> dict:
        """
        应用指定 hook 的所有 minifilter（使用预编译链）

        Args:
            hook_name: renderer 名称
            data: 原始数据

        Returns:
            处理后的数据
        """
        chain = self._compiled_chains.get(hook_name, [])
        if not chain:
            return data

        result = data.copy()
        for process_func in chain:
            try:
                result = process_func(result)
            except Exception as e:
                # 获取函数名用于日志
                func_name = getattr(process_func, "__name__", "unknown")
                logger.error(f"[FltMgr] 执行失败 {func_name}: {e}")
                # 继续执行下一个，不中断

        return result

    def get_chain(self, hook_name: str) -> list[str]:
        """获取指定 hook 的执行链（名称列表）"""
        return self._sorted_chains.get(hook_name, [])

    def get_compiled_chain(self, hook_name: str) -> list[Callable[[dict], dict]]:
        """获取指定 hook 的预编译链（函数列表）"""
        return self._compiled_chains.get(hook_name, [])


# 全局实例
_flt_mgr: FltMgr | None = None


def get_flt_mgr() -> FltMgr:
    """获取全局 FltMgr 实例（懒加载，完整初始化）"""
    global _flt_mgr
    if _flt_mgr is None:
        _flt_mgr = FltMgr()
        _flt_mgr.scan()
        _flt_mgr.build_chains()
        _flt_mgr.load_processors()
        _flt_mgr.compile_chains()
    return _flt_mgr


def apply_minifilters(hook_name: str, data: dict) -> dict:
    """
    便捷函数：应用指定 hook 的所有 minifilter

    Args:
        hook_name: renderer 名称
        data: 原始数据

    Returns:
        处理后的数据
    """
    return get_flt_mgr().apply(hook_name, data)


def init_flt_mgr() -> FltMgr:
    """
    主动初始化 FltMgr（建议在 bot 启动时调用）

    Returns:
        初始化完成的 FltMgr 实例
    """
    return get_flt_mgr()
