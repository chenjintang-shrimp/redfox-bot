# renderers/error_handler.py
import functools
import traceback
from typing import Callable, Any

from backend.expections import (
    UserQueryError,
    UserNotBindError,
    BindExistError,
    ScoreQueryError,
    # 未来加的异常也放这里
)
from utils.flt_mgr import apply_minifilters
from utils.strings import format_template
from utils.logger import get_logger

logger = get_logger("renderer")


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
                return format_template("USER_NOT_FOUND_TEMPLATE")

            case UserQueryError():
                return format_template(
                    "USER_QUERY_ERROR_TEMPLATE", error_msg=e.error_msg
                )

            # 用户未绑定
            case UserNotBindError():
                return format_template(
                    "USER_NOT_BOUND_TEMPLATE", user=e.user_context
                )

            # 已绑定其他账号
            case BindExistError():
                return format_template(
                    "USER_BIND_EXISTING_TEMPLATE", username=e.username
                )

            # === 未来加新异常，只需要在这里加一个 case ===
            case ScoreQueryError() if e.status_code == 404:
                return format_template(
                    "SCORE_NOT_FOUND_TEMPLATE",
                    username=e.username, beatmap_id=e.beatmap_id
                )

            case ScoreQueryError():
                return format_template(
                    "SCORE_QUERY_ERROR_TEMPLATE", error_msg=e.error_msg
                )

            # 兜底：未知异常
            case _:
                error_msg = f"[{type(e).__name__}] {str(e)}"
                return format_template("RENDERER_ERROR_TEMPLATE", error_msg=error_msg)


def renderer(hook_name: str | None = None):
    """
    装饰器：自动捕获异常、应用 minifilter 并调用统一处理器

    Args:
        hook_name: 可选，声明该 renderer 的 hook 名称，用于自动应用 minifilter
                  为 None 时不应用 minifilter

    用法:
        @renderer("user_card")  # 声明 hook 名称
        async def render_user_card_image(data: dict, ...) -> bytes:
            # 会自动应用所有声明了 hooks: [user_card] 的 minifilter
            ...

        @renderer()  # 不声明 hook，不应用 minifilter
        async def render_simple_text(data: dict) -> str:
            ...
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            # 如果第一个参数是 dict，尝试应用 minifilter
            if hook_name and args and isinstance(args[0], dict):
                try:
                    original_data = args[0]
                    processed_data = apply_minifilters(hook_name, original_data)
                    # 替换第一个参数为处理后的数据
                    args = (processed_data,) + args[1:]
                    logger.debug(f"[renderer] 已应用 minifilter [{hook_name}]")
                except Exception as e:
                    logger.error(f"[renderer] 应用 minifilter 失败 [{hook_name}]: {e}")
                    # 失败时继续使用原始数据

            try:
                return await func(*args, **kwargs)
            except Exception as e:
                # 记录详细错误信息到日志
                logger.error(f"Error in renderer '{func.__name__}': {e}")
                logger.error(traceback.format_exc())
                return ExceptionHandler.handle(e)

        return wrapper

    return decorator
