from discord import Member, User
from discord.ext.commands import Context
from backend.expections.user import UserNotBindError
import re

from backend.database import get_osu_user_by_discord_id

async def resolve_username(ctx: Context, user_arg: str | User | Member | None) -> str:
    target_discord_id: int = 0
    if user_arg is None:
        target_discord_id = ctx.author.id
    elif isinstance(user_arg, (User, Member)):
        target_discord_id = user_arg.id
    elif isinstance(user_arg, str):
        match = re.match(r"<@!?(\d+)>", user_arg)
        if match:
            target_discord_id = int(match.group(1))
        else:
            return user_arg

    osu_user = await get_osu_user_by_discord_id(target_discord_id)
    if osu_user is None:
        user_mention_str = f"<@{target_discord_id}>"
        raise UserNotBindError(
            user_mention_str,
        )
    return osu_user.osu_username
