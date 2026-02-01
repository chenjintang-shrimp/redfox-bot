import os

import nonebot
from nonebot.adapters.onebot.v11 import Adapter as OneBotV11Adapter

from utils.flt_mgr import init_flt_mgr
from utils.html2image import close_browser, init_browser
from utils.logger import get_logger
from utils.scheduler import start_scheduler, stop_scheduler
from utils.scheduler_registry import auto_discover_tasks, get_all_tasks
from backend.database import create_db_and_tables


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

    nonebot.load_plugins("frontend/qq/plugins")

    nonebot.run()


if __name__ == "__main__":
    main()
