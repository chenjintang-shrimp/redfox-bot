from discord import app_commands
from discord.ext import commands
from renderer.beatmap import render_beatmap_info
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


async def setup(bot):
    await bot.add_cog(BeatmapCog(bot))
