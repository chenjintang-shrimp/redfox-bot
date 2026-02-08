from nonebot import on_command
from nonebot.adapters.onebot.v11 import MessageEvent, MessageSegment
from nonebot.params import CommandArg

from backend.user_qq import bind_user_qq, get_user_info, unbind_user_qq, set_user_gamemode_qq, get_user_gamemode_qq
from backend.expections.user import BindExistError, UserNotBindError, UserQueryError
from frontend.qq.util import resolve_username_qq
from renderer.user import render_user_card_image, render_user_info
from utils.logger import get_logger
from utils.strings import format_template

logger = get_logger("qq.plugins.user")

info_cmd = on_command("info", priority=5)
info_short_cmd = on_command("i", priority=5)
bind_cmd = on_command("bind", priority=5)
unbind_cmd = on_command("unbind", priority=5)
switch_gamemode_cmd = on_command("set_gamemode", priority=5)


async def handle_info_text(event: MessageEvent, args):
    """文字版用户信息"""
    qq_id = event.user_id
    username_arg = args.extract_plain_text().strip()

    try:
        username = await resolve_username_qq(
            qq_id, username_arg if username_arg else None
        )
    except UserNotBindError:
        await info_short_cmd.send(format_template("USER_NOT_BIND_HINT", locale="zh"))
        return

    try:
        msg = await render_user_info(username, locale="zh")  # type: ignore[call-arg]
        await info_short_cmd.send(msg)
    except UserQueryError as e:
        await info_short_cmd.send(
            format_template("USER_QUERY_ERROR", error_msg=e.error_msg, locale="zh")
        )
    except Exception as e:
        logger.error(f"查询用户信息失败: {e}")
        await info_short_cmd.send(format_template("QUERY_FAILED", locale="zh"))


@info_short_cmd.handle()
async def handle_info_short(event: MessageEvent, args=CommandArg()):
    await handle_info_text(event, args)


@info_cmd.handle()
async def handle_info(event: MessageEvent, args=CommandArg()):
    """图片版用户信息"""
    qq_id = event.user_id
    username_arg = args.extract_plain_text().strip()

    try:
        username = await resolve_username_qq(
            qq_id, username_arg if username_arg else None
        )
    except UserNotBindError:
        await info_cmd.send(format_template("USER_NOT_BIND_HINT", locale="zh"))
        return

    try:
        user_data = await get_user_info(username)
        image = await render_user_card_image(user_data)
        await info_cmd.send(MessageSegment.image(image))
    except UserQueryError as e:
        await info_cmd.send(
            format_template("USER_QUERY_ERROR", error_msg=e.error_msg, locale="zh")
        )
    except Exception as e:
        logger.error(f"生成用户卡片失败: {e}")
        await info_cmd.send(format_template("RENDER_FAILED", locale="zh"))


@bind_cmd.handle()
async def handle_bind(event: MessageEvent, args=CommandArg()):
    qq_id = event.user_id
    username = args.extract_plain_text().strip()

    if not username:
        await bind_cmd.send(format_template("USER_NOT_FOUND_TEMPLATE", locale="zh"))
        return

    try:
        await bind_user_qq(qq_id, username)
        await bind_cmd.send(
            format_template("BIND_SUCCESS", username=username, locale="zh")
        )
    except BindExistError:
        await bind_cmd.send(format_template("BIND_EXIST", locale="zh"))
    except UserQueryError:
        await bind_cmd.send(
            format_template("BIND_USER_NOT_FOUND", username=username, locale="zh")
        )
    except Exception as e:
        logger.error(f"绑定用户失败: {e}")
        await bind_cmd.send(format_template("BIND_FAILED", locale="zh"))


@unbind_cmd.handle()
async def handle_unbind(event: MessageEvent):
    qq_id = event.user_id

    try:
        deleted = await unbind_user_qq(qq_id)
        if deleted:
            await unbind_cmd.send(format_template("UNBIND_SUCCESS", locale="zh"))
        else:
            await unbind_cmd.send(format_template("UNBIND_NOT_BOUND", locale="zh"))
    except Exception as e:
        logger.error(f"解绑用户失败: {e}")
        await unbind_cmd.send(format_template("UNBIND_FAILED", locale="zh"))


@switch_gamemode_cmd.handle()
async def handle_switch_gamemode(event: MessageEvent, args=CommandArg()):
    """设置默认游戏模式"""
    qq_id = event.user_id
    gamemode = args.extract_plain_text().strip()

    if not gamemode:
        # 显示当前设置
        current_mode = await get_user_gamemode_qq(qq_id)
        if current_mode:
            await switch_gamemode_cmd.send(
                format_template("GAMEMODE_CURRENT", gamemode=current_mode, locale="zh")
            )
        else:
            await switch_gamemode_cmd.send(
                format_template("GAMEMODE_NOT_SET", locale="zh")
            )
        return

    # 设置游戏模式（不限制输入，支持任意私服模式）
    success = await set_user_gamemode_qq(qq_id, gamemode)
    if success:
        await switch_gamemode_cmd.send(
            format_template("GAMEMODE_SET_SUCCESS", gamemode=gamemode, locale="zh")
        )
    else:
        await switch_gamemode_cmd.send(
            format_template("GAMEMODE_SET_FAILED_NOT_BOUND", locale="zh")
        )