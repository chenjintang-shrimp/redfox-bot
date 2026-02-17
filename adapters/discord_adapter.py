"""Discord 平台适配器实现"""

import io
import re
from typing import Any, Optional

import discord
from discord import Member, User, File, Embed
from discord.ext.commands import Context

from adapters.base import PlatformAdapter
from adapters.message_types import TextMessage, ImageMessage, EmbedMessage, Message
from models.context import UserContext
from backend.database import get_user_binding
from backend.exceptions.user import UserNotBindError


class DiscordAdapter(PlatformAdapter):
    """Discord 平台适配器

    将 Discord 特定的 API 转换为统一接口
    """

    @property
    def platform_name(self) -> str:
        return "discord"

    async def get_user_context(self, ctx: Context) -> UserContext:
        """从 Discord Context 获取统一的用户上下文

        Args:
            ctx: discord.ext.commands.Context

        Returns:
            UserContext: 包含用户绑定信息的上下文
        """
        discord_id = ctx.author.id
        binding = await get_user_binding(self.platform_name, discord_id)

        return UserContext(
            platform=self.platform_name,
            platform_user_id=str(discord_id),
            osu_username=binding.osu_username if binding else None,
            osu_user_id=binding.osu_id if binding else None,
            current_gamemode=binding.current_gamemode if binding else None,
        )

    async def send(self, ctx: Context, message: Message) -> Any:
        """发送消息到 Discord

        Args:
            ctx: discord.ext.commands.Context
            message: 统一消息对象

        Returns:
            discord.Message: 发送的消息对象
        """
        if isinstance(message, TextMessage):
            return await ctx.send(message.content)

        elif isinstance(message, ImageMessage):
            file = File(
                io.BytesIO(message.image_bytes),
                filename=message.filename or "image.png"
            )
            if message.caption:
                return await ctx.send(content=message.caption, file=file)
            return await ctx.send(file=file)

        elif isinstance(message, EmbedMessage):
            embed = Embed(
                title=message.title,
                description=message.description,
                color=message.color
            )
            if message.fields:
                for field in message.fields:
                    embed.add_field(
                        name=field.get("name", ""),
                        value=field.get("value", ""),
                        inline=field.get("inline", False)
                    )
            if message.image_url:
                embed.set_image(url=message.image_url)
            if message.thumbnail_url:
                embed.set_thumbnail(url=message.thumbnail_url)
            if message.footer:
                embed.set_footer(text=message.footer)
            return await ctx.send(embed=embed)

        else:
            raise ValueError(f"Unknown message type: {type(message)}")

    async def resolve_username(
        self, ctx: Context, username_arg: Optional[str | User | Member]
    ) -> str:
        """解析用户名

        如果 username_arg 为 None，返回已绑定用户的用户名
        如果 username_arg 是 User/Member，返回该用户的绑定用户名
        如果 username_arg 是字符串且不是 mention，直接返回
        如果 username_arg 是 mention，解析并返回该用户的绑定用户名

        Args:
            ctx: Discord Context
            username_arg: 用户名参数（可以是字符串、User 或 Member）

        Returns:
            解析后的 osu! 用户名

        Raises:
            UserNotBindError: 用户未绑定且未提供有效用户名
        """
        target_discord_id: int | None = None

        if username_arg is None:
            target_discord_id = ctx.author.id
        elif isinstance(username_arg, (User, Member)):
            target_discord_id = username_arg.id
        elif isinstance(username_arg, str):
            # 检查是否是 mention
            match = re.match(r"<@!?(\d+)>", username_arg)
            if match:
                target_discord_id = int(match.group(1))
            else:
                # 直接返回用户名
                return username_arg

        if target_discord_id is not None:
            binding = await get_user_binding(self.platform_name, target_discord_id)
            if binding is None:
                user_mention = f"<@{target_discord_id}>"
                raise UserNotBindError(user_mention)
            return binding.osu_username

        raise UserNotBindError("Unknown user")

    async def send_image_bytes(
        self,
        ctx: Context,
        image_bytes: bytes,
        filename: str = "image.png",
        caption: Optional[str] = None
    ) -> discord.Message:
        """便捷方法：发送图片字节

        Args:
            ctx: Discord Context
            image_bytes: 图片字节数据
            filename: 文件名
            caption: 说明文字

        Returns:
            discord.Message: 发送的消息
        """
        message = ImageMessage(
            image_bytes=image_bytes,
            filename=filename,
            caption=caption
        )
        return await self.send(ctx, message)
