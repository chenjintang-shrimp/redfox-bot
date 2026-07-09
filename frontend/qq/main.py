import os
import traceback

import nonebot
from nonebot.adapters.onebot.v11 import Adapter as OneBotV11Adapter
from nonebot.exception import IgnoredException, StopPropagation
from nonebot.matcher import Matcher
from nonebot.message import run_preprocessor, run_postprocessor
from nonebot.typing import T_State
from nonebot.adapters import Bot, Event
from nonebot.adapters.onebot.v11 import (
    GroupMessageEvent,
    MessageEvent,
    PrivateMessageEvent,
)

from frontend.qq import config as qq_config
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

        if qq_config.group_whitelist:
            get_logger("QQBot").info(
                f"群聊白名单已启用: {len(qq_config.group_whitelist)} 个群"
            )
        else:
            get_logger("QQBot").info("群聊白名单为空，允许所有群")
        get_logger("QQBot").info(
            f"私聊命令: {'已启用' if qq_config.private_enabled else '已禁用'}"
        )

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
        """在 matcher 运行前进行群白名单/私聊开关检查并记录日志"""
        # 仅对消息事件做准入控制
        if isinstance(event, MessageEvent):
            if isinstance(event, GroupMessageEvent):
                if not qq_config.is_group_allowed(event.group_id):
                    raise IgnoredException("群聊未在白名单中")
            elif isinstance(event, PrivateMessageEvent):
                if not qq_config.private_enabled:
                    raise IgnoredException("私聊已被禁用")

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
