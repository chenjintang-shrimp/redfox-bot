import discord
from discord.ext import commands
import os

from utils.logger import get_logger
from utils.variable import BOT_TOKEN


intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    get_logger("Bot").info(f"Bot Online:{bot.user}")


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
