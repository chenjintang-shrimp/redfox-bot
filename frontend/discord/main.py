import discord

from discord.ext import commands
import os


from utils.flt_mgr import init_flt_mgr
from utils.html2image import close_browser, init_browser
from utils.logger import get_logger

from utils.variable import BOT_TOKEN

from utils.scheduler import add_task, start_scheduler, stop_scheduler

from utils.scheduler_registry import auto_discover_tasks, get_all_tasks
from backend.api_client import close_osu_api_client


intents = discord.Intents.default()

intents.message_content = True


bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    get_logger("Bot").info(f"Bot Online:{bot.user}")

    # 自动发现并注册定时任务

    auto_discover_tasks("backend")

    for task in get_all_tasks():
        add_task(task.name, task.func, task.interval, *task.args, **task.kwargs)

    get_logger("Bot").info(f"已注册 {len(get_all_tasks())} 个定时任务")

    await start_scheduler()

    await init_browser()

    init_flt_mgr()


@bot.event
async def on_disconnect():
    await stop_scheduler()
    await close_browser()
    await close_osu_api_client()


# 加载所有 Cog


async def load_cogs():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    cogs_dir = os.path.join(current_dir, "cogs")
    base_module = "frontend.discord.cogs"

    logger = get_logger("Bot")
    logger.debug(f"开始扫描 Cogs 目录: {cogs_dir}")

    for root, _dirs, files in os.walk(cogs_dir):
        # 检查是否是包目录（包含 __init__.py）
        is_package = "__init__.py" in files

        logger.debug(f"扫描目录: {root}, 文件: {files}, 是否包: {is_package}")

        for filename in files:
            if not filename.endswith(".py"):
                continue
            # 跳过以 _ 开头的文件，但保留 __init__.py
            if filename.startswith("_") and filename != "__init__.py":
                continue

            # 计算相对路径
            rel_path = os.path.relpath(root, cogs_dir)
            module_name = filename[:-3]

            if rel_path == ".":
                # 直接在 cogs 目录下
                extension = f"{base_module}.{module_name}"
            else:
                # 在子目录中
                # 统一处理 Windows 和 Linux 的路径分隔符
                sub_package = rel_path.replace(os.sep, ".").replace("/", ".").replace("\\", ".")
                if is_package:
                    # 如果是包，只加载 __init__.py，忽略其他文件
                    # __init__.py 中的 setup 函数应该负责加载包内的所有 Cog
                    if filename != "__init__.py":
                        logger.debug(f"跳过包内文件: {filename} (包 {sub_package} 将通过 __init__.py 加载)")
                        continue
                    extension = f"{base_module}.{sub_package}"
                else:
                    # 非包子目录，按普通模块加载
                    extension = f"{base_module}.{sub_package}.{module_name}"

            logger.debug(f"尝试加载 Cog: {extension}")
            try:
                await bot.load_extension(extension)
                logger.info(f"已加载 Cog: {extension}")
            except Exception as e:
                logger.error(f"加载 Cog 失败 {extension}: {e}")


@bot.event
async def setup_hook():
    from backend.database import create_db_and_tables

    await create_db_and_tables()

    await load_cogs()


def main():
    bot.run(BOT_TOKEN)


if __name__ == "__main__":
    main()
