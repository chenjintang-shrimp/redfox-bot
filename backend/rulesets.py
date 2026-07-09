"""osu! 游戏模式 (ruleset) 注册表

集中维护所有官方与自定义游戏模式的元数据，提供 id / shortName / fullName
之间的归一化与查找。前端命令通过 ``normalize_gamemode`` 将用户输入统一为
API 所需的 shortName 字符串。
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass(frozen=True, slots=True)
class Ruleset:
    """单个游戏模式的元数据"""

    id: int
    short_name: str
    full_name: str
    category: str
    capabilities: list[str] = field(default_factory=list)


_BUILTINS: list[Ruleset] = [
    Ruleset(0, "osu", "osu!", "standard", ["scores", "ranking", "ppCalculation"]),
    Ruleset(1, "taiko", "osu!taiko", "standard", ["scores", "ranking", "ppCalculation"]),
    Ruleset(2, "fruits", "osu!catch", "standard", ["scores", "ranking", "ppCalculation"]),
    Ruleset(3, "mania", "osu!mania", "standard", ["scores", "ranking", "ppCalculation"]),
    Ruleset(4, "osurx", "osu! Relax", "relax", ["scores", "ppCalculation"]),
    Ruleset(5, "osuap", "osu! Autopilot", "autopilot", ["scores", "ppCalculation"]),
    Ruleset(6, "taikorx", "osu!taiko Relax", "relax", ["scores", "ppCalculation"]),
    Ruleset(7, "fruitsrx", "osu!catch Relax", "relax", ["scores", "ppCalculation"]),
    Ruleset(10, "sentakki", "Sentakki", "custom", ["scores", "ranking"]),
    Ruleset(11, "tau", "Tau", "custom", ["scores", "ranking", "ppCalculation"]),
    Ruleset(12, "rush", "Rush!", "custom", ["scores", "ranking"]),
    Ruleset(13, "hishigata", "Hishigata", "custom", ["scores", "ranking"]),
    Ruleset(14, "soyokaze", "soyokaze!", "custom", ["scores", "ranking", "ppCalculation"]),
]


_BY_ID: dict[int, Ruleset] = {r.id: r for r in _BUILTINS}
_BY_SHORT: dict[str, Ruleset] = {r.short_name: r for r in _BUILTINS}
_BY_FULL_LOWER: dict[str, Ruleset] = {r.full_name.lower(): r for r in _BUILTINS}


def all_rulesets() -> list[Ruleset]:
    """返回全部已注册游戏模式"""
    return list(_BUILTINS)


def get_ruleset(
    *, id: Optional[int] = None, short_name: Optional[str] = None
) -> Optional[Ruleset]:
    """按 id 或 shortName 查找游戏模式"""
    if id is not None:
        return _BY_ID.get(id)
    if short_name is not None:
        return _BY_SHORT.get(short_name)
    return None


def normalize_gamemode(raw: str) -> Optional[str]:
    """将用户输入归一化为 API 所需的 shortName

    接受 id（数字字符串）、shortName、fullName（大小写不敏感）。
    无法识别时返回 None。
    """
    text = raw.strip()
    if not text:
        return None

    # 纯数字 → id
    if text.lstrip("-").isdigit():
        rs = _BY_ID.get(int(text))
        return rs.short_name if rs else None

    # shortName / fullName 大小写不敏感
    lower = text.lower()
    if lower in _BY_SHORT:
        return _BY_SHORT[lower].short_name

    if lower in _BY_FULL_LOWER:
        return _BY_FULL_LOWER[lower].short_name

    return None


def list_short_names() -> list[str]:
    """返回全部 shortName，用于帮助提示"""
    return [r.short_name for r in _BUILTINS]
