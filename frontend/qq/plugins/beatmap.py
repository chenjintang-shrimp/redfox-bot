from nonebot import on_command
from nonebot.adapters.onebot.v11 import MessageEvent
from nonebot.params import CommandArg

from adapters.qq_adapter import QQAdapter
from renderer.beatmap import render_beatmap_info
from utils.logger import get_logger
from utils.strings import format_template

logger = get_logger("qq.plugins.beatmap")

m_cmd = on_command("m", priority=5)

adapter = QQAdapter()


@m_cmd.handle()
async def handle_m(event: MessageEvent, args=CommandArg()):
    text = args.extract_plain_text().strip()

    if not text:
        await m_cmd.send(format_template("BEATMAP_ID_REQUIRED", locale="zh"))
        return

    try:
        beatmap_id = int(text)
    except ValueError:
        await m_cmd.send(format_template("BEATMAP_ID_INVALID", locale="zh"))
        return

    try:
        msg = await render_beatmap_info(beatmap_id, locale="zh")
        await m_cmd.send(msg)
    except Exception as e:
        await adapter.handle_error(event, e, locale="zh")
