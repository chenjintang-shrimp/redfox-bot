# FRONTEND KNOWLEDGE BASE

**Scope:** Discord and QQ bot command layers.

## OVERVIEW
Multi-platform bot frontend. Discord uses discord.py Cogs with hybrid commands; QQ uses NoneBot2 plugins with `on_command` decorators.

## WHERE TO LOOK
| Task | Location | Notes |
|------|----------|-------|
| Add Discord command | discord/cogs/ | `commands.Cog` class + `@commands.hybrid_command()` |
| Add QQ command | qq/plugins/ | `on_command()` decorator + `handle()` async function |
| Discord entry point | discord/main.py | Cog auto-discovery on startup |
| QQ entry point | qq/main.py | `nonebot.load_plugins("frontend/qq/plugins")` |
| Resolve Discord username | discord/util.py | Mentions → bound osu! username |
| Shared adapter base | ../adapters/base.py | `PlatformAdapter` ABC |

## CONVENTIONS
- **Discord**: Use `@commands.hybrid_command()` for both `!` prefix and slash commands
- **QQ**: Commands are registered via `on_command("cmd", priority=5)`; handlers receive `MessageEvent` + `CommandArg`
- Both platforms use `PlatformAdapter` to get `UserContext` and send unified `Message` types
- Error handling: catch in command body → call `adapter.handle_error(ctx_or_event, e, locale="en"/"zh")`

## CODE MAP

| Symbol | Type | File | Role |
|--------|------|------|------|
| BeatmapCog | class | discord/cogs/beatmap.py | `!m` / `!um` beatmap queries |
| ScoresCog | class | discord/cogs/scores.py | Score commands with pagination views |
| UserCog | class | discord/cogs/user.py | User info / bind commands |
| resolve_username | function | discord/util.py | Mention/user arg → bound osu username |
| QQAdapter.handle_error | method | qq_adapter.py | Catches + localizes exceptions for QQ |

## UNIQUE STYLES
- **Discord pagination**: `BasePaginationView` (discord.ui.View) with Previous/Next buttons; `interaction_check` restricts to command author
- **Cog auto-loading**: `frontend/discord/main.py` scans `.py` files, skips `_` prefix (except `__init__.py`)
- **QQ global exception hook**: `frontend/qq/main.py` registers `run_preprocessor` + `run_postprocessor` to log and catch matcher errors
- **Locale split**: Discord defaults to `"en"`; QQ defaults to `"zh"`
