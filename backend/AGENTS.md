# BACKEND KNOWLEDGE BASE

**Scope:** API client, database, exception hierarchy, and core business data functions.

## OVERVIEW
Backend API layer for osu! private server integration. Handles OAuth2 authentication, HTTP client lifecycle, SQLModel database, and domain-specific data queries.

## WHERE TO LOOK
| Task | Location | Notes |
|------|----------|-------|
| API client / OAuth2 | api_client.py | OAuth2Handler with aiocache + asyncio.Lock |
| Database models / ORM | database.py | SQLModel + aiosqlite |
| Add exception type | exceptions/{domain}.py | Inherit Exception, set `template_key` |
| User queries | user.py | `get_user_info`, `get_user_beatmap_scores` |
| Score queries | scores.py | Paginated score fetching with fallback username |
| Beatmap queries | beatmap.py | `get_beatmap_info` |
| Exception exports | exceptions/__init__.py | Add to `__all__` |

## CONVENTIONS
- All backend functions are `async`; I/O is always awaited
- `OAuth2Handler` refreshes tokens 30s before expiry; uses `asyncio.Lock` to prevent duplicate refreshes
- Custom exceptions MUST define `template_key` for automatic localization
- API URLs are templated in `config/api.yaml` and resolved via `utils.strings.get_api_url()`
- `get_osu_api_client()` returns a singleton `httpx.AsyncClient`

## CODE MAP

| Symbol | Type | File | Role |
|--------|------|------|------|
| OAuth2Handler | class | api_client.py | Token refresh with aiocache + asyncio.Lock |
| get_osu_api_client | function | api_client.py | Singleton httpx.AsyncClient |
| close_osu_api_client | function | api_client.py | Cleanup on shutdown |
| create_db_and_tables | function | database.py | SQLModel engine init |
| get_user_binding | function | database.py | Query platform→osu binding |

## ANTI-PATTERNS
- **Bare except for username fallback**: `scores.py` and `beatmap.py` use `except Exception:` to gracefully fall back to `str(user_id)` when user info lookup fails
- **No transaction retries**: Database writes do not retry on `sqlite3.OperationalError`
