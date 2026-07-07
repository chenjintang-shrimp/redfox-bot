"""平台适配器抽象基类"""

import traceback
from abc import ABC, abstractmethod
from typing import Any, Optional

from models.context import UserContext
from adapters.message_types import Message, TextMessage
from utils.strings import format_template
from utils.logger import get_logger


def _classify_error(error: Exception) -> str:
    """将异常分类为模板 key 字符串

    优先使用异常的 template_key 属性；其次检测 httpx/网络错误返回 CONNECTION_FAILED；
    兜底返回 QUERY_FAILED。

    Args:
        error: 捕获的异常

    Returns:
        对应的 i18n 模板 key
    """
    template_key = getattr(error, "template_key", None)
    if template_key:
        return template_key

    error_module = getattr(type(error), "__module__", "")
    is_httpx_error = "httpx" in error_module

    error_str = str(error).lower()
    is_connection_error_keywords = any(
        keyword in error_str
        for keyword in [
            "connecterror", "connection error", "timeout", "timed out",
            "network error", "unreachable", "refused", "no route",
        ]
    )

    if is_httpx_error or is_connection_error_keywords:
        return "CONNECTION_FAILED"
    return "QUERY_FAILED"


def _format_error_message(template_key: str, error: Exception, locale: str) -> str:
    """根据模板 key 和异常上下文格式化本地化错误消息

    Args:
        template_key: i18n 模板 key
        error: 捕获的异常
        locale: 语言代码 (en/zh)

    Returns:
        本地化后的错误消息字符串
    """
    context_vars = getattr(error, "__dict__", {})
    return format_template(template_key, context=context_vars, locale=locale)


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

        template_key = _classify_error(error)
        message = _format_error_message(template_key, error, locale)

        await self.send(platform_ctx, TextMessage(content=message))
