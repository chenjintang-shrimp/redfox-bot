import asyncio
from typing import Callable, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta

from utils.logger import get_logger

logger = get_logger("scheduler")


@dataclass
class ScheduledTask:
    """定时任务定义"""

    name: str
    func: Callable[..., Any]
    interval: int
    args: tuple = field(default_factory=tuple)
    kwargs: dict = field(default_factory=dict)
    enabled: bool = True
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None
    run_count: int = 0
    error_count: int = 0


# 模块级私有状态
_tasks: dict[str, ScheduledTask] = {}
_running_tasks: dict[str, asyncio.Task] = {}
_started: bool = False
_lock = asyncio.Lock()


async def _run_loop(task: ScheduledTask) -> None:
    """任务执行循环"""
    logger.debug(f"任务 {task.name} 开始运行")

    while task.enabled:
        try:
            logger.debug(f"执行任务: {task.name}")
            await task.func(*task.args, **task.kwargs)

            task.last_run = datetime.now()
            task.run_count += 1

            task.next_run = datetime.now() + timedelta(seconds=task.interval)
            await asyncio.sleep(task.interval)

        except asyncio.CancelledError:
            logger.debug(f"任务 {task.name} 被取消")
            raise
        except Exception as e:
            task.error_count += 1
            logger.error(f"任务 {task.name} 执行失败: {e}", exc_info=True)


def add_task(
    name: str, func: Callable[..., Any], interval: int, *args, **kwargs
) -> ScheduledTask:
    """
    添加定时任务
    :param name: 任务名称（唯一标识）
    :param func: 异步函数
    :param interval: 执行间隔（秒）
    :param args: 函数位置参数
    :param kwargs: 函数关键字参数
    """
    if name in _tasks:
        logger.warning(f"任务 {name} 已存在，将被覆盖")
        remove_task(name)

    task = ScheduledTask(
        name=name, func=func, interval=interval, args=args, kwargs=kwargs
    )
    _tasks[name] = task
    logger.debug(f"已添加定时任务: {name}, 间隔: {interval}s")
    return task


def remove_task(name: str) -> bool:
    """移除定时任务"""
    if name not in _tasks:
        return False

    if name in _running_tasks:
        _running_tasks[name].cancel()
        del _running_tasks[name]

    del _tasks[name]
    logger.debug(f"任务 {name} 已移除")
    return True


def enable_task(name: str) -> bool:
    """启用指定任务"""
    if name not in _tasks:
        return False
    _tasks[name].enabled = True
    logger.debug(f"任务 {name} 已启用")
    return True


def disable_task(name: str) -> bool:
    """禁用指定任务"""
    if name not in _tasks:
        return False
    _tasks[name].enabled = False
    logger.debug(f"任务 {name} 已禁用")
    return True


async def start_scheduler() -> None:
    """启动调度器"""
    global _started

    if _started:
        logger.warning("调度器已在运行")
        return

    async with _lock:
        for name, task in _tasks.items():
            if task.enabled and name not in _running_tasks:
                _running_tasks[name] = asyncio.create_task(
                    _run_loop(task), name=f"scheduler_{name}"
                )

    _started = True
    logger.info(f"调度器已启动，共 {len(_running_tasks)} 个任务")


async def stop_scheduler() -> None:
    """停止调度器"""
    global _started

    if not _started:
        return

    async with _lock:
        for name, task in list(_running_tasks.items()):
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
            logger.debug(f"任务 {name} 已停止")

        _running_tasks.clear()

    _started = False
    logger.info("调度器已停止")


def get_task_info(name: str) -> Optional[dict]:
    """获取任务信息"""
    if name not in _tasks:
        return None

    task = _tasks[name]
    return {
        "name": task.name,
        "interval": task.interval,
        "enabled": task.enabled,
        "last_run": task.last_run,
        "next_run": task.next_run,
        "run_count": task.run_count,
        "error_count": task.error_count,
        "is_running": name in _running_tasks,
    }


def list_tasks() -> list[dict]:
    """列出所有任务信息"""
    return [info for name in _tasks.keys() if (info := get_task_info(name)) is not None]


def is_running() -> bool:
    """调度器是否正在运行"""
    return _started


def clear_all_tasks() -> None:
    """清除所有任务（调度器停止时可用）"""
    global _tasks
    _tasks.clear()
    logger.debug("所有任务已清除")
