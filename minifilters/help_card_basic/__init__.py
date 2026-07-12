"""Prepare QQ help catalog data for the shared help-card template."""

from collections import defaultdict

HOOKS: list[str] = ["help_card"]

_CATEGORY_ORDER: tuple[str, ...] = ("帮助", "系统", "用户", "谱面", "成绩")


def _prepare_command(command: dict) -> dict:
    """Make a catalog entry safe and convenient for the Jinja template."""
    result = dict(command)
    aliases = result.get("aliases", ())
    result["command_names"] = " / ".join((result.get("name", ""), *aliases))
    result["aliases_text"] = "、".join(aliases)
    return result


def process(data: dict) -> dict:
    """Build grouped overview or detailed command data from raw catalog entries."""
    if not isinstance(data, dict):
        return data

    result = dict(data)
    view = result.get("view")
    if view == "detail":
        command = result.get("command", {})
        result["command"] = _prepare_command(command) if isinstance(command, dict) else {}
        return result

    grouped: dict[str, list[dict]] = defaultdict(list)
    commands = result.get("commands", [])
    if isinstance(commands, list):
        for command in commands:
            if isinstance(command, dict):
                prepared = _prepare_command(command)
                grouped[prepared.get("category", "其他")].append(prepared)

    result["groups"] = [
        {"name": category, "commands": grouped[category]}
        for category in _CATEGORY_ORDER
        if grouped[category]
    ]
    return result
