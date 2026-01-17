import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from frontend.discord.util import resolve_username
from renderer.user import render_binding_user, render_user_info, render_unbinding_user
from utils.logger import get_logger
from discord.ext import commands
from discord import app_commands


class User(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        get_logger("cogs.user").info("Cog User Loaded")

    @commands.hybrid_command(name="info", description="Query User info.")
    @app_commands.describe(user="osu!username or @mention")
    async def info(self, ctx: commands.Context, user: str | None = None):
        await ctx.defer()

        username = await resolve_username(ctx, user)
        msg = await render_user_info(username)
        await ctx.send(msg)

    @commands.hybrid_command(name="bind", description="Bind user to the bot")
    @app_commands.describe(user="osu!username or @mention")
    async def bind(self, ctx: commands.Context, user: str):
        await ctx.defer()

        msg = await render_binding_user(ctx.author.id, user)
        await ctx.send(msg)

    @commands.hybrid_command(name="unbind", description="Unbind your osu! account from the bot")
    async def unbind(self, ctx: commands.Context):
        await ctx.defer()

        msg = await render_unbinding_user(ctx.author.id)
        await ctx.send(msg)

async def setup(bot: commands.Bot):
    await bot.add_cog(User(bot))
