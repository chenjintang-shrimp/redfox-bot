from nonebot import on_command
from nonebot.adapters.onebot.v11 import MessageEvent
from nonebot.params import CommandArg

from backend.expections.beatmap import BeatmapNotFoundError
from renderer.beatmap import render_beatmap_info
from utils.logger import get_logger
from utils.strings import format_template

logger = get_logger("qq.plugins.beatmap")

m_cmd = on_command("m", priority=5)


@m_cmd.handle()
async def handle_m(event: MessageEvent, args=CommandArg()):
    text = args.extract_plain_text().strip()

    if not text:
        await m_cmd.finish(format_template("QQ_BEATMAP_ID_REQUIRED_TEMPLATE"))
        return

    try:
        beatmap_id = int(text)
    except ValueError:
        await m_cmd.finish(format_template("QQ_BEATMAP_ID_INVALID_TEMPLATE"))
        return

    try:
        msg = await render_beatmap_info(beatmap_id)
        await m_cmd.finish(msg)
    except BeatmapNotFoundError:
        await m_cmd.finish(format_template("BEATMAP_NOT_FOUND_TEMPLATE"))
    except Exception as e:
        logger.error(f"查询谱面失败: {e}")
        await m_cmd.finish(format_template("QQ_QUERY_FAILED_TEMPLATE"))
