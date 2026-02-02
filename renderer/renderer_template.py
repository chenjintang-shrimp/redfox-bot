# renderers/error_handler.py
import functools
import traceback
from typing import Callable, Any, Protocol, runtime_checkable

from backend.expections import (
    BindExistError,
    NoSkinAvailableError,
    ScoreQueryError,
    UserNotBindError,
    UserQueryError,
    # 未来加的异常也放这里
)
from utils.strings import format_template
from utils.logger import get_logger

logger = get_logger("renderer")


@runtime_checkable
class RendererFunc(Protocol):
    """Renderer 函数协议，包含 __view_name__ 属性"""
    __view_name__: str
    async def __call__(self, *args: Any, **kwargs: Any) -> Any: ...


class ExceptionHandler:
    """
    统一异常处理器
    负责将异常转换为用户友好的字符串
    """

    @staticmethod
    def handle(e: Exception) -> str:
        """
        根据异常类型返回对应的格式化字符串
        """
        match e:
            # 用户查询错误
            case UserQueryError() if e.status_code == 404:
                return format_template("USER_NOT_FOUND_TEMPLATE", locale="en")

            case UserQueryError():
                return format_template(
                    "USER_QUERY_ERROR_TEMPLATE", locale="en", error_msg=e.error_msg
                )

            # 用户未绑定
            case UserNotBindError():
                return format_template("USER_NOT_BOUND_TEMPLATE", locale="en", user=e.user_context)

            # 已绑定其他账号
            case BindExistError():
                return format_template(
                    "USER_BIND_EXISTING_TEMPLATE", locale="en", username=e.username
                )

            # === 未来加新异常，只需要在这里加一个 case ===
            case ScoreQueryError() if e.status_code == 404:
                return format_template(
                    "SCORE_NOT_FOUND_TEMPLATE",
                    locale="en",
                    username=e.username,
                    beatmap_id=e.beatmap_id,
                )

            case ScoreQueryError():
                return format_template(
                    "SCORE_QUERY_ERROR_TEMPLATE", locale="en", error_msg=e.error_msg
                )

            # 没有可用皮肤
            case NoSkinAvailableError():
                return format_template(
                    "NO_SKIN_AVAILABLE_TEMPLATE",
                    locale="en",
                    skin_name=e.skin_name,
                    template_name=e.template_name,
                )

            # 兜底：未知异常
            case _:
                error_msg = f"[{type(e).__name__}] {str(e)}"
                return format_template("RENDERER_ERROR_TEMPLATE", locale="en", error_msg=error_msg)


def renderer(view_name: str | Callable | None = None) -> Callable[[Callable], RendererFunc]:
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

    def decorator(func: Callable) -> RendererFunc:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                # 记录详细错误信息到日志
                logger.error(f"Error in renderer '{func.__name__}': {e}")
                logger.error(traceback.format_exc())
                return ExceptionHandler.handle(e)

        # 保存视图名，供 minifilter 使用
        # 优先使用显式声明的 view_name，否则使用函数名
        actual_view_name = view_name if isinstance(view_name, str) else func.__name__
        wrapper.__view_name__ = actual_view_name  # type: ignore[attr-defined]
        return wrapper  # type: ignore[return-value]


    return decorator
