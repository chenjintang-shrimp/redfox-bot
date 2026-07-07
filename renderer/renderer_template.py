# renderers/error_handler.py
import functools
import traceback
from collections.abc import Awaitable, Callable
from typing import Any, ParamSpec, TypeVar, cast, overload

from utils.strings import format_template
from utils.logger import get_logger

logger = get_logger("renderer")

P = ParamSpec("P")
R = TypeVar("R")
RendererFunc = Callable[P, Awaitable[R]]
AnyRendererFunc = Callable[..., Awaitable[Any]]


def handle_exception(e: Exception, locale: str = "en") -> str:
    """
    根据异常类型返回对应的格式化字符串

    使用异常的 template_key 属性和 __dict__ 作为模板变量

    Args:
        e: 异常对象
        locale: 语言代码，默认"en"
    """
    template_key = getattr(e, "template_key", None)

    if template_key:
        context_vars = getattr(e, "__dict__", {})
        try:
            return format_template(template_key, context=context_vars, locale=locale)
        except Exception as fmt_error:
            logger.error(f"Failed to format template {template_key}: {fmt_error}")
            error_msg = f"[{type(e).__name__}] {str(e)}"
            return format_template(
                "RENDERER_ERROR_TEMPLATE", locale=locale, error_msg=error_msg
            )

    error_msg = f"[{type(e).__name__}] {str(e)}"
    return format_template(
        "RENDERER_ERROR_TEMPLATE", locale=locale, error_msg=error_msg
    )


@overload
def renderer(view_name: str | None = None) -> Callable[[RendererFunc[P, R]], RendererFunc[P, R]]:
    ...


@overload
def renderer(view_name: RendererFunc[P, R]) -> RendererFunc[P, R]:
    ...


def renderer(
    view_name: str | AnyRendererFunc | None = None,
) -> Callable[[RendererFunc[P, R]], RendererFunc[P, R]] | AnyRendererFunc:
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

    def decorator(func: RendererFunc[P, R]) -> RendererFunc[P, R]:
        func_name = getattr(func, "__name__", type(func).__name__)
        actual_view_name = view_name if isinstance(view_name, str) else func_name
        returns_bytes = getattr(func, "__annotations__", {}).get("return") is bytes

        @functools.wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                logger.error(f"Error in renderer '{func_name}': {e}")
                logger.error(traceback.format_exc())
                if returns_bytes:
                    raise
                locale_value = kwargs.get("locale", "en")
                locale = locale_value if isinstance(locale_value, str) else "en"
                return cast(R, handle_exception(e, locale))

        setattr(wrapper, "__view_name__", actual_view_name)
        return cast(RendererFunc[P, R], wrapper)

    if callable(view_name):
        return decorator(cast(AnyRendererFunc, view_name))
    return decorator
