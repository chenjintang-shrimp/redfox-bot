import io

from frontend.discord.util import resolve_username
from backend.user import bind_user, get_user_info, unbind_user
from backend.expections.user import UserQueryError, BindExistError
from renderer.user import render_user_card_image
from utils.logger import get_logger
from utils.i18n import get_i18n
from discord.ext import commands
from discord import app_commands, File

# Discord 平台 i18n 实例
i18n = get_i18n("discord")


class User(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        get_logger("cogs.user").info("Cog User Loaded")

    @commands.hybrid_command(name="info", description="Query User info.")
    @app_commands.describe(user="osu!username or @mention")
    async def info(self, ctx: commands.Context, user: str | None = None):
        await ctx.defer()

        username = await resolve_username(ctx, user)
        try:
            user_info = await get_user_info(username)
            msg = i18n.get("user.info_text",
                username=user_info.get("username"),
                id=user_info.get("id"),
                playmode=user_info.get("playmode"),
                pp=user_info.get("statistics", {}).get("pp", 0),
                global_rank=user_info.get("statistics", {}).get("global_rank", "N/A")
            )
            await ctx.send(msg)
        except UserQueryError:
            await ctx.send(i18n.get("user.not_found", username=username))
        except Exception as e:
            await ctx.send(i18n.get("user.query_failed", error=str(e)))

    @commands.hybrid_command(
        name="uinfo", description="Query User info with image card."
    )
    @app_commands.describe(user="osu!username or @mention")
    async def uinfo(self, ctx: commands.Context, user: str | None = None):
        """查询用户信息（图片卡片版）"""
        await ctx.defer()

        username = await resolve_username(ctx, user)
        try:
            user_data = await get_user_info(username)
            image = await render_user_card_image(user_data)
            await ctx.send(file=File(io.BytesIO(image), f"{username}_card.png"))
        except UserQueryError:
            await ctx.send(i18n.get("user.not_found", username=username))
        except Exception:
            await ctx.send(i18n.get("errors.render_failed"))

    @commands.hybrid_command(name="bind", description="Bind user to the bot")
    @app_commands.describe(user="osu!username or @mention")
    async def bind(self, ctx: commands.Context, user: str):
        await ctx.defer()

        try:
            await bind_user(ctx.author.id, user)
            await ctx.send(i18n.get("user.bind_success", username=user))
        except UserQueryError:
            await ctx.send(i18n.get("user.bind_user_not_found", username=user))
        except BindExistError:
            await ctx.send(i18n.get("user.bind_exists"))
        except Exception as e:
            await ctx.send(i18n.get("user.bind_failed", error=str(e)))

    @commands.hybrid_command(
        name="unbind", description="Unbind your osu! account from the bot"
    )
    async def unbind(self, ctx: commands.Context):
        await ctx.defer()

        try:
            deleted = await unbind_user(ctx.author.id)
            if deleted:
                await ctx.send(i18n.get("user.unbind_success"))
            else:
                await ctx.send(i18n.get("user.unbind_not_bound"))
        except Exception as e:
            await ctx.send(i18n.get("user.unbind_failed", error=str(e)))


async def setup(bot: commands.Bot):
    await bot.add_cog(User(bot))
