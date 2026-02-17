import io

from discord import File, app_commands
from discord.ext import commands

from adapters.discord_adapter import DiscordAdapter
from services import BeatmapService
from renderer.beatmap import render_beatmap_info, render_beatmap_card_image
from utils.logger import get_logger


class BeatmapCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.adapter = DiscordAdapter()

    @commands.hybrid_command("m", description="Query Beatmap Info")
    @app_commands.describe(beatmap_id="Beatmap ID")
    async def beatmap(self, ctx: commands.Context, beatmap_id: int):
        """
        Query beatmap info by ID
        Usage: !m <beatmap_id>
        """
        get_logger("Discord").info(
            f"User {ctx.author}({ctx.author.id}) queried beatmap {beatmap_id}"
        )

        try:
            msg = await render_beatmap_info(beatmap_id, locale="en")
            await ctx.send(msg)
        except Exception as e:
            await self.adapter.handle_error(ctx, e, locale="en")

    @commands.hybrid_command("um", description="Query Beatmap Info with image card")
    @app_commands.describe(beatmap_id="Beatmap ID")
    async def ubeatmap(self, ctx: commands.Context, beatmap_id: int):
        """
        Query beatmap info by ID (image card version)
        Usage: !um <beatmap_id>
        """
        await ctx.defer()
        get_logger("Discord").info(
            f"User {ctx.author}({ctx.author.id}) queried beatmap {beatmap_id} (image)"
        )

        try:
            beatmap_info = await BeatmapService.get_beatmap(beatmap_id)
            image = await render_beatmap_card_image(beatmap_info.__dict__)
            await ctx.send(file=File(io.BytesIO(image), f"beatmap_{beatmap_id}.png"))
        except Exception as e:
            await self.adapter.handle_error(ctx, e, locale="en")


async def setup(bot: commands.Bot):
    await bot.add_cog(BeatmapCog(bot))
