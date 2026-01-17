from discord.ext import commands
import discord
import urllib.parse
from utils.variable import API_URL, OAUTH_APP_ID, OAUTH_REDIRECT_URI
from datetime import datetime, timedelta
import backend.oauth
from backend.database import User, save_user


class Auth(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="bind")
    async def bind(self, ctx: commands.Context):
        """
        Sends an OAuth binding link to the user via DM.
        """
        user_id = str(ctx.author.id)

        # Construct the OAuth Authorization URL
        params = {
            "client_id": OAUTH_APP_ID,
            "redirect_uri": OAUTH_REDIRECT_URI,
            "response_type": "code",
            "scope": "public",  # Adjust scopes as needed
            "state": user_id,
        }
        query_string = urllib.parse.urlencode(params)
        auth_url = f"{API_URL}/oauth/authorize?{query_string}"

        try:
            embed = discord.Embed(
                title="Link your account",
                description=f"Click the link below to bind your osu! account:\n\n[Login with osu!]({auth_url})\n\nThis link is unique to you and safe to share.",
                color=discord.Color.blue(),
            )
            await ctx.author.send(embed=embed)
            await ctx.reply(
                "I've sent you a DM with the binding link!", ephemeral=True
            )  # Ephemeral in reply context serves as a good UX if supported or just standard reply
        except discord.Forbidden:
            await ctx.reply(
                "I couldn't send you a DM. Please check your privacy settings."
            )

    @commands.command(name="verify")
    async def verify(self, ctx: commands.Context, code: str):
        """
        Verifies the OAuth code and binds the account.
        Usage: !verify <code>
        """
        try:
            # Exchange code for token
            token_data = await backend.oauth.exchange_code_for_token(code)
            access_token = token_data["access_token"]
            refresh_token = token_data["refresh_token"]
            expires_in = token_data["expires_in"]

            # Get user info
            user_info = await backend.oauth.get_user_info(access_token)
            osu_id = user_info["id"]
            osu_username = user_info["username"]

            # Calculate expiry
            expires_at = datetime.now() + timedelta(seconds=expires_in)

            # Create user object
            user = User(
                discord_id=str(ctx.author.id),
                osu_id=osu_id,
                osu_username=osu_username,
                access_token=access_token,
                refresh_token=refresh_token,
                expires_at=expires_at,
            )

            # Save to database
            save_user(user)

            await ctx.reply(
                f"Successfully bound to osu! user **{osu_username}** (ID: {osu_id})!"
            )

        except Exception as e:
            await ctx.reply(f"Failed to bind account: {str(e)}")


async def setup(bot):
    await bot.add_cog(Auth(bot))
