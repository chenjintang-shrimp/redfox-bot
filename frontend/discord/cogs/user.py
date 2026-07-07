import io
from dataclasses import asdict

from discord.ext import commands
from discord import app_commands, File

from adapters.discord_adapter import DiscordAdapter
from services import UserService
from renderer.user import render_user_card_image, render_user_info
from utils.strings import format_template
from utils.logger import get_logger


class User(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.adapter = DiscordAdapter()
        get_logger("cogs.user").info("Cog User Loaded")

    @commands.hybrid_command(name="info", description="Query User info.")
    @app_commands.describe(user="osu!username or @mention")
    async def info(self, ctx: commands.Context, user: str | None = None):
        await ctx.defer()

        try:
            username = await self.adapter.resolve_username(ctx, user)
            msg = await render_user_info(username, locale="en")
            await ctx.send(msg)
        except Exception as e:
            await self.adapter.handle_error(ctx, e, locale="en")

    @commands.hybrid_command(
        name="uinfo", description="Query User info with image card."
    )
    @app_commands.describe(user="osu!username or @mention")
    async def uinfo(self, ctx: commands.Context, user: str | None = None):
        """查询用户信息（图片卡片版）"""
        await ctx.defer()

        try:
            username = await self.adapter.resolve_username(ctx, user)
            user_data = await UserService.get_user_info(username)
            image = await render_user_card_image(asdict(user_data))
            await ctx.send(file=File(io.BytesIO(image), f"{username}_card.png"))
        except Exception as e:
            await self.adapter.handle_error(ctx, e, locale="en")

    @commands.hybrid_command(name="bind", description="Bind user to the bot")
    @app_commands.describe(user="osu!username or @mention")
    async def bind(self, ctx: commands.Context, user: str):
        await ctx.defer()

        try:
            context = await self.adapter.get_user_context(ctx)
            user_info = await UserService.bind_user(context, user)
            msg = format_template(
                "USER_BIND_SUCCESS_TEMPLATE", locale="en", username=user_info.username
            )
            await ctx.send(msg)
        except Exception as e:
            await self.adapter.handle_error(ctx, e, locale="en")

    @commands.hybrid_command(
        name="unbind", description="Unbind your osu! account from the bot"
    )
    async def unbind(self, ctx: commands.Context):
        await ctx.defer()

        try:
            context = await self.adapter.get_user_context(ctx)
            deleted = await UserService.unbind_user(context)
            if deleted:
                msg = format_template("USER_UNBIND_SUCCESS_TEMPLATE", locale="en")
            else:
                msg = format_template(
                    "USER_NOT_BOUND_TEMPLATE", locale="en", user="You"
                )
            await ctx.send(msg)
        except Exception as e:
            await self.adapter.handle_error(ctx, e, locale="en")

    @commands.hybrid_command(
        name="set_gamemode", description="Set your default game mode for score queries"
    )
    @app_commands.describe(
        gamemode="Game mode (e.g., osu, taiko, fruits, mania, or custom)"
    )
    async def set_gamemode_cmd(
        self, ctx: commands.Context, gamemode: str | None = None
    ):
        """设置默认游戏模式"""
        await ctx.defer()

        try:
            context = await self.adapter.get_user_context(ctx)

            if gamemode is None:
                # 显示当前设置
                current_mode = await UserService.get_gamemode(context)
                if current_mode:
                    msg = format_template(
                        "GAMEMODE_CURRENT", gamemode=current_mode, locale="en"
                    )
                else:
                    msg = format_template("GAMEMODE_NOT_SET", locale="en")
                await ctx.send(msg)
                return

            # 设置游戏模式
            success = await UserService.set_gamemode(context, gamemode)
            if success:
                msg = format_template(
                    "GAMEMODE_SET_SUCCESS", gamemode=gamemode, locale="en"
                )
            else:
                msg = format_template("GAMEMODE_SET_FAILED_NOT_BOUND", locale="en")
            await ctx.send(msg)
        except Exception as e:
            await self.adapter.handle_error(ctx, e, locale="en")


async def setup(bot: commands.Bot):
    await bot.add_cog(User(bot))
