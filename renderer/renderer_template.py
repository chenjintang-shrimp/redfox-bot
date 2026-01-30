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


def renderer(func: Callable) -> Callable:
    """
    装饰器：自动捕获异常并调用统一处理器
    """

    @functools.wraps(func)
    async def wrapper(*args, **kwargs) -> Any:
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            # 记录详细错误信息到日志
            logger.error(f"Error in renderer '{func.__name__}': {e}")
            logger.error(traceback.format_exc())
            return ExceptionHandler.handle(e)

    return wrapper
