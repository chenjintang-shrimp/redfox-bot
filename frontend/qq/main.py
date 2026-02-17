import os
import traceback

import nonebot
from nonebot.adapters.onebot.v11 import Adapter as OneBotV11Adapter
from nonebot.exception import IgnoredException, StopPropagation
from nonebot.matcher import Matcher
from nonebot.message import run_preprocessor, run_postprocessor
from nonebot.typing import T_State
from nonebot.adapters import Bot, Event

from utils.flt_mgr import init_flt_mgr
from utils.html2image import close_browser, init_browser
from utils.logger import get_logger
from utils.scheduler import start_scheduler, stop_scheduler
from utils.scheduler_registry import auto_discover_tasks, get_all_tasks
from backend.database import create_db_and_tables
from backend.api_client import close_osu_api_client

logger = get_logger("qq.exception_handler")


def main():
    # 检查 .env.qq 配置文件
    env_file = ".env.qq"
    if os.path.exists(env_file):
        nonebot.init(_env_file=env_file)
    else:
        print(f"警告: 配置文件 {env_file} 不存在，请复制 .env.qq.example 为 {env_file}")
        print("使用默认配置启动...")
        nonebot.init()

    driver = nonebot.get_driver()
    driver.register_adapter(OneBotV11Adapter)

    @driver.on_startup
    async def on_startup():
        get_logger("QQBot").info("QQ Bot starting...")

        await create_db_and_tables()

        auto_discover_tasks("backend")
        for task in get_all_tasks():
            from utils.scheduler import add_task

            add_task(task.name, task.func, task.interval, *task.args, **task.kwargs)

        get_logger("QQBot").info(f"已注册 {len(get_all_tasks())} 个定时任务")

        await start_scheduler()
        await init_browser()
        init_flt_mgr()

        get_logger("QQBot").info("QQ Bot started!")

    @driver.on_shutdown
    async def on_shutdown():
        get_logger("QQBot").info("QQ Bot shutting down...")
        await stop_scheduler()
        await close_browser()
        await close_osu_api_client()

    nonebot.load_plugins("frontend/qq/plugins")

    # 注册全局异常处理器
    _register_exception_handlers()

    nonebot.run()


def _register_exception_handlers():
    """注册全局异常处理器，捕获详细的 matcher 执行错误"""

    @run_preprocessor
    async def on_run_preprocessor(
        bot: Bot, event: Event, state: T_State, matcher: Matcher
    ):
        """在 matcher 运行前记录日志"""
        logger.debug(f"Running matcher: {matcher.type}, module: {matcher.module_name}")

    @run_postprocessor
    async def on_run_postprocessor(
        bot: Bot,
        event: Event,
        state: T_State,
        matcher: Matcher,
        exception: Exception | None,
    ):
        """在 matcher 运行后捕获异常，并向用户发送错误信息"""
        if exception is not None:
            # 忽略框架内部控制的异常
            if isinstance(exception, (IgnoredException, StopPropagation)):
                return

            # 构建详细的错误信息
            error_type = type(exception).__name__
            error_msg = str(exception)
            stack_trace = traceback.format_exc()

            # 记录详细的异常信息到日志
            logger.error("=" * 60)
            logger.error(f"Matcher failed: {matcher.type}")
            logger.error(f"Module: {matcher.module_name}")
            logger.error(f"Exception type: {error_type}")
            logger.error(f"Exception message: {error_msg}")
            logger.error(f"Stack trace:\n{stack_trace}")
            logger.error("=" * 60)

            # 向用户发送友好的错误提示（包含技术细节）
            try:
                from nonebot.adapters.onebot.v11 import (
                    MessageEvent,
                    PrivateMessageEvent,
                )

                if isinstance(event, MessageEvent):
                    user_msg = "❌ 命令执行出错\n"
                    user_msg += f"类型: {error_type}\n"
                    user_msg += f"信息: {error_msg[:200]}"  # 限制长度
                    if len(error_msg) > 200:
                        user_msg += "..."

                    # 私聊可以发详细点，群聊简短点
                    if isinstance(event, PrivateMessageEvent):
                        user_msg += f"\n\n详细:\n{stack_trace[:500]}"
                        if len(stack_trace) > 500:
                            user_msg += "..."

                    await bot.send(event, user_msg)
            except Exception as send_err:
                logger.error(f"发送错误信息给用户失败: {send_err}")


if __name__ == "__main__":
    main()
