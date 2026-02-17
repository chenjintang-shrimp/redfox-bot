"""平台适配器抽象基类"""

from abc import ABC, abstractmethod
from typing import Any, Optional

from models.context import UserContext
from adapters.message_types import Message


class PlatformAdapter(ABC):
    """平台适配器抽象基类

    所有平台适配器（Discord、QQ等）都应该继承此类
    提供统一的用户上下文获取和消息发送接口
    """

    @property
    @abstractmethod
    def platform_name(self) -> str:
        """返回平台标识符，如 'discord', 'qq'"""
        pass

    @abstractmethod
    async def get_user_context(self, platform_ctx: Any) -> UserContext:
        """从平台特定的上下文获取统一的用户上下文

        Args:
            platform_ctx: 平台特定的上下文对象
                - Discord: commands.Context
                - QQ: MessageEvent

        Returns:
            UserContext: 统一的用户上下文
        """
        pass

    @abstractmethod
    async def send(self, platform_ctx: Any, message: Message) -> Any:
        """发送消息到平台

        Args:
            platform_ctx: 平台特定的上下文对象
            message: 统一的消息对象（TextMessage/ImageMessage/EmbedMessage）

        Returns:
            平台特定的消息对象（可选）
        """
        pass

    @abstractmethod
    async def resolve_username(
        self, platform_ctx: Any, username_arg: Optional[str]
    ) -> str:
        """解析用户名

        如果 username_arg 为 None，则返回已绑定用户的用户名
        如果 username_arg 不为 None，则直接返回

        Args:
            platform_ctx: 平台特定的上下文对象
            username_arg: 用户提供的用户名参数

        Returns:
            解析后的用户名

        Raises:
            UserNotBindError: 用户未绑定且未提供用户名
        """
        pass
