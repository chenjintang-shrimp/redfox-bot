"""QQ command for clearing the process-local memory cache."""

from nonebot import on_command
from nonebot.adapters.onebot.v11 import MessageEvent

from adapters.qq_adapter import QQAdapter
from utils.caches import clear_cache
from utils.strings import format_template

cacheclear_cmd = on_command("cacheclear", priority=5)

adapter = QQAdapter()


@cacheclear_cmd.handle()
async def handle_cacheclear(event: MessageEvent) -> None:
    """Clear every key from the current bot process's in-memory cache."""
    try:
        await clear_cache()
        await cacheclear_cmd.send(format_template("CACHE_CLEAR_SUCCESS", locale="zh"))
    except Exception as error:
        await adapter.handle_error(event, error, locale="zh")
