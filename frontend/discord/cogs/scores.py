import io
import traceback

from discord import File, app_commands
from discord.ext import commands
from discord.ext.commands import Cog

from adapters.discord_adapter import DiscordAdapter
from models.context import UserContext
from services import UserService, ScoreService
from renderer.scores import (
    render_user_beatmap_scores,
    render_user_score_list,
    render_user_recent_score,
    render_user_today_bp,
    render_user_beatmap_score_card,
    render_user_recent_score_card,
    render_user_score_list_image,
    render_user_today_bp_image,
)
from utils.logger import get_logger

from ._views import ScoresPaginationView, UserScoresPaginationView, TodayBPPaginationView

logger = get_logger("cogs.scores")


class Scores(Cog):
    def __init__(self, bot):
        self.bot = bot
        self.adapter = DiscordAdapter()
        get_logger("cogs.scores").info("Cog scores Loaded")

    async def _get_score_target(
        self, ctx: commands.Context, user_arg: str | None
    ) -> tuple[UserContext, int, str]:
        """获取用户上下文、目标 osu! 用户 ID 和用户名

        Returns:
            tuple: (UserContext, user_id, username)
        """
        context = await self.adapter.get_user_context(ctx)
        username = await self.adapter.resolve_username(ctx, user_arg)
        user_info = await UserService.get_user_info(username)
        return context, user_info.id, username

    @commands.hybrid_command(
        name="ss", description="Query your all scores on a beatmap"
    )
    @app_commands.describe(beatmap_id="beatmap id")
    async def ss(self, ctx: commands.Context, beatmap_id: int):
        await ctx.defer()

        try:
            _, user_id, _ = await self._get_score_target(ctx, None)
            total_pages = await ScoreService.get_page_count(user_id, beatmap_id)
            content = await render_user_beatmap_scores(
                user_id, beatmap_id, 1, locale="en"
            )

            if total_pages > 1:
                view = ScoresPaginationView(user_id, beatmap_id, ctx.author.id, total_pages)
                await ctx.send(content=content, view=view)
            else:
                await ctx.send(content=content)
        except Exception as e:
            await self.adapter.handle_error(ctx, e, locale="en")

    @commands.hybrid_command(
        name="ps", description="Query your recent passed scores (24h)"
    )
    @app_commands.describe(user="osu! username or mention")
    async def ps(self, ctx: commands.Context, user: str | None = None):
        await ctx.defer()

        try:
            _, user_id, _ = await self._get_score_target(ctx, user)
            content = await render_user_score_list(
                user_id, "recent", include_fails=False, page=1, locale="en"
            )
            total_pages = await ScoreService.get_user_scores_page_count(
                user_id, "recent", include_fails=False
            )

            if total_pages > 1:
                view = UserScoresPaginationView(
                    user_id, "recent", False, ctx.author.id, total_pages
                )
                await ctx.send(content=content, view=view)
            else:
                await ctx.send(content=content)
        except Exception as e:
            await self.adapter.handle_error(ctx, e, locale="en")

    @commands.hybrid_command(
        name="rs", description="Query your recent scores (24h, including fails)"
    )
    @app_commands.describe(user="osu! username or mention")
    async def rs(self, ctx: commands.Context, user: str | None = None):
        await ctx.defer()

        try:
            _, user_id, _ = await self._get_score_target(ctx, user)
            content = await render_user_score_list(
                user_id, "recent", include_fails=True, page=1, locale="en"
            )
            total_pages = await ScoreService.get_user_scores_page_count(
                user_id, "recent", include_fails=True
            )

            if total_pages > 1:
                view = UserScoresPaginationView(
                    user_id, "recent", True, ctx.author.id, total_pages
                )
                await ctx.send(content=content, view=view)
            else:
                await ctx.send(content=content)
        except Exception as e:
            await self.adapter.handle_error(ctx, e, locale="en")

    @commands.hybrid_command(
        name="t",
        description="Query your best scores achieved in the last 24 hours (Today's BP)",
    )
    @app_commands.describe(user="osu! username or mention")
    async def t(self, ctx: commands.Context, user: str | None = None):
        await ctx.defer()

        try:
            _, user_id, _ = await self._get_score_target(ctx, user)
            content = await render_user_today_bp(user_id, page=1, locale="en")
            # Note: Today BP page count is not implemented in ScoreService yet
            total_pages = 1

            if total_pages > 1:
                view = TodayBPPaginationView(user_id, ctx.author.id, total_pages)
                await ctx.send(content=content, view=view)
            else:
                await ctx.send(content=content)
        except Exception as e:
            await self.adapter.handle_error(ctx, e, locale="en")

    @commands.hybrid_command(name="p", description="Query your latest passed score")
    @app_commands.describe(user="osu! username or mention")
    async def p(self, ctx: commands.Context, user: str | None = None):
        await ctx.defer()

        try:
            context, user_id, _ = await self._get_score_target(ctx, user)
            gamemode = await UserService.get_gamemode(context)
            content = await render_user_recent_score(
                user_id, "recent", include_fails=False, locale="en", mode=gamemode
            )
            await ctx.send(content=content)
        except Exception as e:
            await self.adapter.handle_error(ctx, e, locale="en")

    @commands.hybrid_command(
        name="r", description="Query your latest score (including fails)"
    )
    @app_commands.describe(user="osu! username or mention")
    async def r(self, ctx: commands.Context, user: str | None = None):
        await ctx.defer()

        try:
            context, user_id, _ = await self._get_score_target(ctx, user)
            gamemode = await UserService.get_gamemode(context)
            content = await render_user_recent_score(
                user_id, "recent", include_fails=True, locale="en", mode=gamemode
            )
            await ctx.send(content=content)
        except Exception as e:
            await self.adapter.handle_error(ctx, e, locale="en")

    # ============ 图片版本命令 ============

    @commands.hybrid_command(
        name="uss", description="Query your all scores on a beatmap (image card)"
    )
    @app_commands.describe(beatmap_id="beatmap id")
    async def uss(self, ctx: commands.Context, beatmap_id: int):
        """查询谱面成绩（图片卡片版）"""
        await ctx.defer()

        try:
            _, user_id, _ = await self._get_score_target(ctx, None)
            image = await render_user_beatmap_score_card(user_id, beatmap_id)
            await ctx.send(file=File(io.BytesIO(image), f"score_{beatmap_id}.png"))
        except Exception as e:
            await self.adapter.handle_error(ctx, e, locale="en")

    @commands.hybrid_command(
        name="ups", description="Query your recent passed scores (image card)"
    )
    @app_commands.describe(user="osu! username or mention")
    async def ups(self, ctx: commands.Context, user: str | None = None):
        """查询最近通过成绩（图片卡片版）"""
        await ctx.defer()

        try:
            context, user_id, username = await self._get_score_target(ctx, user)
            gamemode = await UserService.get_gamemode(context)

            image = await render_user_score_list_image(
                user_id, username, score_type="recent", include_fails=False, mode=gamemode
            )
            await ctx.send(file=File(io.BytesIO(image), f"{username}_recent.png"))
        except Exception as e:
            await self.adapter.handle_error(ctx, e, locale="en")

    @commands.hybrid_command(
        name="urs", description="Query your recent scores including fails (image card)"
    )
    @app_commands.describe(user="osu! username or mention")
    async def urs(self, ctx: commands.Context, user: str | None = None):
        """查询最近成绩包含失败（图片卡片版）"""
        await ctx.defer()

        try:
            context, user_id, username = await self._get_score_target(ctx, user)
            gamemode = await UserService.get_gamemode(context)

            image = await render_user_score_list_image(
                user_id, username, score_type="recent", include_fails=True, mode=gamemode
            )
            await ctx.send(file=File(io.BytesIO(image), f"{username}_recent_all.png"))
        except Exception as e:
            await self.adapter.handle_error(ctx, e, locale="en")

    @commands.hybrid_command(
        name="ut", description="Query your today's BP (image card)"
    )
    @app_commands.describe(user="osu! username or mention")
    async def ut(self, ctx: commands.Context, user: str | None = None):
        """查询今日BP（图片卡片版）"""
        await ctx.defer()

        try:
            context, user_id, username = await self._get_score_target(ctx, user)
            gamemode = await UserService.get_gamemode(context)

            image = await render_user_today_bp_image(user_id, username, mode=gamemode)
            await ctx.send(file=File(io.BytesIO(image), f"{username}_today_bp.png"))
        except Exception as e:
            await self.adapter.handle_error(ctx, e, locale="en")

    @commands.hybrid_command(
        name="up", description="Query your latest passed score (image card)"
    )
    @app_commands.describe(user="osu! username or mention")
    async def up(self, ctx: commands.Context, user: str | None = None):
        """查询最新通过成绩（图片卡片版）"""
        await ctx.defer()

        try:
            context, user_id, username = await self._get_score_target(ctx, user)
            gamemode = await UserService.get_gamemode(context)

            image = await render_user_recent_score_card(
                user_id, include_fails=False, mode=gamemode
            )
            await ctx.send(file=File(io.BytesIO(image), f"{username}_latest.png"))
        except Exception as e:
            await self.adapter.handle_error(ctx, e, locale="en")

    @commands.hybrid_command(
        name="ur", description="Query your latest score including fails (image card)"
    )
    @app_commands.describe(user="osu! username or mention")
    async def ur(self, ctx: commands.Context, user: str | None = None):
        """查询最新成绩包含失败（图片卡片版）"""
        await ctx.defer()

        try:
            context, user_id, username = await self._get_score_target(ctx, user)
            gamemode = await UserService.get_gamemode(context)

            image = await render_user_recent_score_card(
                user_id, include_fails=True, mode=gamemode
            )
            await ctx.send(file=File(io.BytesIO(image), f"{username}_latest_all.png"))
        except Exception as e:
            await self.adapter.handle_error(ctx, e, locale="en")

    @commands.hybrid_command(name="b", description="Query your best score (single)")
    @app_commands.describe(user="osu! username or mention")
    async def b(self, ctx: commands.Context, user: str | None = None):
        """查询最佳成绩（文字版，单条）"""
        await ctx.defer()

        try:
            context, user_id, _ = await self._get_score_target(ctx, user)
            gamemode = await UserService.get_gamemode(context)

            content = await render_user_score_list(
                user_id,
                "best",
                include_fails=False,
                page=1,
                limit=1,
                locale="en",
                mode=gamemode,
            )
            await ctx.send(content=content)
        except Exception as e:
            await self.adapter.handle_error(ctx, e, locale="en")

    @commands.hybrid_command(name="bs", description="Query your best scores (multiple)")
    @app_commands.describe(
        count="Number of scores (1-100, default 20)", user="osu! username or mention"
    )
    async def bs(self, ctx: commands.Context, count: int = 20, user: str | None = None):
        """查询最佳成绩列表（文字版，多条）

        使用方式:
        /bs 3 - 查询自己的前3个best成绩
        /bs 5 someone - 查询某人的前5个best成绩
        """
        await ctx.defer()
        count = min(max(count, 1), 100)  # 限制 1-100

        try:
            context, user_id, _ = await self._get_score_target(ctx, user)
            gamemode = await UserService.get_gamemode(context)

            content = await render_user_score_list(
                user_id,
                "best",
                include_fails=False,
                page=1,
                limit=count,
                locale="en",
                mode=gamemode,
            )
            await ctx.send(content=content)
        except Exception as e:
            await self.adapter.handle_error(ctx, e, locale="en")

    @commands.hybrid_command(
        name="ub", description="Query your best score (image card, single)"
    )
    @app_commands.describe(user="osu! username or mention")
    async def ub(self, ctx: commands.Context, user: str | None = None):
        """查询最佳成绩（图片卡片版，单条）"""
        await ctx.defer()

        try:
            context, user_id, username = await self._get_score_target(ctx, user)
            gamemode = await UserService.get_gamemode(context)

            image = await render_user_score_list_image(
                user_id,
                username,
                score_type="best",
                include_fails=False,
                count=1,
                mode=gamemode,
            )
            await ctx.send(file=File(io.BytesIO(image), f"{username}_best.png"))
        except Exception as e:
            await self.adapter.handle_error(ctx, e, locale="en")

    @commands.hybrid_command(
        name="ubs", description="Query your best scores (image card, multiple)"
    )
    @app_commands.describe(
        count="Number of scores (1-100, default 20)", user="osu! username or mention"
    )
    async def ubs(
        self, ctx: commands.Context, count: int = 20, user: str | None = None
    ):
        """查询最佳成绩列表（图片卡片版，多条）

        使用方式:
        /ubs 3 - 查询自己的前3个best成绩
        /ubs 5 someone - 查询某人的前5个best成绩
        """
        await ctx.defer()
        count = min(max(count, 1), 100)  # 限制 1-100

        try:
            logger.info("[ubs] 开始执行指令")
            context, user_id, username = await self._get_score_target(ctx, user)
            logger.info(f"[ubs] 获取到 user_id: {user_id}")
            logger.info(f"[ubs] 获取到 username: {username}")
            gamemode = await UserService.get_gamemode(context)
            logger.info(f"[ubs] 获取到 gamemode: {gamemode}")

            logger.info("[ubs] 开始渲染图片")
            image = await render_user_score_list_image(
                user_id,
                username,
                score_type="best",
                include_fails=False,
                count=count,
                mode=gamemode,
            )
            logger.info(f"[ubs] 图片渲染成功，长度: {len(image)} 字节")
            logger.info("[ubs] 准备发送图片")
            await ctx.send(file=File(io.BytesIO(image), f"{username}_best_list.png"))
            logger.info("[ubs] 图片发送成功")
        except Exception as e:
            logger.error(f"[ubs] 发生错误: {e}")
            logger.error(traceback.format_exc())
            await self.adapter.handle_error(ctx, e, locale="en")


async def setup(bot: commands.Bot):
    await bot.add_cog(Scores(bot))
