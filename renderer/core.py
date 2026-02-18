"""
渲染层核心抽象模块

提供渲染引擎的基础抽象，包括：
- RenderResult: 统一的渲染结果载体
- RenderEngine: 渲染引擎协议
- RenderAdapter: 渲染适配器基类
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Protocol, runtime_checkable


@dataclass(slots=True, frozen=True)
class RenderResult:
    """
    统一的渲染结果载体

    封装了所有可发送的消息类型，前端只需根据 content_type 决定如何发送

    Attributes:
        content_type: 内容类型，"image" | "text" | "interactive"
        data: 实际内容，bytes（图片）或 str（文本）
        metadata: 额外元数据，如图片尺寸、文件名等
    """

    content_type: str
    data: bytes | str
    metadata: dict[str, Any] = field(default_factory=dict)


@runtime_checkable
class RenderEngine(Protocol):
    """
    渲染引擎协议

    所有渲染引擎都必须实现此协议，包括：
    - HtmlImageAdapter: HTML 转图片
    - TextAdapter: 纯文本渲染
    - 未来可能的 SkiaAdapter、PydollAdapter 等
    """

    async def render(
        self,
        view_name: str,
        data: dict[str, Any],
        **kwargs: Any,
    ) -> RenderResult:
        """
        将数据渲染为 RenderResult

        Args:
            view_name: 视图名称，如 "score_card", "user_card"
            data: 渲染数据
            **kwargs: 额外参数，如 skin、width、height 等

        Returns:
            RenderResult: 统一的渲染结果
        """
        ...

    def supports(self, view_name: str) -> bool:
        """
        检查是否支持渲染指定视图

        Args:
            view_name: 视图名称

        Returns:
            bool: 是否支持
        """
        ...


class RenderAdapter(ABC):
    """
    渲染适配器基类

    所有具体的渲染适配器都应继承此类
    """

    def __init__(self, config: dict[str, Any] | None = None) -> None:
        """
        初始化适配器

        Args:
            config: 适配器配置
        """
        self.config = config or {}

    @abstractmethod
    async def render(
        self,
        view_name: str,
        data: dict[str, Any],
        **kwargs: Any,
    ) -> RenderResult:
        """
        将数据渲染为 RenderResult

        Args:
            view_name: 视图名称
            data: 渲染数据
            **kwargs: 额外参数

        Returns:
            RenderResult: 渲染结果
        """
        raise NotImplementedError

    @abstractmethod
    def supports(self, view_name: str) -> bool:
        """
        检查是否支持渲染指定视图

        Args:
            view_name: 视图名称

        Returns:
            bool: 是否支持
        """
        raise NotImplementedError


class NoRendererAvailableError(Exception):
    """
    没有可用渲染引擎时抛出的异常

    当 RenderService 找不到任何支持指定视图的引擎时抛出
    """

    def __init__(self, view_name: str) -> None:
        """
        初始化异常

        Args:
            view_name: 视图名称
        """
        self.view_name = view_name
        super().__init__(f"No renderer available for view: {view_name}")
