import io

from frontend.discord.util import resolve_username
from renderer.user import (
    render_binding_user,
    render_user_card_image,
    render_user_info,
    render_unbinding_user,
)
from backend.user import get_user_info, set_user_gamemode, get_user_gamemode
from utils.logger import get_logger
from discord.ext import commands
from discord import app_commands, File


class User(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        get_logger("cogs.user").info("Cog User Loaded")

    @commands.hybrid_command(name="info", description="Query User info.")
    @app_commands.describe(user="osu!username or @mention")
    async def info(self, ctx: commands.Context, user: str | None = None):
        await ctx.defer()

        username = await resolve_username(ctx, user)
        msg = await render_user_info(username, locale="en")  # type: ignore[call-arg]
        await ctx.send(msg)

    @commands.hybrid_command(
        name="uinfo", description="Query User info with image card."
    )
    @app_commands.describe(user="osu!username or @mention")
    async def uinfo(self, ctx: commands.Context, user: str | None = None):
        """查询用户信息（图片卡片版）"""
        await ctx.defer()

        username = await resolve_username(ctx, user)
        user_data = await get_user_info(username)
        image = await render_user_card_image(user_data)

        await ctx.send(file=File(io.BytesIO(image), f"{username}_card.png"))

    @commands.hybrid_command(name="bind", description="Bind user to the bot")
    @app_commands.describe(user="osu!username or @mention")
    async def bind(self, ctx: commands.Context, user: str):
        await ctx.defer()

        msg = await render_binding_user(ctx.author.id, user, locale="en")  # type: ignore[call-arg]
        await ctx.send(msg)

    @commands.hybrid_command(
        name="unbind", description="Unbind your osu! account from the bot"
    )
    async def unbind(self, ctx: commands.Context):
        await ctx.defer()

        msg = await render_unbinding_user(ctx.author.id, locale="en")  # type: ignore[call-arg]
        await ctx.send(msg)

    @commands.hybrid_command(
        name="set_gamemode", description="Set your default game mode for score queries"
    )
    @app_commands.describe(gamemode="Game mode (e.g., osu, taiko, fruits, mania, or custom)")
    async def set_gamemode_cmd(self, ctx: commands.Context, gamemode: str | None = None):
        """设置默认游戏模式"""
        await ctx.defer()

        discord_id = ctx.author.id

        if gamemode is None:
            # 显示当前设置
            current_mode = await get_user_gamemode(discord_id)
            if current_mode:
                await ctx.send(f"Current default game mode: {current_mode}")
            else:
                await ctx.send("No default game mode set")
            return

        # 设置游戏模式（不限制输入，支持任意私服模式）
        success = await set_user_gamemode(discord_id, gamemode)
        if success:
            await ctx.send(f"Successfully set default game mode to: {gamemode}")
        else:
            await ctx.send("Please bind your osu! account first using `/bind <username>`")


async def setup(bot: commands.Bot):
    await bot.add_cog(User(bot))
