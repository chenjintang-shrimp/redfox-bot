"""平台适配器抽象基类"""

import traceback
from abc import ABC, abstractmethod
from typing import Any, Optional

from models.context import UserContext
from adapters.message_types import Message, TextMessage
from utils.strings import format_template
from utils.logger import get_logger


class PlatformAdapter(ABC):
    """平台适配器抽象基类

    所有平台适配器（Discord、QQ等）都应该继承此类
    提供统一的用户上下文获取和消息发送接口
    """

    def __init__(self):
        self.logger = get_logger(f"adapter.{self.platform_name}")

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

    async def handle_error(
        self, platform_ctx: Any, error: Exception, locale: str = "zh"
    ) -> None:
        """统一错误处理和本地化

        根据异常类型选择对应的本地化模板并发送错误消息，同时记录详细日志

        Args:
            platform_ctx: 平台特定的上下文对象
            error: 捕获的异常
            locale: 语言代码 (en/zh)
        """
        # 记录详细的错误日志
        self.logger.error(f"发生错误: {type(error).__name__}: {error}")
        self.logger.error(traceback.format_exc())

        # 检查是否是 httpx 相关的异常
        error_module = getattr(type(error), "__module__", "")
        is_httpx_error = "httpx" in error_module
        
        # 检查是否是网络连接错误（通过错误字符串关键词，作为兜底）
        error_str = str(error).lower()
        is_connection_error_keywords = any(
            keyword in error_str 
            for keyword in [
                "connecterror", "connection error", "timeout", "timed out",
                "network error", "unreachable", "refused", "no route"
            ]
        )

        # 获取异常的模板key和上下文
        template_key = getattr(error, "template_key", None)
        context_vars = getattr(error, "__dict__", {})

        if template_key:
            message = format_template(template_key, locale=locale, **context_vars)
        elif is_httpx_error or is_connection_error_keywords:
            # httpx 异常或网络连接关键词错误，使用 CONNECTION_FAILED 模板
            message = format_template("CONNECTION_FAILED", locale=locale)
        else:
            # 未知异常使用通用错误模板
            message = format_template("QUERY_FAILED", locale=locale)

        await self.send(platform_ctx, TextMessage(content=message))
