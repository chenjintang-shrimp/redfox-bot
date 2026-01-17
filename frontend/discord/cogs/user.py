from utils.logger import get_logger
from discord.ext import commands
from discord import app_commands, Interaction

from backend.user import bind_user, get_user_info


class User(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        get_logger("cogs.user").info("Cog User Loaded")

    @commands.command(name="info")
    async def info_prefix(self, ctx: commands.Context, user: str):
        msg = await get_user_info(user)
        await ctx.send(msg)

    @app_commands.command(name="info", description="查询用户信息")
    async def info_slash(self, interaction: Interaction, user: str):
        msg = await get_user_info(user)
        await interaction.response.send_message(msg)

    @commands.command(name="bind")
    async def bind_prefix(self, ctx: commands.Context, user: str):
        msg = await bind_user(ctx.author.id, user)
        await ctx.send(msg)

    @app_commands.command(name="bind",description="Bind user to the bot")
    async def bind_slash(self, interaction: Interaction, user: str):
        msg = await bind_user(interaction.user.id, user)
        await interaction.response.send_message(msg)

async def setup(bot: commands.Bot):
    await bot.add_cog(User(bot))
