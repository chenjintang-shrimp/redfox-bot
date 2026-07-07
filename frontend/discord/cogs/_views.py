"""Pagination view classes for score-related Discord interactions."""

import discord

from renderer.scores import (
    render_user_beatmap_scores,
    render_user_score_list,
    render_user_today_bp,
)


class BasePaginationView(discord.ui.View):
    """分页视图基类"""

    def __init__(self, author_id: int, total_pages: int, timeout: float = 60):
        super().__init__(timeout=timeout)
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
        """子类需要重写此方法"""
        raise NotImplementedError("Subclasses must implement update_view()")

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.author_id:
            await interaction.response.send_message(
                "This interaction is not for you.", ephemeral=True
            )
            return False
        return True


class ScoresPaginationView(BasePaginationView):
    def __init__(self, user_id: int, beatmap_id: int, author_id: int, total_pages: int):
        super().__init__(author_id, total_pages)
        self.user_id = user_id
        self.beatmap_id = beatmap_id

    async def update_view(self, interaction: discord.Interaction):
        content = await render_user_beatmap_scores(
            self.user_id, self.beatmap_id, self.page, locale="en"
        )
        self.update_buttons()
        await interaction.response.edit_message(content=content, view=self)


class UserScoresPaginationView(BasePaginationView):
    def __init__(
        self,
        user_id: int,
        type: str,
        include_fails: bool,
        author_id: int,
        total_pages: int,
    ):
        super().__init__(author_id, total_pages)
        self.user_id = user_id
        self.type = type
        self.include_fails = include_fails

    async def update_view(self, interaction: discord.Interaction):
        content = await render_user_score_list(
            self.user_id,
            self.type,
            include_fails=self.include_fails,
            page=self.page,
            locale="en",
        )
        self.update_buttons()
        await interaction.response.edit_message(content=content, view=self)


class TodayBPPaginationView(BasePaginationView):
    def __init__(self, user_id: int, author_id: int, total_pages: int):
        super().__init__(author_id, total_pages)
        self.user_id = user_id

    async def update_view(self, interaction: discord.Interaction):
        content = await render_user_today_bp(self.user_id, page=self.page, locale="en")
        self.update_buttons()
        await interaction.response.edit_message(content=content, view=self)
