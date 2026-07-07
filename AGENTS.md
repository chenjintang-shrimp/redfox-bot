# PROJECT KNOWLEDGE BASE

**Generated:** 2026-05-31
**Commit:** 69a7284
**Branch:** develop

## OVERVIEW
A highly-customized Python 3.14+ Discord/QQ bot for osu! private servers. Multi-platform (Discord via discord.py, QQ via nonebot2), unified backend API layer with OAuth2, skin-based HTML-to-image rendering.

## STRUCTURE
```
g0v0bot-discord/
├── adapters/          # Platform abstraction layer (Discord/QQ)
├── backend/           # Core business logic: API client, database, exceptions
├── config/            # YAML configs: bot, OAuth, API URLs, i18n strings
├── docs/              # Skin/minifilter guides
├── frontend/
│   ├── discord/       # discord.py Cogs + hybrid commands
│   └── qq/            # NoneBot2 plugins (on_command decorators)
├── minifilters/       # Data transformation plugins (score_card_basic, etc.)
├── models/            # UserContext dataclass
├── renderer/          # Skin system: Jinja2 HTML templates → Playwright screenshots
├── services/          # Business logic services (User, Score, Beatmap)
├── skins/             # HTML/CSS/Jinja2 skin templates
└── utils/             # Shared: cache, logger, scheduler, strings
```

## WHERE TO LOOK
| Task | Location | Notes |
|------|----------|-------|
| Add Discord command | frontend/discord/cogs/ | Cog class + setup() |
| Add QQ command | frontend/qq/plugins/ | on_command + handle() |
| Modify API client | backend/api_client.py | OAuth2Handler, httpx AsyncClient |
| Add database model | backend/database.py | SQLModel |
| Add exception type | backend/exceptions/ | Inherit from base, set template_key |
| Add skin/template | skins/{name}/ | skin.yaml + {renderer_name}.html |
| Add minifilter | minifilters/{name}/ | process(data) async function |
| i18n strings | config/strings.yaml | Key per locale (en/zh) |
| API endpoint URL | config/api.yaml | URL template with placeholders |
| Scheduled task | Any backend module | @scheduled_task(name, interval) |

## CODE MAP

| Symbol | Type | Location | Role |
|--------|------|----------|------|
| OAuth2Handler | class | backend/api_client.py | Token refresh with aiocache + asyncio.Lock |
| PlatformAdapter | ABC | adapters/base.py | Unified user context + message send |
| DiscordAdapter | class | adapters/discord_adapter.py | Discord-specific ctx → UserContext |
| QQAdapter | class | adapters/qq_adapter.py | QQ-specific MessageEvent → UserContext |
| UserContext | dataclass | models/context.py | Cross-layer user binding info |
| UserService | class | services/user_service.py | Resolve username, get user info |
| ScoreService | class | services/score_service.py | Score-related business logic |
| BeatmapService | class | services/beatmap_service.py | Beatmap-related business logic |
| renderer | decorator | renderer/renderer_template.py | Auto-catch + exception→localized msg |
| scheduled_task | decorator | utils/scheduler_registry.py | Auto-discovered scheduled tasks |
| auto_discover_tasks | function | utils/scheduler_registry.py | Import-based task discovery |
| get_osu_api_client | function | backend/api_client.py | Singleton httpx client |
| close_osu_api_client | function | backend/api_client.py | Cleanup on shutdown |

## CONVENTIONS
- **Type annotations**: Required everywhere; ty type-checks the project
- **Async/await**: All I/O operations are async; backend functions are async
- **Localization**: Error messages use `template_key` on exceptions + `format_template()` from config/strings.yaml
- **Logging**: `get_logger("module.name")` via loguru; never use print() in production code
- **Database**: SQLModel with aiosqlite; models in backend/database.py
- **Package layout**: Top-level packages (frontend, backend, utils, etc.) declared in `[tool.setuptools] packages`

## ANTI-PATTERNS (THIS PROJECT)
- **No tests**: The project has zero test files, test configs, or testing infrastructure
- **No CI/CD**: No .github/workflows, Makefile, Dockerfile, or pre-commit hooks
- **Bare except**: `except Exception:` is used in some places for graceful degradation (e.g., username fallback)
- **Type ignores**: use `# type: ignore` sparingly, only when ty cannot express a real runtime pattern

## UNIQUE STYLES
- **Hybrid commands**: Discord uses `commands.hybrid_command()` for both prefix `!` and slash commands
- **Auto-discovery**: Cogs auto-loaded from frontend/discord/cogs/; tasks auto-discovered via `@scheduled_task` + `auto_discover_tasks()`
- **Skin fallback chain**: skin.yaml mapping → {name}.html → default skin → RENDERER_ERROR_TEMPLATE
- **Minifilter pipeline**: Renderer calls `flt_mgr.process()` to chain data transformers before template rendering
- **Exception template keys**: All custom exceptions define `template_key` for automatic localized error messages

## COMMANDS
```bash
# Install dependencies
uv sync

# Run Discord bot
uv run discord-bot

# Run QQ bot
uv run qq-bot

# Type check
uv run ty check

# Lint (default ruff rules, no config)
uv run ruff check .
```

## NOTES
- Bot token and secrets live in `config/config.yaml` (copied from config.example.yaml)
- `.env` and `.env.qq` are legacy; migration notice in `.env.example`
- Playwright browser initialized on startup, closed on disconnect
- aiocache used for OAuth token storage and other caching
- frontend/discord/main.py loads Cogs by scanning .py files; skips files starting with _
