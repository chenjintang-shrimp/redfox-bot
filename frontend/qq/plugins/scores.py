from nonebot import on_command
from nonebot.adapters.onebot.v11 import MessageEvent, MessageSegment
from nonebot.params import CommandArg

from backend.user_qq import get_user_info
from backend.expections.user import UserNotBindError
from backend.expections.scores import ScoreQueryError
from frontend.qq.util import resolve_username_qq
from renderer.scores import (
    render_user_beatmap_score_card,
    render_user_score_list_image,
    render_user_recent_score_card,
    render_user_today_bp_image,
)
from utils.logger import get_logger

logger = get_logger("qq.plugins.scores")

ss_cmd = on_command("ss", priority=5)
ps_cmd = on_command("ps", priority=5)
rs_cmd = on_command("rs", priority=5)
t_cmd = on_command("t", priority=5)
p_cmd = on_command("p", priority=5)
r_cmd = on_command("r", priority=5)
b_cmd = on_command("b", priority=5)
bs_cmd = on_command("bs", priority=5)


@ss_cmd.handle()
async def handle_ss(event: MessageEvent, args=CommandArg()):
    """查询谱面成绩 (图片版)"""
    qq_id = event.user_id
    text = args.extract_plain_text().strip()

    if not text:
        await ss_cmd.finish("请提供谱面ID，格式: !ss <beatmap_id>")
        return

    try:
        beatmap_id = int(text)
    except ValueError:
        await ss_cmd.finish("谱面ID必须是数字")
        return

    try:
        username = await resolve_username_qq(qq_id, None)
        user_info = await get_user_info(username)
        user_id = user_info["id"]

        image = await render_user_beatmap_score_card(user_id, beatmap_id)
        await ss_cmd.finish(MessageSegment.image(image))
    except UserNotBindError:
        await ss_cmd.finish("请先使用 !bind <osu用户名> 绑定账号")
    except ScoreQueryError as e:
        await ss_cmd.finish(f"查询失败: {e.error_msg}")
    except Exception as e:
        logger.error(f"查询谱面成绩失败: {e}")
        await ss_cmd.finish("查询失败，请稍后重试")


@ps_cmd.handle()
async def handle_ps(event: MessageEvent, args=CommandArg()):
    """查询最近通过成绩 (图片版)"""
    qq_id = event.user_id
    username_arg = args.extract_plain_text().strip()

    try:
        username = await resolve_username_qq(qq_id, username_arg if username_arg else None)
        user_info = await get_user_info(username)
        user_id = user_info["id"]

        image = await render_user_score_list_image(
            user_id, username, score_type="recent", include_fails=False
        )
        await ps_cmd.finish(MessageSegment.image(image))
    except UserNotBindError:
        await ps_cmd.finish("请先使用 !bind <osu用户名> 绑定账号，或指定用户名查询")
    except ScoreQueryError as e:
        await ps_cmd.finish(f"查询失败: {e.error_msg}")
    except Exception as e:
        logger.error(f"查询最近通过成绩失败: {e}")
        await ps_cmd.finish("查询失败，请稍后重试")


@rs_cmd.handle()
async def handle_rs(event: MessageEvent, args=CommandArg()):
    """查询最近成绩，包含失败 (图片版)"""
    qq_id = event.user_id
    username_arg = args.extract_plain_text().strip()

    try:
        username = await resolve_username_qq(qq_id, username_arg if username_arg else None)
        user_info = await get_user_info(username)
        user_id = user_info["id"]

        image = await render_user_score_list_image(
            user_id, username, score_type="recent", include_fails=True
        )
        await rs_cmd.finish(MessageSegment.image(image))
    except UserNotBindError:
        await rs_cmd.finish("请先使用 !bind <osu用户名> 绑定账号，或指定用户名查询")
    except ScoreQueryError as e:
        await ps_cmd.finish(f"查询失败: {e.error_msg}")
    except Exception as e:
        logger.error(f"查询最近成绩失败: {e}")
        await rs_cmd.finish("查询失败，请稍后重试")


@t_cmd.handle()
async def handle_t(event: MessageEvent, args=CommandArg()):
    """查询今日BP (图片版)"""
    qq_id = event.user_id
    username_arg = args.extract_plain_text().strip()

    try:
        username = await resolve_username_qq(qq_id, username_arg if username_arg else None)
        user_info = await get_user_info(username)
        user_id = user_info["id"]

        image = await render_user_today_bp_image(user_id, username)
        await t_cmd.finish(MessageSegment.image(image))
    except UserNotBindError:
        await t_cmd.finish("请先使用 !bind <osu用户名> 绑定账号，或指定用户名查询")
    except ScoreQueryError as e:
        await t_cmd.finish(f"查询失败: {e.error_msg}")
    except Exception as e:
        logger.error(f"查询今日BP失败: {e}")
        await t_cmd.finish("查询失败，请稍后重试")


@p_cmd.handle()
async def handle_p(event: MessageEvent, args=CommandArg()):
    """查询最新通过成绩 (图片版)"""
    qq_id = event.user_id
    username_arg = args.extract_plain_text().strip()

    try:
        username = await resolve_username_qq(qq_id, username_arg if username_arg else None)
        user_info = await get_user_info(username)
        user_id = user_info["id"]

        image = await render_user_recent_score_card(user_id, include_fails=False)
        await p_cmd.finish(MessageSegment.image(image))
    except UserNotBindError:
        await p_cmd.finish("请先使用 !bind <osu用户名> 绑定账号，或指定用户名查询")
    except ScoreQueryError as e:
        await p_cmd.finish(f"查询失败: {e.error_msg}")
    except Exception as e:
        logger.error(f"查询最新通过成绩失败: {e}")
        await p_cmd.finish("查询失败，请稍后重试")


@r_cmd.handle()
async def handle_r(event: MessageEvent, args=CommandArg()):
    """查询最新成绩，包含失败 (图片版)"""
    qq_id = event.user_id
    username_arg = args.extract_plain_text().strip()

    try:
        username = await resolve_username_qq(qq_id, username_arg if username_arg else None)
        user_info = await get_user_info(username)
        user_id = user_info["id"]

        image = await render_user_recent_score_card(user_id, include_fails=True)
        await r_cmd.finish(MessageSegment.image(image))
    except UserNotBindError:
        await r_cmd.finish("请先使用 !bind <osu用户名> 绑定账号，或指定用户名查询")
    except ScoreQueryError as e:
        await r_cmd.finish(f"查询失败: {e.error_msg}")
    except Exception as e:
        logger.error(f"查询最新成绩失败: {e}")
        await r_cmd.finish("查询失败，请稍后重试")


@b_cmd.handle()
async def handle_b(event: MessageEvent, args=CommandArg()):
    """查询最佳成绩 (图片版，单条)"""
    qq_id = event.user_id
    username_arg = args.extract_plain_text().strip()

    try:
        username = await resolve_username_qq(qq_id, username_arg if username_arg else None)
        user_info = await get_user_info(username)
        user_id = user_info["id"]

        image = await render_user_score_list_image(
            user_id, username, score_type="best", include_fails=False, count=1
        )
        await b_cmd.finish(MessageSegment.image(image))
    except UserNotBindError:
        await b_cmd.finish("请先使用 !bind <osu用户名> 绑定账号，或指定用户名查询")
    except ScoreQueryError as e:
        await b_cmd.finish(f"查询失败: {e.error_msg}")
    except Exception as e:
        logger.error(f"查询最佳成绩失败: {e}")
        await b_cmd.finish("查询失败，请稍后重试")


@bs_cmd.handle()
async def handle_bs(event: MessageEvent, args=CommandArg()):
    """查询最佳成绩列表 (图片版，多条)"""
    qq_id = event.user_id
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
        username = await resolve_username_qq(qq_id, username_arg if username_arg else None)
        user_info = await get_user_info(username)
        user_id = user_info["id"]

        image = await render_user_score_list_image(
            user_id, username, score_type="best", include_fails=False, count=count
        )
        await bs_cmd.finish(MessageSegment.image(image))
    except UserNotBindError:
        await bs_cmd.finish("请先使用 !bind <osu用户名> 绑定账号，或指定用户名查询")
    except ScoreQueryError as e:
        await bs_cmd.finish(f"查询失败: {e.error_msg}")
    except Exception as e:
        logger.error(f"查询最佳成绩列表失败: {e}")
        await bs_cmd.finish("查询失败，请稍后重试")
