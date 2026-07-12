from nonebot import on_command
from nonebot.adapters.onebot.v11 import MessageEvent
from nonebot.params import CommandArg

from adapters.qq_adapter import QQAdapter
from frontend.qq.help_catalog import all_help_command_data, get_help_command
from renderer.help import render_help_card_image
from utils.strings import format_template

help_cmd = on_command("help", priority=5)

adapter = QQAdapter()


@help_cmd.handle()
async def handle_help(event: MessageEvent, args=CommandArg()) -> None:
    """Render QQ command overview or a detailed command help card."""
    command_name = args.extract_plain_text().strip()

    if not command_name:
        data = {"view": "overview", "commands": all_help_command_data()}
    else:
        command = get_help_command(command_name)
        if command is None:
            await help_cmd.send(
                format_template("HELP_COMMAND_NOT_FOUND", locale="zh", command=command_name)
            )
            return
        data = {"view": "detail", "command": command.to_template_data()}

    try:
        image = await render_help_card_image(data)
        await adapter.send_image_bytes(event, image)
    except Exception as error:
        await adapter.handle_error(event, error, locale="zh")
