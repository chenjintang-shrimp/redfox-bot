import importlib
import pkgutil
from typing import Callable
from dataclasses import dataclass

from utils.logger import get_logger

logger = get_logger("scheduler_registry")


@dataclass
class TaskDef:
    """任务定义"""
    name: str
    func: Callable
    interval: int
    args: tuple
    kwargs: dict


# 全局任务注册表
_scheduled_tasks: list[TaskDef] = []


def scheduled_task(name: str, interval: int, *args, **kwargs):
    """
    装饰器，用于注册定时任务

    用法:
        @scheduled_task("my_task", interval=300)
        async def my_task():
            pass
    """
    def decorator(func: Callable):
        _scheduled_tasks.append(TaskDef(
            name=name,
            func=func,
            interval=interval,
            args=args,
            kwargs=kwargs
        ))
        logger.debug(f"已注册定时任务: {name}, 间隔: {interval}s")
        return func
    return decorator


def get_all_tasks() -> list[TaskDef]:
    """获取所有已注册的任务"""
    return _scheduled_tasks.copy()


def auto_discover_tasks(package_name: str = "backend") -> None:
    """
    自动扫描包下的所有模块，导入以触发装饰器注册

    :param package_name: 要扫描的包名
    """
    try:
        package = importlib.import_module(package_name)
    except ImportError as e:
        logger.warning(f"无法导入包 {package_name}: {e}")
        return

    if not hasattr(package, "__path__"):
        logger.warning(f"{package_name} 不是包，无法扫描")
        return

    logger.info(f"开始扫描包: {package_name}")
    count = 0

    for _, name, is_pkg in pkgutil.iter_modules(package.__path__):
        full_name = f"{package_name}.{name}"
        try:
            importlib.import_module(full_name)
            count += 1
            logger.debug(f"已导入模块: {full_name}")

            # 递归扫描子包
            if is_pkg:
                auto_discover_tasks(full_name)
        except Exception as e:
            logger.warning(f"导入模块 {full_name} 失败: {e}")

    logger.info(f"扫描完成，共导入 {count} 个模块")


def clear_registry() -> None:
    """清空注册表（主要用于测试）"""
    global _scheduled_tasks
    _scheduled_tasks.clear()
    logger.debug("任务注册表已清空")


def get_task_count() -> int:
    """获取已注册任务数量"""
    return len(_scheduled_tasks)
