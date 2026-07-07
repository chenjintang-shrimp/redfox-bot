# RENDERER KNOWLEDGE BASE

**Scope:** Skin system, HTML template rendering, and image generation.

## OVERVIEW
Skin-based rendering engine. Jinja2 HTML templates are loaded from `skins/` and converted to PNG images via Playwright.

## WHERE TO LOOK
| Task | Location | Notes |
|------|----------|-------|
| Add a renderer | scores.py / beatmap.py / user.py | Decorate with `@renderer("view_name")` |
| Skin configuration | skin_loader.py | `find_template()` with fallback chain |
| Exception handling | renderer_template.py | `@renderer` decorator auto-catches + localizes |
| Add a skin | ../skins/{name}/ | `skin.yaml` + `{renderer_name}.html` |
| Add a minifilter | ../minifilters/{name}/ | `process(data)` async function |
| HTML-to-image | ../utils/html2image.py | Playwright screenshot utility |

## CONVENTIONS
- Use `@renderer("view_name")` or `@renderer` (auto-infers from function name)
- Renderer functions receive processed data dict and return `str` (HTML) or `bytes` (image)
- The decorator catches exceptions and returns a localized error message string
- `flt_mgr.process(data)` chains all registered minifilters before template rendering

## CODE MAP

| Symbol | Type | File | Role |
|--------|------|------|------|
| renderer | decorator | renderer_template.py | Auto-catch + localize exceptions |
| find_template | function | skin_loader.py | Skin fallback chain resolver |
| render_beatmap_card_image | function | beatmap.py | Beatmap data → PNG bytes |
| render_user_score_list_image | function | scores.py | Score list → PNG bytes |
| render_user_beatmap_score_card | function | scores.py | Single score → PNG bytes |
| init_flt_mgr | function | ../utils/flt_mgr.py | Register all minifilters |

## UNIQUE STYLES
- **Skin fallback chain**: `skin.yaml` template mapping → `{renderer_name}.html` → `default` skin → `RENDERER_ERROR_TEMPLATE`
- **Minifilter pipeline**: Data transformers (e.g., `score_card_basic`) enrich/format raw API data before it reaches Jinja2
- **Template caching**: `skin_loader._skin_configs` caches `skin.yaml` per skin name
- **Renderer dual output**: Some renderers return `str` (HTML for Discord embeds); others return `bytes` (PNG for QQ / Discord file)
