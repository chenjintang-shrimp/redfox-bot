# renderers/error_handler.py
import functools
import traceback
from typing import Callable, Any, Protocol, runtime_checkable, TypeVar, cast

from utils.strings import format_template
from utils.logger import get_logger

logger = get_logger("renderer")


@runtime_checkable
class RendererFunc(Protocol):
    """Renderer 函数协议，包含 __view_name__ 属性"""

    __view_name__: str

    async def __call__(self, *args: Any, **kwargs: Any) -> Any: ...


# 类型变量用于保留函数签名
F = TypeVar("F", bound=Callable[..., Any])


class ExceptionHandler:
    """
    统一异常处理器
    负责将异常转换为用户友好的字符串
    """

    @staticmethod
    def handle(e: Exception, locale: str = "en") -> str:
        """
        根据异常类型返回对应的格式化字符串

        使用异常的 template_key 属性和 __dict__ 作为模板变量

        Args:
            e: 异常对象
            locale: 语言代码，默认"en"
        """
        # 获取异常的模板key
        template_key = getattr(e, "template_key", None)

        if template_key:
            # 使用异常的 __dict__ 作为模板变量
            context_vars = getattr(e, "__dict__", {})
            try:
                return format_template(template_key, locale=locale, **context_vars)
            except Exception as fmt_error:
                logger.error(f"Failed to format template {template_key}: {fmt_error}")
                # 模板格式化失败，回退到通用错误
                error_msg = f"[{type(e).__name__}] {str(e)}"
                return format_template(
                    "RENDERER_ERROR_TEMPLATE", locale=locale, error_msg=error_msg
                )

        # 兜底：未知异常
        error_msg = f"[{type(e).__name__}] {str(e)}"
        return format_template(
            "RENDERER_ERROR_TEMPLATE", locale=locale, error_msg=error_msg
        )


def renderer(
    view_name: str | F | None = None,
) -> Callable[[F], F]:
    """
    装饰器：自动捕获异常并调用统一处理器

    支持两种用法:
        1. 带视图名: @renderer("user_beatmap_score_card")
        2. 自动推断: @renderer (使用函数名作为视图名)

    用法:
        @renderer("user_beatmap_score_card")
        async def render_user_beatmap_score_card(...) -> Any:
            ...

        @renderer
        async def render_something(...) -> Any:
            ...
    """

    def decorator(func: F) -> F:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                # 记录详细错误信息到日志
                logger.error(f"Error in renderer '{func.__name__}': {e}")
                logger.error(traceback.format_exc())
                # 从 kwargs 中提取 locale，默认使用 "en"
                locale = kwargs.get("locale", "en")
                return ExceptionHandler.handle(e, locale)

        # 保存视图名，供 minifilter 使用
        # 优先使用显式声明的 view_name，否则使用函数名
        actual_view_name = view_name if isinstance(view_name, str) else func.__name__
        wrapper.__view_name__ = actual_view_name  # type: ignore[attr-defined]
        # 使用 cast 保留原函数类型签名
        return cast(F, wrapper)

    # 处理 @renderer 不带括号的情况
    if callable(view_name) and not isinstance(view_name, str):
        func = view_name
        view_name = None
        return decorator(func)

    return decorator
