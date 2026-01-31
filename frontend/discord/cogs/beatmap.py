import io

from discord import File, app_commands
from discord.ext import commands
from backend.beatmap import get_beatmap_info
from renderer.beatmap import render_beatmap_info, render_beatmap_card_image
from utils.logger import get_logger


class BeatmapCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command("m", description="Query Beatmap Info")
    @app_commands.describe(beatmap_id="Beatmap ID")
    async def beatmap(self, ctx, beatmap_id: int):
        """
        Query beatmap info by ID
        Usage: !m <beatmap_id>
        """
        get_logger("Discord").info(
            f"User {ctx.author}({ctx.author.id}) queried beatmap {beatmap_id}"
        )
        msg = await render_beatmap_info(beatmap_id)
        await ctx.send(msg)

    @commands.hybrid_command("um", description="Query Beatmap Info with image card")
    @app_commands.describe(beatmap_id="Beatmap ID")
    async def ubeatmap(self, ctx, beatmap_id: int):
        """
        Query beatmap info by ID (image card version)
        Usage: !um <beatmap_id>
        """
        await ctx.defer()
        get_logger("Discord").info(
            f"User {ctx.author}({ctx.author.id}) queried beatmap {beatmap_id} (image)"
        )

        beatmap_info = await get_beatmap_info(beatmap_id)
        image = await render_beatmap_card_image(beatmap_info)
        await ctx.send(file=File(io.BytesIO(image), f"beatmap_{beatmap_id}.png"))


async def setup(bot):
    await bot.add_cog(BeatmapCog(bot))
