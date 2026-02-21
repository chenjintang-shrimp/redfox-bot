# Details

Date : 2026-02-21 16:35:06

Directory d:\\guosu\\g0v0bot-discord

Total : 77 files,  28983 codes, 259 comments, 1975 blanks, all 31217 lines

[Summary](results.md) / Details / [Diff Summary](diff.md) / [Diff Details](diff-details.md)

## Files
| filename | language | code | comment | blank | total |
| :--- | :--- | ---: | ---: | ---: | ---: |
| [.trae/specs/refactor-plugin-system/checklist.md](/.trae/specs/refactor-plugin-system/checklist.md) | Markdown | 85 | 0 | 19 | 104 |
| [.trae/specs/refactor-plugin-system/spec.md](/.trae/specs/refactor-plugin-system/spec.md) | Markdown | 125 | 0 | 53 | 178 |
| [.trae/specs/refactor-plugin-system/tasks.md](/.trae/specs/refactor-plugin-system/tasks.md) | Markdown | 81 | 0 | 27 | 108 |
| [README.md](/README.md) | Markdown | 111 | 0 | 47 | 158 |
| [adapters/__init__.py](/adapters/__init__.py) | Python | 4 | 0 | 3 | 7 |
| [adapters/base.py](/adapters/base.py) | Python | 88 | 6 | 27 | 121 |
| [adapters/discord_adapter.py](/adapters/discord_adapter.py) | Python | 134 | 2 | 29 | 165 |
| [adapters/message_types.py](/adapters/message_types.py) | Python | 35 | 1 | 17 | 53 |
| [adapters/qq_adapter.py](/adapters/qq_adapter.py) | Python | 110 | 4 | 36 | 150 |
| [backend/__init__.py](/backend/__init__.py) | Python | 0 | 0 | 1 | 1 |
| [backend/api_client.py](/backend/api_client.py) | Python | 266 | 6 | 56 | 328 |
| [backend/beatmap.py](/backend/beatmap.py) | Python | 32 | 3 | 13 | 48 |
| [backend/database.py](/backend/database.py) | Python | 79 | 3 | 34 | 116 |
| [backend/exceptions/__init__.py](/backend/exceptions/__init__.py) | Python | 12 | 0 | 2 | 14 |
| [backend/exceptions/beatmap.py](/backend/exceptions/beatmap.py) | Python | 6 | 0 | 3 | 9 |
| [backend/exceptions/renderer.py](/backend/exceptions/renderer.py) | Python | 6 | 0 | 2 | 8 |
| [backend/exceptions/scores.py](/backend/exceptions/scores.py) | Python | 7 | 0 | 3 | 10 |
| [backend/exceptions/user.py](/backend/exceptions/user.py) | Python | 18 | 0 | 11 | 29 |
| [backend/scores.py](/backend/scores.py) | Python | 142 | 3 | 37 | 182 |
| [backend/user.py](/backend/user.py) | Python | 118 | 2 | 32 | 152 |
| [config/api.yaml](/config/api.yaml) | YAML | 10 | 1 | 2 | 13 |
| [config/config.example.yaml](/config/config.example.yaml) | YAML | 17 | 14 | 10 | 41 |
| [config/strings.yaml](/config/strings.yaml) | YAML | 215 | 39 | 45 | 299 |
| [docs/minifilter_guide.md](/docs/minifilter_guide.md) | Markdown | 178 | 0 | 62 | 240 |
| [docs/minifilter_guide_en.md](/docs/minifilter_guide_en.md) | Markdown | 180 | 0 | 64 | 244 |
| [docs/skin_guide.md](/docs/skin_guide.md) | Markdown | 342 | 0 | 83 | 425 |
| [docs/skin_guide_en.md](/docs/skin_guide_en.md) | Markdown | 311 | 0 | 73 | 384 |
| [frontend/__init__.py](/frontend/__init__.py) | Python | 0 | 0 | 1 | 1 |
| [frontend/discord/__init__.py](/frontend/discord/__init__.py) | Python | 0 | 0 | 1 | 1 |
| [frontend/discord/cogs/beatmap.py](/frontend/discord/cogs/beatmap.py) | Python | 45 | 0 | 11 | 56 |
| [frontend/discord/cogs/scores.py](/frontend/discord/cogs/scores.py) | Python | 426 | 2 | 74 | 502 |
| [frontend/discord/cogs/user.py](/frontend/discord/cogs/user.py) | Python | 104 | 2 | 19 | 125 |
| [frontend/discord/main.py](/frontend/discord/main.py) | Python | 74 | 11 | 42 | 127 |
| [frontend/discord/util.py](/frontend/discord/util.py) | Python | 24 | 0 | 5 | 29 |
| [frontend/qq/__init__.py](/frontend/qq/__init__.py) | Python | 0 | 0 | 1 | 1 |
| [frontend/qq/main.py](/frontend/qq/main.py) | Python | 99 | 7 | 30 | 136 |
| [frontend/qq/plugins/__init__.py](/frontend/qq/plugins/__init__.py) | Python | 0 | 0 | 1 | 1 |
| [frontend/qq/plugins/beatmap.py](/frontend/qq/plugins/beatmap.py) | Python | 26 | 0 | 10 | 36 |
| [frontend/qq/plugins/scores.py](/frontend/qq/plugins/scores.py) | Python | 179 | 3 | 44 | 226 |
| [frontend/qq/plugins/user.py](/frontend/qq/plugins/user.py) | Python | 107 | 2 | 26 | 135 |
| [minifilters/__init__.py](/minifilters/__init__.py) | Python | 4 | 0 | 2 | 6 |
| [minifilters/score_card_basic/__init__.py](/minifilters/score_card_basic/__init__.py) | Python | 61 | 4 | 19 | 84 |
| [minifilters/score_card_basic/minifilter.yaml](/minifilters/score_card_basic/minifilter.yaml) | YAML | 7 | 0 | 3 | 10 |
| [minifilters/score_list_basic/__init__.py](/minifilters/score_list_basic/__init__.py) | Python | 57 | 4 | 22 | 83 |
| [minifilters/score_list_basic/minifilter.yaml](/minifilters/score_list_basic/minifilter.yaml) | YAML | 6 | 0 | 3 | 9 |
| [minifilters/today_bp_basic/__init__.py](/minifilters/today_bp_basic/__init__.py) | Python | 55 | 3 | 21 | 79 |
| [minifilters/today_bp_basic/minifilter.yaml](/minifilters/today_bp_basic/minifilter.yaml) | YAML | 6 | 0 | 3 | 9 |
| [models/__init__.py](/models/__init__.py) | Python | 1 | 0 | 1 | 2 |
| [models/context.py](/models/context.py) | Python | 25 | 0 | 8 | 33 |
| [openapi.json](/openapi.json) | JSON | 20,260 | 0 | 0 | 20,260 |
| [pyproject.toml](/pyproject.toml) | TOML | 37 | 2 | 6 | 45 |
| [renderer/__init__.py](/renderer/__init__.py) | Python | 19 | 0 | 7 | 26 |
| [renderer/beatmap.py](/renderer/beatmap.py) | Python | 70 | 3 | 18 | 91 |
| [renderer/renderer_template.py](/renderer/renderer_template.py) | Python | 75 | 12 | 25 | 112 |
| [renderer/scores.py](/renderer/scores.py) | Python | 671 | 57 | 172 | 900 |
| [renderer/skin_loader.py](/renderer/skin_loader.py) | Python | 98 | 4 | 34 | 136 |
| [renderer/user.py](/renderer/user.py) | Python | 88 | 5 | 31 | 124 |
| [services/__init__.py](/services/__init__.py) | Python | 5 | 0 | 3 | 8 |
| [services/beatmap_service.py](/services/beatmap_service.py) | Python | 99 | 1 | 22 | 122 |
| [services/score_service.py](/services/score_service.py) | Python | 202 | 3 | 42 | 247 |
| [services/user_service.py](/services/user_service.py) | Python | 137 | 0 | 38 | 175 |
| [skins/default/beatmap_card.html](/skins/default/beatmap_card.html) | Polymer | 373 | 6 | 33 | 412 |
| [skins/default/score_card.html](/skins/default/score_card.html) | Polymer | 397 | 8 | 32 | 437 |
| [skins/default/score_list.html](/skins/default/score_list.html) | Polymer | 286 | 0 | 32 | 318 |
| [skins/default/skin.yaml](/skins/default/skin.yaml) | YAML | 11 | 0 | 2 | 13 |
| [skins/default/today_bp.html](/skins/default/today_bp.html) | Polymer | 287 | 0 | 33 | 320 |
| [skins/default/user_card.html](/skins/default/user_card.html) | Polymer | 95 | 0 | 11 | 106 |
| [utils/__init__.py](/utils/__init__.py) | Python | 0 | 0 | 1 | 1 |
| [utils/caches.py](/utils/caches.py) | Python | 18 | 0 | 12 | 30 |
| [utils/flt_mgr.py](/utils/flt_mgr.py) | Python | 244 | 15 | 71 | 330 |
| [utils/html2image.py](/utils/html2image.py) | Python | 67 | 4 | 25 | 96 |
| [utils/logger.py](/utils/logger.py) | Python | 47 | 3 | 14 | 64 |
| [utils/scheduler.py](/utils/scheduler.py) | Python | 140 | 1 | 45 | 186 |
| [utils/scheduler_registry.py](/utils/scheduler_registry.py) | Python | 67 | 2 | 27 | 96 |
| [utils/strings.py](/utils/strings.py) | Python | 39 | 4 | 15 | 58 |
| [utils/variable.py](/utils/variable.py) | Python | 41 | 7 | 18 | 66 |
| [uv.lock](/uv.lock) | TOML | 1,092 | 0 | 68 | 1,160 |

[Summary](results.md) / Details / [Diff Summary](diff.md) / [Diff Details](diff-details.md)