Here is the English translation of the Minifilter Development Guide.

---

# Minifilter Development Guide

## What is Minifilter?

Minifilter is a data processing system designed to process data returned by the API before rendering. You can use it to:

- Format numerical values (e.g., PP, Ranks).
- Add calculated fields.
- Convert data formats.
- Add custom fields.

## Directory Structure

Each minifilter is an independent package located in the `minifilters/` directory:

```
minifilters/
└── your_minifilter/          # Minifilter directory name
    ├── __init__.py           # Must contain the process() function
    └── minifilter.yaml       # Configuration file
```

## Configuration File (minifilter.yaml)

```yaml
name: your_minifilter        # Minifilter name (unique)
version: 1.0.0              # Version number
description: "Description"  # Description text

hooks:                      # List of renderers to hook
  - user_card
  - score_card

depends:                    # Other minifilters to depend on (executed in order)
  - other_minifilter
```

## Implementation File (\_\_init\_\_.py)

You must define the `process(data: dict) -> dict` function:

```python
def process(data: dict) -> dict:
    """
    Process data
    
    Args:
        data: Raw API data (may have been processed by other minifilters)
    
    Returns:
        The processed data
    """
    # Read raw fields
    statistics = data.get("statistics") or {}
    
    # Add formatted fields
    pp = statistics.get("pp", 0)
    data["pp_formatted"] = f"{int(pp):,}"
    
    # Return processed data
    return data
```

## Complete Examples

### Basic User Card Formatting (user_card_basic)

```python
# minifilters/user_card_basic/__init__.py

def process(data: dict) -> dict:
    """Basic user card formatting"""
    statistics = data.get("statistics") or {}
    
    # PP formatting
    pp = statistics.get("pp", 0)
    data["pp_formatted"] = f"{int(pp):,}"
    
    # Global rank formatting
    global_rank = statistics.get("global_rank", 0)
    data["rank_formatted"] = f"#{int(global_rank):,}" if global_rank else "#-"
    
    # Country rank formatting
    country_rank = statistics.get("country_rank", 0)
    data["country_rank_formatted"] = f"#{int(country_rank):,}" if country_rank else "#-"
    
    # Play time formatting (convert to hours)
    play_time = statistics.get("play_time", 0)
    hours = int(play_time // 3600)
    data["play_time_formatted"] = f"{hours:,}h"
    
    return data
```

```yaml
# minifilters/user_card_basic/minifilter.yaml
name: user_card_basic
version: 1.0.0
description: Basic user card formatting

hooks:
  - user_card

depends: []
```

### Depending on Other Minifilters

```python
# minifilters/user_card_extra/__init__.py

def process(data: dict) -> dict:
    """Extra user card formatting (executed after basic)"""
    statistics = data.get("statistics") or {}
    
    # Accuracy formatting
    accuracy = statistics.get("hit_accuracy", 0)
    data["accuracy_formatted"] = f"{accuracy:.2f}%"
    
    # Max combo
    max_combo = statistics.get("maximum_combo", 0)
    data["max_combo_formatted"] = f"{int(max_combo):,}"
    
    return data
```

```yaml
# minifilters/user_card_extra/minifilter.yaml
name: user_card_extra
version: 1.0.0
description: Extra user card formatting

hooks:
  - user_card

depends:
  - user_card_basic    # Ensure execution after basic
```

## Available Data Fields

All field definitions come from **osu! API v2** (osu-web). Below are common fields:

### User Data (User)

| Field | Type | Description | Example |
|------|------|------|------|
| `id` | int | User ID | 12345678 |
| `username` | str | Username | "peppy" |
| `avatar_url` | str | Avatar URL | "https://..." |
| `country` | object | Country Info | `{"code": "JP", "name": "Japan"}` |
| `country.code` | str | Country Code | "JP" |
| `country.name` | str | Country Name | "Japan" |
| `statistics` | object | Statistics | See table below |

### Statistics (UserStatistics)

| Field | Type | Description |
|------|------|------|
| `pp` | float | Performance Points |
| `global_rank` | int | Global Rank |
| `country_rank` | int | Country Rank |
| `hit_accuracy` | float | Accuracy (%) |
| `play_count` | int | Play Count |
| `play_time` | int | Play Time (seconds) |
| `maximum_combo` | int | Max Combo |
| `total_hits` | int | Total Hits |
| `ranked_score` | int | Ranked Score |
| `total_score` | int | Total Score |

### Beatmap Data (Beatmap)

| Field | Type | Description |
|------|------|------|
| `id` | int | Beatmap ID |
| `beatmapset_id` | int | Beatmapset ID |
| `version` | str | Difficulty Name |
| `difficulty_rating` | float | Star Rating |
| `mode` | str | Game Mode (osu/taiko/catch/mania) |
| `total_length` | int | Total Length (seconds) |
| `hit_length` | int | Hit Length (seconds) |
| `bpm` | float | BPM |
| `cs` | float | Circle Size |
| `drain` | float | HP Drain |
| `accuracy` | float | Overall Difficulty |
| `ar` | float | Approach Rate |

### Score Data (Score)

| Field | Type | Description |
|------|------|------|
| `id` | int | Score ID |
| `user_id` | int | User ID |
| `accuracy` | float | Accuracy |
| `mods` | list | Mods Used |
| `score` | int | Score |
| `max_combo` | int | Max Combo |
| `passed` | bool | Passed State |
| `pp` | float | PP Value |
| `rank` | str | Grade (SS/S/A/B/C/D) |
| `created_at` | str | Score Date |
| `statistics` | object | Detailed Statistics |

## Dependency System

### Execution Order

FltMgr uses topological sorting to automatically calculate the execution order:

```
A (No dependency) → B (Depends on A) → C (Depends on B)
```

### Circular Dependencies

If a circular dependency exists (e.g., A depends on B, and B depends on A), all minifilters for that hook will be disabled.

## Best Practices

1. **Single Responsibility**: Each minifilter should do one thing only.
2. **Naming Convention**: Use the format `hook_name_function`.
3. **Defensive Programming**: Use `.get()` to avoid `KeyError`.
4. **Add New Fields**: Do not modify raw fields; add new formatted fields instead.
5. **Documentation**: Add docstrings in `__init__.py`.

## Debugging Tips

Check the logs to confirm the minifilter loading status:

```
[FltMgr] Loaded: user_card_basic (hooks: ['user_card'], depends: [])
[FltMgr] Execution Chain [user_card]: user_card_basic -> user_card_extra
[FltMgr] Compiled [user_card]: 2 processors
```

## References

- [osu! API v2 Documentation](https://osu.ppy.sh/docs/index.html)
- Check `minifilters/user_card_basic/` and `minifilters/user_card_extra/` in this project as reference implementations.
