import discord

from discord.ext import commands
import os


from minifilters import auto_discover_minifilters

from utils.html2image import close_browser, init_browser
from utils.logger import get_logger

from utils.variable import BOT_TOKEN

from utils.scheduler import add_task, start_scheduler, stop_scheduler

from utils.scheduler_registry import auto_discover_tasks, get_all_tasks



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

    auto_discover_minifilters("minifilters")



@bot.event

async def on_disconnect():

    await stop_scheduler()

    await close_browser()



# 加载所有 Cog

async def load_cogs():

    current_dir = os.path.dirname(os.path.abspath(__file__))

    cogs_dir = os.path.join(current_dir, "cogs")

    for filename in os.listdir(cogs_dir):

        if filename.endswith(".py"):

            await bot.load_extension(f"frontend.discord.cogs.{filename[:-3]}")



@bot.event

async def setup_hook():

    from backend.database import create_db_and_tables


    await create_db_and_tables()

    await load_cogs()



def main():

    bot.run(BOT_TOKEN)



if __name__ == "__main__":
    main()

