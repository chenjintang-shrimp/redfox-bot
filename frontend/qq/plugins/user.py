from nonebot import on_command
from nonebot.adapters.onebot.v11 import MessageEvent, MessageSegment
from nonebot.params import CommandArg

from adapters.qq_adapter import QQAdapter
from services import UserService
from renderer.user import render_user_card_image, render_user_info
from utils.logger import get_logger
from utils.strings import format_template

logger = get_logger("qq.plugins.user")

info_cmd = on_command("info", priority=5)
info_short_cmd = on_command("i", priority=5)
bind_cmd = on_command("bind", priority=5)
unbind_cmd = on_command("unbind", priority=5)
switch_gamemode_cmd = on_command("set_gamemode", priority=5)

adapter = QQAdapter()


async def handle_info_text(event: MessageEvent, args):
    """文字版用户信息"""
    username_arg = args.extract_plain_text().strip()

    try:
        context = await adapter.get_user_context(event)
        username = await UserService.resolve_username(
            context, username_arg if username_arg else None
        )
    except Exception as e:
        await adapter.handle_error(event, e, locale="zh")
        return

    try:
        msg = await render_user_info(username, locale="zh")  # type: ignore[call-arg]
        await info_short_cmd.send(msg)
    except Exception as e:
        await adapter.handle_error(event, e, locale="zh")


@info_short_cmd.handle()
async def handle_info_short(event: MessageEvent, args=CommandArg()):
    await handle_info_text(event, args)


@info_cmd.handle()
async def handle_info(event: MessageEvent, args=CommandArg()):
    """图片版用户信息"""
    username_arg = args.extract_plain_text().strip()

    try:
        context = await adapter.get_user_context(event)
        username = await UserService.resolve_username(
            context, username_arg if username_arg else None
        )
    except Exception as e:
        await adapter.handle_error(event, e, locale="zh")
        return

    try:
        user_info = await UserService.get_user_info(username)
        image = await render_user_card_image(user_info.__dict__)
        await info_cmd.send(MessageSegment.image(image))
    except Exception as e:
        await adapter.handle_error(event, e, locale="zh")


@bind_cmd.handle()
async def handle_bind(event: MessageEvent, args=CommandArg()):
    username = args.extract_plain_text().strip()

    if not username:
        await bind_cmd.send(format_template("USER_NOT_FOUND_TEMPLATE", locale="zh"))
        return

    try:
        context = await adapter.get_user_context(event)
        user_info = await UserService.bind_user(context, username)
        await bind_cmd.send(
            format_template(
                "USER_BIND_SUCCESS_TEMPLATE", username=user_info.username, locale="zh"
            )
        )
    except Exception as e:
        await adapter.handle_error(event, e, locale="zh")


@unbind_cmd.handle()
async def handle_unbind(event: MessageEvent):
    try:
        context = await adapter.get_user_context(event)
        deleted = await UserService.unbind_user(context)
        if deleted:
            await unbind_cmd.send(format_template("USER_UNBIND_SUCCESS_TEMPLATE", locale="zh"))
        else:
            await unbind_cmd.send(format_template("USER_NOT_BOUND_TEMPLATE", locale="zh", user="你"))
    except Exception as e:
        await adapter.handle_error(event, e, locale="zh")


@switch_gamemode_cmd.handle()
async def handle_switch_gamemode(event: MessageEvent, args=CommandArg()):
    """设置默认游戏模式"""
    gamemode = args.extract_plain_text().strip()

    try:
        context = await adapter.get_user_context(event)

        if not gamemode:
            # 显示当前设置
            current_mode = await UserService.get_gamemode(context)
            if current_mode:
                await switch_gamemode_cmd.send(
                    format_template("GAMEMODE_CURRENT", gamemode=current_mode, locale="zh")
                )
            else:
                await switch_gamemode_cmd.send(
                    format_template("GAMEMODE_NOT_SET", locale="zh")
                )
            return

        # 设置游戏模式
        success = await UserService.set_gamemode(context, gamemode)
        if success:
            await switch_gamemode_cmd.send(
                format_template("GAMEMODE_SET_SUCCESS", gamemode=gamemode, locale="zh")
            )
        else:
            await switch_gamemode_cmd.send(
                format_template("GAMEMODE_SET_FAILED_NOT_BOUND", locale="zh")
            )
    except Exception as e:
        await adapter.handle_error(event, e, locale="zh")
