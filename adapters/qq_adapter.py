"""QQ 平台适配器实现"""

from typing import Any, Optional

from nonebot.adapters.onebot.v11 import MessageEvent, MessageSegment

from adapters.base import PlatformAdapter
from adapters.message_types import TextMessage, ImageMessage, EmbedMessage, Message
from models.context import UserContext
from backend.database import get_user_binding
from backend.exceptions.user import UserNotBindError


class QQAdapter(PlatformAdapter):
    """QQ 平台适配器

    将 NoneBot2/OneBot V11 API 转换为统一接口
    """

    @property
    def platform_name(self) -> str:
        return "qq"

    async def get_user_context(self, platform_ctx: MessageEvent) -> UserContext:
        """从 QQ MessageEvent 获取统一的用户上下文

        Args:
            platform_ctx: nonebot.adapters.onebot.v11.MessageEvent

        Returns:
            UserContext: 包含用户绑定信息的上下文
        """
        event = platform_ctx
        qq_id = event.user_id
        binding = await get_user_binding(self.platform_name, qq_id)

        return UserContext(
            platform=self.platform_name,
            platform_user_id=str(qq_id),
            osu_username=binding.osu_username if binding else None,
            osu_user_id=binding.osu_id if binding else None,
            current_gamemode=binding.current_gamemode if binding else None,
        )

    async def send(self, platform_ctx: MessageEvent, message: Message) -> Any:
        """发送消息到 QQ

        Args:
            platform_ctx: MessageEvent
            message: 统一消息对象

        Returns:
            发送结果
        """
        from nonebot import get_bot

        event = platform_ctx
        bot = get_bot()

        if isinstance(message, TextMessage):
            return await bot.send(event, MessageSegment.text(message.content))

        elif isinstance(message, ImageMessage):
            # QQ 使用 base64 或文件路径发送图片
            # 这里使用 base64 方式
            import base64

            image_b64 = base64.b64encode(message.image_bytes).decode()
            msg = MessageSegment.image(f"base64://{image_b64}")

            if message.caption:
                # QQ 不支持图片+文字混合，先发送文字再发送图片
                await bot.send(event, MessageSegment.text(message.caption))

            return await bot.send(event, msg)

        elif isinstance(message, EmbedMessage):
            # QQ 不支持 Embed，转换为文本格式
            lines = []
            if message.title:
                lines.append(f"**{message.title}**")
            if message.description:
                lines.append(message.description)
            if message.fields:
                for field in message.fields:
                    lines.append(f"\n{field.get('name', '')}:")
                    lines.append(field.get('value', ''))
            if message.footer:
                lines.append(f"\n{message.footer}")

            text = "\n".join(lines)
            return await bot.send(event, MessageSegment.text(text))

        else:
            raise ValueError(f"Unknown message type: {type(message)}")

    async def resolve_username(
        self, platform_ctx: MessageEvent, username_arg: Optional[str]
    ) -> str:
        """解析用户名

        如果 username_arg 为 None 或空字符串，返回已绑定用户的用户名
        如果 username_arg 不为空，直接返回

        Args:
            platform_ctx: MessageEvent
            username_arg: 用户提供的用户名参数

        Returns:
            解析后的 osu! 用户名

        Raises:
            UserNotBindError: 用户未绑定且未提供用户名
        """
        event = platform_ctx

        if username_arg and username_arg.strip():
            return username_arg.strip()

        qq_id = event.user_id
        binding = await get_user_binding(self.platform_name, qq_id)

        if binding is None:
            raise UserNotBindError(str(qq_id))

        return binding.osu_username

    async def send_image_bytes(
        self,
        platform_ctx: MessageEvent,
        image_bytes: bytes,
        caption: Optional[str] = None
    ) -> Any:
        """便捷方法：发送图片字节

        Args:
            platform_ctx: MessageEvent
            image_bytes: 图片字节数据
            caption: 说明文字（QQ 会单独发送）

        Returns:
            发送结果
        """
        message = ImageMessage(
            image_bytes=image_bytes,
            filename="image.png",
            caption=caption
        )
        return await self.send(platform_ctx, message)
