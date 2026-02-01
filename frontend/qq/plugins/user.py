from nonebot import on_command
from nonebot.adapters.onebot.v11 import MessageEvent, MessageSegment
from nonebot.params import CommandArg

from backend.user_qq import bind_user_qq, get_user_info, unbind_user_qq
from backend.expections.user import BindExistError, UserNotBindError, UserQueryError
from frontend.qq.util import resolve_username_qq
from renderer.user import render_user_card_image, render_user_info
from utils.logger import get_logger

logger = get_logger("qq.plugins.user")

info_cmd = on_command("info", aliases={"i"}, priority=5)
bind_cmd = on_command("bind", priority=5)
unbind_cmd = on_command("unbind", priority=5)
card_cmd = on_command("info", aliases={"i"}, priority=5)


@info_cmd.handle()
async def handle_info(event: MessageEvent, args=CommandArg()):
    qq_id = event.user_id
    username_arg = args.extract_plain_text().strip()

    try:
        username = await resolve_username_qq(qq_id, username_arg if username_arg else None)
    except UserNotBindError:
        await info_cmd.finish("请先使用 !bind <osu用户名> 绑定账号，或指定用户名查询")
        return

    try:
        msg = await render_user_info(username)
        await info_cmd.finish(msg)
    except UserQueryError as e:
        await info_cmd.finish(f"查询失败: {e.error_msg}")
    except Exception as e:
        logger.error(f"查询用户信息失败: {e}")
        await info_cmd.finish("查询失败，请稍后重试")


@card_cmd.handle()
async def handle_card(event: MessageEvent, args=CommandArg()):
    qq_id = event.user_id
    username_arg = args.extract_plain_text().strip()

    try:
        username = await resolve_username_qq(qq_id, username_arg if username_arg else None)
    except UserNotBindError:
        await card_cmd.finish("请先使用 !bind <osu用户名> 绑定账号，或指定用户名查询")
        return

    try:
        user_data = await get_user_info(username)
        image = await render_user_card_image(user_data)
        await card_cmd.finish(MessageSegment.image(image))
    except UserQueryError as e:
        await card_cmd.finish(f"查询失败: {e.error_msg}")
    except Exception as e:
        logger.error(f"生成用户卡片失败: {e}")
        await card_cmd.finish("生成卡片失败，请稍后重试")


@bind_cmd.handle()
async def handle_bind(event: MessageEvent, args=CommandArg()):
    qq_id = event.user_id
    username = args.extract_plain_text().strip()

    if not username:
        await bind_cmd.finish("请提供 osu! 用户名，格式: !bind <用户名>")
        return

    try:
        await bind_user_qq(qq_id, username)
        await bind_cmd.finish(f"成功绑定 osu! 用户: {username}")
    except BindExistError:
        await bind_cmd.finish("你已经绑定过 osu! 账号了，请先解绑")
    except UserQueryError:
        await bind_cmd.finish(f"找不到用户: {username}")
    except Exception as e:
        logger.error(f"绑定用户失败: {e}")
        await bind_cmd.finish("绑定失败，请稍后重试")


@unbind_cmd.handle()
async def handle_unbind(event: MessageEvent):
    qq_id = event.user_id

    try:
        deleted = await unbind_user_qq(qq_id)
        if deleted:
            await unbind_cmd.finish("解绑成功")
        else:
            await unbind_cmd.finish("你还没有绑定 osu! 账号")
    except Exception as e:
        logger.error(f"解绑用户失败: {e}")
        await unbind_cmd.finish("解绑失败，请稍后重试")
