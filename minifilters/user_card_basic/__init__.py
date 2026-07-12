"""Normalize game-mode data for the user card."""

from backend.rulesets import get_ruleset, normalize_gamemode

HOOKS: list[str] = ["user_card"]

_CAPABILITIES: tuple[tuple[str, str], ...] = (
    ("scores", "Scores"),
    ("ranking", "Ranking"),
    ("ppCalculation", "PP Calc"),
)


def _rank_history_chart(history: object) -> dict | None:
    """Convert API rank history into compact SVG polyline coordinates."""
    if not isinstance(history, list):
        return None

    values = [
        value
        for value in history
        if isinstance(value, int) and not isinstance(value, bool) and value > 0
    ]
    if len(values) < 2:
        return None

    point_count = min(len(values), 48)
    sampled = [
        values[round(index * (len(values) - 1) / (point_count - 1))]
        for index in range(point_count)
    ]
    minimum = min(sampled)
    maximum = max(sampled)
    span = max(maximum - minimum, 1)
    width = 300
    height = 54
    padding = 4
    points = " ".join(
        f"{padding + index * (width - padding * 2) / (point_count - 1):.1f},"
        f"{padding + (rank - minimum) * (height - padding * 2) / span:.1f}"
        for index, rank in enumerate(sampled)
    )

    return {
        "points": points,
        "sample_count": len(values),
        "start_rank": values[0],
        "end_rank": values[-1],
    }


def _mode_display(source: str, raw_mode: object) -> dict:
    """Return card-ready mode metadata while preserving unknown API values."""
    raw_text = str(raw_mode).strip()
    normalized = normalize_gamemode(raw_text)
    ruleset = get_ruleset(short_name=normalized) if normalized else None
    supported = set(ruleset.capabilities) if ruleset else set()

    return {
        "source": source,
        "full_name": ruleset.full_name if ruleset else raw_text,
        "capabilities": [
            {"name": label, "supported": capability in supported}
            for capability, label in _CAPABILITIES
        ],
    }


def _format_statistics(statistics: object) -> dict[str, str]:
    """Produce stable display strings when a ruleset has no ranking data."""
    stats = statistics if isinstance(statistics, dict) else {}

    def number(value: object, digits: int = 0) -> str:
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            return "-"
        return f"{value:.{digits}f}"

    global_rank = number(stats.get("global_rank"))
    country_rank = number(stats.get("country_rank"))
    return {
        "pp": number(stats.get("pp")),
        "global_rank": f"#{global_rank}" if global_rank != "-" else "-",
        "country_rank": f"#{country_rank}" if country_rank != "-" else "-",
        "accuracy": (
            f"{number(stats.get('hit_accuracy'), 2)}%"
            if number(stats.get("hit_accuracy"), 2) != "-"
            else "-"
        ),
    }


def process(data: dict) -> dict:
    """Add API and saved-GM mode displays without altering source values."""
    if not isinstance(data, dict):
        return data

    result = dict(data)
    result["statistics"] = result.get("statistics") or {}
    result["statistics_display"] = _format_statistics(result["statistics"])
    query_gamemode = result.get("query_gamemode") or result.get("playmode", "osu")
    result["mode_displays"] = [_mode_display("QUERY", query_gamemode)]

    saved_gamemode = result.get("saved_gamemode")
    if result.get("compare_saved_gamemode") and saved_gamemode:
        result["mode_displays"].append(_mode_display("GM", saved_gamemode))

    result["rank_history_chart"] = _rank_history_chart(result.get("rank_history"))

    return result
