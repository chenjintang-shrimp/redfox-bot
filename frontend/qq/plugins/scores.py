import traceback

from nonebot import on_command
from nonebot.adapters.onebot.v11 import MessageEvent
from nonebot.params import CommandArg

from adapters.qq_adapter import QQAdapter
from services import UserService
from renderer.scores import (
    render_user_beatmap_score_card,
    render_user_score_list_image,
    render_user_recent_score_card,
    render_user_today_bp_image,
)
from utils.logger import get_logger
from utils.strings import format_template

logger = get_logger("qq.plugins.scores")

ss_cmd = on_command("ss", priority=5)
ps_cmd = on_command("ps", priority=5)
rs_cmd = on_command("rs", priority=5)
t_cmd = on_command("t", priority=5)
p_cmd = on_command("p", priority=5)
r_cmd = on_command("r", priority=5)
b_cmd = on_command("b", priority=5)
bs_cmd = on_command("bs", priority=5)

adapter = QQAdapter()


async def _get_user_info_from_event(event: MessageEvent, username_arg: str | None):
    """从事件中获取用户信息和上下文

    Returns:
        tuple: (context, user_id, username)
    """
    context = await adapter.get_user_context(event)
    username = await UserService.resolve_username(context, username_arg)
    user_info = await UserService.get_user_info(username)
    return context, user_info.id, username


@ss_cmd.handle()
async def handle_ss(event: MessageEvent, args=CommandArg()):
    """查询谱面成绩 (图片版)"""
    text = args.extract_plain_text().strip()

    if not text:
        await ss_cmd.send(format_template("BEATMAP_ID_REQUIRED", locale="zh"))
        return

    try:
        beatmap_id = int(text)
    except ValueError:
        await ss_cmd.send(format_template("BEATMAP_ID_INVALID", locale="zh"))
        return

    try:
        _, user_id, _ = await _get_user_info_from_event(event, None)
        image = await render_user_beatmap_score_card(user_id, beatmap_id)
        await adapter.send_image_bytes(event, image)
    except Exception as e:
        await adapter.handle_error(event, e, locale="zh")


@ps_cmd.handle()
async def handle_ps(event: MessageEvent, args=CommandArg()):
    """查询最近通过成绩 (图片版)"""
    username_arg = args.extract_plain_text().strip()

    try:
        context, user_id, username = await _get_user_info_from_event(
            event, username_arg if username_arg else None
        )
        gamemode = await UserService.get_gamemode(context)

        image = await render_user_score_list_image(
            user_id, username, score_type="recent", include_fails=False, mode=gamemode
        )
        await adapter.send_image_bytes(event, image)
    except Exception as e:
        await adapter.handle_error(event, e, locale="zh")


@rs_cmd.handle()
async def handle_rs(event: MessageEvent, args=CommandArg()):
    """查询最近成绩，包含失败 (图片版)"""
    username_arg = args.extract_plain_text().strip()

    try:
        context, user_id, username = await _get_user_info_from_event(
            event, username_arg if username_arg else None
        )
        gamemode = await UserService.get_gamemode(context)

        image = await render_user_score_list_image(
            user_id, username, score_type="recent", include_fails=True, mode=gamemode
        )
        await adapter.send_image_bytes(event, image)
    except Exception as e:
        await adapter.handle_error(event, e, locale="zh")


@t_cmd.handle()
async def handle_t(event: MessageEvent, args=CommandArg()):
    """查询今日BP (图片版)"""
    username_arg = args.extract_plain_text().strip()

    try:
        context, user_id, username = await _get_user_info_from_event(
            event, username_arg if username_arg else None
        )
        gamemode = await UserService.get_gamemode(context)

        image = await render_user_today_bp_image(user_id, username, mode=gamemode)
        await adapter.send_image_bytes(event, image)
    except Exception as e:
        await adapter.handle_error(event, e, locale="zh")


@p_cmd.handle()
async def handle_p(event: MessageEvent, args=CommandArg()):
    """查询最新通过成绩 (图片版)"""
    username_arg = args.extract_plain_text().strip()

    try:
        context, user_id, _ = await _get_user_info_from_event(
            event, username_arg if username_arg else None
        )
        gamemode = await UserService.get_gamemode(context)

        image = await render_user_recent_score_card(
            user_id, include_fails=False, mode=gamemode
        )
        await adapter.send_image_bytes(event, image)
    except Exception as e:
        await adapter.handle_error(event, e, locale="zh")


@r_cmd.handle()
async def handle_r(event: MessageEvent, args=CommandArg()):
    """查询最新成绩，包含失败 (图片版)"""
    username_arg = args.extract_plain_text().strip()

    try:
        context, user_id, _ = await _get_user_info_from_event(
            event, username_arg if username_arg else None
        )
        gamemode = await UserService.get_gamemode(context)

        image = await render_user_recent_score_card(
            user_id, include_fails=True, mode=gamemode
        )
        await adapter.send_image_bytes(event, image)
    except Exception as e:
        await adapter.handle_error(event, e, locale="zh")


@b_cmd.handle()
async def handle_b(event: MessageEvent, args=CommandArg()):
    """查询最佳成绩 (图片版，单条)"""
    username_arg = args.extract_plain_text().strip()

    try:
        context, user_id, username = await _get_user_info_from_event(
            event, username_arg if username_arg else None
        )
        gamemode = await UserService.get_gamemode(context)

        image = await render_user_score_list_image(
            user_id,
            username,
            score_type="best",
            include_fails=False,
            count=1,
            mode=gamemode,
        )
        await adapter.send_image_bytes(event, image)
    except Exception as e:
        logger.error(f"查询最佳成绩失败: {e}")
        logger.error(traceback.format_exc())
        await adapter.handle_error(event, e, locale="zh")


@bs_cmd.handle()
async def handle_bs(event: MessageEvent, args=CommandArg()):
    """查询最佳成绩列表 (图片版，多条)"""
    text = args.extract_plain_text().strip()

    # 解析参数：第一个可能是数字(count)，剩下的可能是用户名
    parts = text.split()
    count = 20
    username_arg = ""

    if parts:
        # 尝试解析第一个为数字
        try:
            count = int(parts[0])
            count = min(count, 100)  # 限制最大100
            if len(parts) > 1:
                username_arg = " ".join(parts[1:])
        except ValueError:
            # 第一个不是数字，全部当作用户名
            username_arg = text

    try:
        context, user_id, username = await _get_user_info_from_event(
            event, username_arg if username_arg else None
        )
        gamemode = await UserService.get_gamemode(context)

        image = await render_user_score_list_image(
            user_id,
            username,
            score_type="best",
            include_fails=False,
            count=count,
            mode=gamemode,
        )
        await adapter.send_image_bytes(event, image)
    except Exception as e:
        logger.error(f"查询最佳成绩列表失败: {e}")
        logger.error(traceback.format_exc())
        await adapter.handle_error(event, e, locale="zh")
