"""QQ help card command catalog.

The catalog is the single source for the overview card, detailed help cards,
and command-name lookup.  Keep entries aligned with ``frontend.qq.plugins``.
"""

from dataclasses import asdict, dataclass


@dataclass(frozen=True, slots=True)
class QQHelpCommand:
    """One documented QQ command."""

    name: str
    usage: str
    summary: str
    detail: str
    category: str
    aliases: tuple[str, ...] = ()

    def to_template_data(self) -> dict:
        """Return renderer-safe command data."""
        return asdict(self)


QQ_HELP_COMMANDS: tuple[QQHelpCommand, ...] = (
    QQHelpCommand(
        name="help",
        usage="help [命令]",
        summary="查看命令总览或某条命令的详细用法。",
        detail="不带参数时显示全部命令；传入命令名或别名时显示对应说明。",
        category="帮助",
    ),
    QQHelpCommand(
        name="cacheclear",
        usage="cacheclear",
        summary="清理当前 bot 进程的内存缓存。",
        detail="会清除谱面数据和 OAuth token 等内存缓存；后续请求会按需重新获取数据。",
        category="系统",
    ),
    QQHelpCommand(
        name="info",
        usage="info [用户名] [模式]",
        summary="以卡片查看玩家资料。",
        detail="不填模式时使用当前发送者保存的 GM；指定模式时覆盖查询模式，并在卡片底部与 GM 对比。",
        category="用户",
    ),
    QQHelpCommand(
        name="i",
        usage="i [用户名]",
        summary="以文字查看玩家资料。",
        detail="不填用户名时查询已绑定玩家。",
        category="用户",
    ),
    QQHelpCommand(
        name="bind",
        usage="bind <用户名>",
        summary="绑定你的 osu! 账号。",
        detail="绑定后，大部分成绩与资料命令可省略用户名。",
        category="用户",
    ),
    QQHelpCommand(
        name="unbind",
        usage="unbind",
        summary="解除当前 QQ 账号的 osu! 绑定。",
        detail="解除绑定后，需在查询命令中显式提供用户名。",
        category="用户",
    ),
    QQHelpCommand(
        name="set_gamemode",
        usage="set_gamemode [模式]",
        summary="查看或设置成绩查询使用的默认游戏模式。",
        detail="模式可使用 ID、短名或全名；不带参数时显示当前设置。",
        category="用户",
        aliases=("gm",),
    ),
    QQHelpCommand(
        name="m",
        usage="m <谱面 ID>",
        summary="查看谱面文字信息。",
        detail="谱面 ID 必须是数字。",
        category="谱面",
    ),
    QQHelpCommand(
        name="ss",
        usage="ss <谱面 ID>",
        summary="查看已绑定玩家在指定谱面的成绩卡片。",
        detail="谱面 ID 必须是数字，且该命令需要先绑定账号。",
        category="谱面",
    ),
    QQHelpCommand(
        name="ps",
        usage="ps [用户名]",
        summary="查看最近通过成绩列表。",
        detail="不填用户名时查询已绑定玩家，使用发送者保存的 GM 模式。",
        category="成绩",
    ),
    QQHelpCommand(
        name="rs",
        usage="rs [用户名]",
        summary="查看最近成绩列表，包含失败成绩。",
        detail="不填用户名时查询已绑定玩家，使用发送者保存的 GM 模式。",
        category="成绩",
    ),
    QQHelpCommand(
        name="t",
        usage="t [用户名]",
        summary="查看今日 BP 成绩。",
        detail="不填用户名时查询已绑定玩家，使用发送者保存的 GM 模式。",
        category="成绩",
    ),
    QQHelpCommand(
        name="p",
        usage="p [用户名]",
        summary="查看最新通过成绩卡片。",
        detail="不填用户名时查询已绑定玩家，使用发送者保存的 GM 模式。",
        category="成绩",
    ),
    QQHelpCommand(
        name="r",
        usage="r [用户名]",
        summary="查看最新成绩卡片，包含失败成绩。",
        detail="不填用户名时查询已绑定玩家，使用发送者保存的 GM 模式。",
        category="成绩",
    ),
    QQHelpCommand(
        name="b",
        usage="b [用户名]",
        summary="查看最佳成绩卡片。",
        detail="不填用户名时查询已绑定玩家，使用发送者保存的 GM 模式。",
        category="成绩",
    ),
    QQHelpCommand(
        name="bs",
        usage="bs [数量] [用户名]",
        summary="查看最佳成绩列表。",
        detail="数量默认为 20、最大为 100；不填用户名时查询已绑定玩家。",
        category="成绩",
    ),
)


def get_help_command(name: str) -> QQHelpCommand | None:
    """Resolve a primary command name or alias, case-insensitively."""
    normalized = name.strip().lower()
    for command in QQ_HELP_COMMANDS:
        if normalized == command.name or normalized in command.aliases:
            return command
    return None


def all_help_command_data() -> list[dict]:
    """Return all catalog entries as renderer input."""
    return [command.to_template_data() for command in QQ_HELP_COMMANDS]
