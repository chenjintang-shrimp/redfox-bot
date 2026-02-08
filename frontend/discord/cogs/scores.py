import discord
from discord import app_commands
from discord.ext import commands
from discord.ext.commands import Cog

import io

from discord import File

from frontend.discord.util import resolve_username
from backend.user import get_user_info, get_user_gamemode
from renderer.scores import (
    render_user_beatmap_scores,
    get_scores_page_count,
    render_user_score_list,
    render_user_recent_score,
    get_user_scores_page_count,
    render_user_today_bp,
    get_today_bp_page_count,
    render_user_beatmap_score_card,
    render_user_recent_score_card,
    render_user_score_list_image,
    render_user_today_bp_image,
)
from utils.logger import get_logger


class ScoresPaginationView(discord.ui.View):
    def __init__(self, user_id: int, beatmap_id: int, author_id: int, total_pages: int):
        super().__init__(timeout=60)
        self.user_id = user_id
        self.beatmap_id = beatmap_id
        self.author_id = author_id
        self.total_pages = total_pages
        self.page = 1
        self.update_buttons()

    def update_buttons(self):
        self.previous_button.disabled = self.page <= 1
        self.next_button.disabled = self.page >= self.total_pages

    @discord.ui.button(label="Previous", style=discord.ButtonStyle.primary)
    async def previous_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        self.page -= 1
        await self.update_view(interaction)

    @discord.ui.button(label="Next", style=discord.ButtonStyle.primary)
    async def next_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        self.page += 1
        await self.update_view(interaction)

    async def update_view(self, interaction: discord.Interaction):
        content = await render_user_beatmap_scores(  # type: ignore[call-arg]
            self.user_id, self.beatmap_id, self.page, locale="en"
        )
        self.update_buttons()
        await interaction.response.edit_message(content=content, view=self)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.author_id:
            await interaction.response.send_message(
                "This interaction is not for you.", ephemeral=True
            )
            return False
        return True


class UserScoresPaginationView(discord.ui.View):
    def __init__(
        self,
        user_id: int,
        type: str,
        include_fails: bool,
        author_id: int,
        total_pages: int,
    ):
        super().__init__(timeout=60)
        self.user_id = user_id
        self.type = type
        self.include_fails = include_fails
        self.author_id = author_id
        self.total_pages = total_pages
        self.page = 1
        self.update_buttons()

    def update_buttons(self):
        self.previous_button.disabled = self.page <= 1
        self.next_button.disabled = self.page >= self.total_pages

    @discord.ui.button(label="Previous", style=discord.ButtonStyle.primary)
    async def previous_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        self.page -= 1
        await self.update_view(interaction)

    @discord.ui.button(label="Next", style=discord.ButtonStyle.primary)
    async def next_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        self.page += 1
        await self.update_view(interaction)

    async def update_view(self, interaction: discord.Interaction):
        content = await render_user_score_list(  # type: ignore
            self.user_id, self.type, include_fails=self.include_fails, page=self.page, locale="en"
        )
        self.update_buttons()
        await interaction.response.edit_message(content=content, view=self)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.author_id:
            await interaction.response.send_message(
                "This interaction is not for you.", ephemeral=True
            )
            return False
        return True


class TodayBPPaginationView(discord.ui.View):
    def __init__(self, user_id: int, author_id: int, total_pages: int):
        super().__init__(timeout=60)
        self.user_id = user_id
        self.author_id = author_id
        self.total_pages = total_pages
        self.page = 1
        self.update_buttons()

    def update_buttons(self):
        self.previous_button.disabled = self.page <= 1
        self.next_button.disabled = self.page >= self.total_pages

    @discord.ui.button(label="Previous", style=discord.ButtonStyle.primary)
    async def previous_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        self.page -= 1
        await self.update_view(interaction)

    @discord.ui.button(label="Next", style=discord.ButtonStyle.primary)
    async def next_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        self.page += 1
        await self.update_view(interaction)

    async def update_view(self, interaction: discord.Interaction):
        content = await render_user_today_bp(self.user_id, page=self.page, locale="en")  # type: ignore[call-arg]
        self.update_buttons()
        await interaction.response.edit_message(content=content, view=self)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.author_id:
            await interaction.response.send_message(
                "This interaction is not for you.", ephemeral=True
            )
            return False
        return True


class Scores(Cog):
    def __init__(self, bot):
        self.bot = bot
        get_logger("cogs.scores").info("Cog scores Loaded")

    @commands.hybrid_command(
        name="ss", description="Query your all scores on a beatmap"
    )
    @app_commands.describe(beatmap_id="beatmap id")
    async def ss(self, ctx: commands.Context, beatmap_id: int):
        await ctx.defer()
        username = await resolve_username(ctx, None)
        user_info = await get_user_info(username)
        user_id = user_info["id"]

        total_pages = await get_scores_page_count(user_id, beatmap_id)
        content = await render_user_beatmap_scores(user_id, beatmap_id, 1, locale="en")  # type: ignore[call-arg]

        if total_pages > 1:
            view = ScoresPaginationView(user_id, beatmap_id, ctx.author.id, total_pages)
            await ctx.send(content=content, view=view)
        else:
            await ctx.send(content=content)

    @commands.hybrid_command(
        name="ps", description="Query your recent passed scores (24h)"
    )
    @app_commands.describe(user="osu! username or mention")
    async def ps(self, ctx: commands.Context, user: str | None = None):
        await ctx.defer()
        username = await resolve_username(ctx, user)
        user_info = await get_user_info(username)
        user_id = user_info["id"]

        # type=recent, include_fails=False (Passed only)
        # Note: API "recent" implies last 24h
        content = await render_user_score_list(  # type: ignore
            user_id, "recent", include_fails=False, page=1, locale="en"
        )
        total_pages = await get_user_scores_page_count(
            user_id, "recent", include_fails=False
        )

        if total_pages > 1:
            view = UserScoresPaginationView(
                user_id, "recent", False, ctx.author.id, total_pages
            )
            await ctx.send(content=content, view=view)
        else:
            await ctx.send(content=content)

    @commands.hybrid_command(
        name="rs", description="Query your recent scores (24h, including fails)"
    )
    @app_commands.describe(user="osu! username or mention")
    async def rs(self, ctx: commands.Context, user: str | None = None):
        await ctx.defer()
        username = await resolve_username(ctx, user)
        user_info = await get_user_info(username)
        user_id = user_info["id"]

        # type=recent, include_fails=True
        content = await render_user_score_list(  # type: ignore
            user_id, "recent", include_fails=True, page=1, locale="en"
        )
        total_pages = await get_user_scores_page_count(
            user_id, "recent", include_fails=True
        )

        if total_pages > 1:
            view = UserScoresPaginationView(
                user_id, "recent", True, ctx.author.id, total_pages
            )
            await ctx.send(content=content, view=view)
        else:
            await ctx.send(content=content)

    @commands.hybrid_command(
        name="t",
        description="Query your best scores achieved in the last 24 hours (Today's BP)",
    )
    @app_commands.describe(user="osu! username or mention")
    async def t(self, ctx: commands.Context, user: str | None = None):
        await ctx.defer()
        username = await resolve_username(ctx, user)
        user_info = await get_user_info(username)
        user_id = user_info["id"]

        # 获取今日（24小时内）刷新的BP
        content = await render_user_today_bp(user_id, page=1, locale="en")  # type: ignore[call-arg]
        total_pages = await get_today_bp_page_count(user_id)

        if total_pages > 1:
            view = TodayBPPaginationView(user_id, ctx.author.id, total_pages)
            await ctx.send(content=content, view=view)
        else:
            await ctx.send(content=content)

    @commands.hybrid_command(name="p", description="Query your latest passed score")
    @app_commands.describe(user="osu! username or mention")
    async def p(self, ctx: commands.Context, user: str | None = None):
        await ctx.defer()
        username = await resolve_username(ctx, user)
        user_info = await get_user_info(username)
        user_id = user_info["id"]

        # type=recent, include_fails=False, limit=1
        content = await render_user_recent_score(user_id, "recent", include_fails=False, locale="en")  # type: ignore[call-arg]
        await ctx.send(content=content)

    @commands.hybrid_command(
        name="r", description="Query your latest score (including fails)"
    )
    @app_commands.describe(user="osu! username or mention")
    async def r(self, ctx: commands.Context, user: str | None = None):
        await ctx.defer()
        username = await resolve_username(ctx, user)
        user_info = await get_user_info(username)
        user_id = user_info["id"]

        # type=recent, include_fails=True, limit=1
        content = await render_user_recent_score(user_id, "recent", include_fails=True, locale="en")  # type: ignore[call-arg]
        await ctx.send(content=content)

    # ============ 图片版本命令 ============

    @commands.hybrid_command(
        name="uss", description="Query your all scores on a beatmap (image card)"
    )
    @app_commands.describe(beatmap_id="beatmap id")
    async def uss(self, ctx: commands.Context, beatmap_id: int):
        """查询谱面成绩（图片卡片版）"""
        await ctx.defer()
        username = await resolve_username(ctx, None)
        user_info = await get_user_info(username)
        user_id = user_info["id"]

        image = await render_user_beatmap_score_card(user_id, beatmap_id)
        await ctx.send(file=File(io.BytesIO(image), f"score_{beatmap_id}.png"))

    @commands.hybrid_command(
        name="ups", description="Query your recent passed scores (image card)"
    )
    @app_commands.describe(user="osu! username or mention")
    async def ups(self, ctx: commands.Context, user: str | None = None):
        """查询最近通过成绩（图片卡片版）"""
        await ctx.defer()
        username = await resolve_username(ctx, user)
        user_info = await get_user_info(username)
        user_id = user_info["id"]
        gamemode = await get_user_gamemode(ctx.author.id)

        image = await render_user_score_list_image(
            user_id, username, score_type="recent", include_fails=False, mode=gamemode
        )
        await ctx.send(file=File(io.BytesIO(image), f"{username}_recent.png"))

    @commands.hybrid_command(
        name="urs", description="Query your recent scores including fails (image card)"
    )
    @app_commands.describe(user="osu! username or mention")
    async def urs(self, ctx: commands.Context, user: str | None = None):
        """查询最近成绩包含失败（图片卡片版）"""
        await ctx.defer()
        username = await resolve_username(ctx, user)
        user_info = await get_user_info(username)
        user_id = user_info["id"]
        gamemode = await get_user_gamemode(ctx.author.id)

        image = await render_user_score_list_image(
            user_id, username, score_type="recent", include_fails=True, mode=gamemode
        )
        await ctx.send(file=File(io.BytesIO(image), f"{username}_recent_all.png"))

    @commands.hybrid_command(
        name="ut", description="Query your today's BP (image card)"
    )
    @app_commands.describe(user="osu! username or mention")
    async def ut(self, ctx: commands.Context, user: str | None = None):
        """查询今日BP（图片卡片版）"""
        await ctx.defer()
        username = await resolve_username(ctx, user)
        user_info = await get_user_info(username)
        user_id = user_info["id"]
        gamemode = await get_user_gamemode(ctx.author.id)

        image = await render_user_today_bp_image(user_id, username, mode=gamemode)
        await ctx.send(file=File(io.BytesIO(image), f"{username}_today_bp.png"))

    @commands.hybrid_command(
        name="up", description="Query your latest passed score (image card)"
    )
    @app_commands.describe(user="osu! username or mention")
    async def up(self, ctx: commands.Context, user: str | None = None):
        """查询最新通过成绩（图片卡片版）"""
        await ctx.defer()
        username = await resolve_username(ctx, user)
        user_info = await get_user_info(username)
        user_id = user_info["id"]
        gamemode = await get_user_gamemode(ctx.author.id)

        image = await render_user_recent_score_card(user_id, include_fails=False, mode=gamemode)
        await ctx.send(file=File(io.BytesIO(image), f"{username}_latest.png"))

    @commands.hybrid_command(
        name="ur", description="Query your latest score including fails (image card)"
    )
    @app_commands.describe(user="osu! username or mention")
    async def ur(self, ctx: commands.Context, user: str | None = None):
        """查询最新成绩包含失败（图片卡片版）"""
        await ctx.defer()
        username = await resolve_username(ctx, user)
        user_info = await get_user_info(username)
        user_id = user_info["id"]
        gamemode = await get_user_gamemode(ctx.author.id)

        image = await render_user_recent_score_card(user_id, include_fails=True, mode=gamemode)
        await ctx.send(file=File(io.BytesIO(image), f"{username}_latest_all.png"))

    # ============ Best 成绩命令 ============

    @commands.hybrid_command(
        name="b", description="Query your best score (single)"
    )
    @app_commands.describe(user="osu! username or mention")
    async def b(self, ctx: commands.Context, user: str | None = None):
        """查询最佳成绩（文字版，单条）"""
        await ctx.defer()
        username = await resolve_username(ctx, user)
        user_info = await get_user_info(username)
        user_id = user_info["id"]
        gamemode = await get_user_gamemode(ctx.author.id)

        content = await render_user_score_list(  # type: ignore
            user_id, "best", include_fails=False, page=1, limit=1, locale="en", mode=gamemode
        )
        await ctx.send(content=content)

    @commands.hybrid_command(
        name="bs", description="Query your best scores list"
    )
    @app_commands.describe(user="osu! username or mention", count="Number of scores (1-100, default 20)")
    async def bs(self, ctx: commands.Context, user: str | None = None, count: int = 20):
        """查询最佳成绩列表（文字版，多条）"""
        await ctx.defer()
        count = min(max(count, 1), 100)  # 限制 1-100
        username = await resolve_username(ctx, user)
        user_info = await get_user_info(username)
        user_id = user_info["id"]
        gamemode = await get_user_gamemode(ctx.author.id)

        content = await render_user_score_list(  # type: ignore
            user_id, "best", include_fails=False, page=1, limit=count, locale="en", mode=gamemode
        )
        await ctx.send(content=content)

    @commands.hybrid_command(
        name="ub", description="Query your best score (image card, single)"
    )
    @app_commands.describe(user="osu! username or mention")
    async def ub(self, ctx: commands.Context, user: str | None = None):
        """查询最佳成绩（图片卡片版，单条）"""
        await ctx.defer()
        username = await resolve_username(ctx, user)
        user_info = await get_user_info(username)
        user_id = user_info["id"]
        gamemode = await get_user_gamemode(ctx.author.id)

        image = await render_user_score_list_image(
            user_id, username, score_type="best", include_fails=False, count=1, mode=gamemode
        )
        await ctx.send(file=File(io.BytesIO(image), f"{username}_best.png"))

    @commands.hybrid_command(
        name="ubs", description="Query your best scores (image card, multiple)"
    )
    @app_commands.describe(user="osu! username or mention", count="Number of scores (1-100, default 20)")
    async def ubs(self, ctx: commands.Context, user: str | None = None, count: int = 20):
        """查询最佳成绩列表（图片卡片版，多条）"""
        await ctx.defer()
        count = min(max(count, 1), 100)  # 限制 1-100
        username = await resolve_username(ctx, user)
        user_info = await get_user_info(username)
        user_id = user_info["id"]
        gamemode = await get_user_gamemode(ctx.author.id)

        image = await render_user_score_list_image(
            user_id, username, score_type="best", include_fails=False, count=count, mode=gamemode
        )
        await ctx.send(file=File(io.BytesIO(image), f"{username}_best_list.png"))


async def setup(bot: commands.Bot):
    await bot.add_cog(Scores(bot))
