import discord

from discord.ext import commands
import importlib
import pkgutil


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
    base_module = "frontend.discord.cogs"
    logger = get_logger("Bot")
    logger.debug(f"开始扫描 Cog 模块: {base_module}")

    pkg = importlib.import_module(base_module)

    for _importer, modname, _ispkg in pkgutil.walk_packages(
        pkg.__path__, prefix=f"{base_module}."
    ):
        simple_name = modname.rsplit(".", 1)[-1]
        if simple_name.startswith("_") and simple_name != "__init__":
            continue

        logger.debug(f"尝试加载 Cog: {modname}")
        try:
            await bot.load_extension(modname)
            logger.info(f"已加载 Cog: {modname}")
        except Exception as e:
            logger.error(f"加载 Cog 失败 {modname}: {e}")


@bot.event
async def setup_hook():
    from backend.database import create_db_and_tables

    await create_db_and_tables()

    await load_cogs()


def main():
    bot.run(BOT_TOKEN)


if __name__ == "__main__":
    main()
