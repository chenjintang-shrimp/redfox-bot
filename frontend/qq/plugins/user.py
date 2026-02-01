from nonebot import on_command
from nonebot.adapters.onebot.v11 import MessageEvent, MessageSegment
from nonebot.params import CommandArg

from backend.user_qq import bind_user_qq, get_user_info, unbind_user_qq
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


async def handle_info_text(event: MessageEvent, args):
    """文字版用户信息"""
    qq_id = event.user_id
    username_arg = args.extract_plain_text().strip()

    try:
        username = await resolve_username_qq(qq_id, username_arg if username_arg else None)
    except UserNotBindError:
        await info_short_cmd.finish(format_template("QQ_USER_NOT_BIND_TEMPLATE"))
        return

    try:
        msg = await render_user_info(username)
        await info_short_cmd.finish(msg)
    except UserQueryError as e:
        await info_short_cmd.finish(format_template("QQ_QUERY_ERROR_TEMPLATE", error_msg=e.error_msg))
    except Exception as e:
        logger.error(f"查询用户信息失败: {e}")
        await info_short_cmd.finish(format_template("QQ_QUERY_FAILED_TEMPLATE"))


@info_short_cmd.handle()
async def handle_info_short(event: MessageEvent, args=CommandArg()):
    await handle_info_text(event, args)


@info_cmd.handle()
async def handle_info(event: MessageEvent, args=CommandArg()):
    """图片版用户信息"""
    qq_id = event.user_id
    username_arg = args.extract_plain_text().strip()

    try:
        username = await resolve_username_qq(qq_id, username_arg if username_arg else None)
    except UserNotBindError:
        await info_cmd.finish(format_template("QQ_USER_NOT_BIND_TEMPLATE"))
        return

    try:
        user_data = await get_user_info(username)
        image = await render_user_card_image(user_data)
        await info_cmd.finish(MessageSegment.image(image))
    except UserQueryError as e:
        await info_cmd.finish(format_template("QQ_QUERY_ERROR_TEMPLATE", error_msg=e.error_msg))
    except Exception as e:
        logger.error(f"生成用户卡片失败: {e}")
        await info_cmd.finish(format_template("QQ_RENDER_FAILED_TEMPLATE"))


@bind_cmd.handle()
async def handle_bind(event: MessageEvent, args=CommandArg()):
    qq_id = event.user_id
    username = args.extract_plain_text().strip()

    if not username:
        await bind_cmd.finish(format_template("USER_NOT_FOUND_TEMPLATE"))
        return

    try:
        await bind_user_qq(qq_id, username)
        await bind_cmd.finish(format_template("QQ_BIND_SUCCESS_TEMPLATE", username=username))
    except BindExistError:
        await bind_cmd.finish(format_template("QQ_BIND_EXIST_TEMPLATE"))
    except UserQueryError:
        await bind_cmd.finish(format_template("QQ_BIND_USER_NOT_FOUND_TEMPLATE", username=username))
    except Exception as e:
        logger.error(f"绑定用户失败: {e}")
        await bind_cmd.finish(format_template("QQ_BIND_FAILED_TEMPLATE"))


@unbind_cmd.handle()
async def handle_unbind(event: MessageEvent):
    qq_id = event.user_id

    try:
        deleted = await unbind_user_qq(qq_id)
        if deleted:
            await unbind_cmd.finish(format_template("QQ_UNBIND_SUCCESS_TEMPLATE"))
        else:
            await unbind_cmd.finish(format_template("QQ_UNBIND_NOT_BOUND_TEMPLATE"))
    except Exception as e:
        logger.error(f"解绑用户失败: {e}")
        await unbind_cmd.finish(format_template("QQ_UNBIND_FAILED_TEMPLATE"))
