# 插件系统重构检查清单

## 核心抽象层检查

- [ ] `models/context.py` 已创建并包含 `UserContext` 数据类
- [ ] `UserContext` 包含所有必要字段: platform (str), platform_user_id, osu_username, osu_user_id, current_gamemode
- [ ] `UserContext` 包含 `is_bound` 属性
- [ ] `adapters/base.py` 已创建并包含 `PlatformAdapter` 抽象基类
- [ ] `PlatformAdapter` 定义了 `get_user_context()` 抽象方法
- [ ] `PlatformAdapter` 定义了 `send()` 抽象方法
- [ ] `adapters/message_types.py` 已创建并定义统一消息类型
- [ ] 包含 `TextMessage` 类型
- [ ] 包含 `ImageMessage` 类型
- [ ] 包含 `EmbedMessage` 类型 (Discord 特有，QQ 可忽略)
- [ ] `backend/database.py` 已更新支持通过 `(platform, user_id)` 查询

## Discord 适配器检查

- [ ] `adapters/discord_adapter.py` 已创建
- [ ] `DiscordAdapter` 继承自 `PlatformAdapter`
- [ ] `get_user_context(ctx)` 正确返回 `UserContext`
- [ ] `send(ctx, message)` 正确处理 `TextMessage`
- [ ] `send(ctx, message)` 正确处理 `ImageMessage` (使用 `discord.File`)
- [ ] `send(ctx, message)` 正确处理 `EmbedMessage`
- [ ] `resolve_username(ctx, username_arg)` 正确解析用户名
- [ ] Discord 分页视图封装保留原有功能

## QQ 适配器检查

- [ ] `adapters/qq_adapter.py` 已创建
- [ ] `QQAdapter` 继承自 `PlatformAdapter`
- [ ] `get_user_context(event)` 正确返回 `UserContext`
- [ ] `send(event, message)` 正确处理 `TextMessage`
- [ ] `send(event, message)` 正确处理 `ImageMessage` (使用 `MessageSegment.image`)
- [ ] `resolve_username_qq(event, username_arg)` 正确解析用户名

## Backend 重构检查

- [ ] `backend/user.py` 已重构使用 `UserContext` 参数
- [ ] `bind_user(context, username)` 工作正常
- [ ] `unbind_user(context)` 工作正常
- [ ] `get_user_binding(context)` 返回正确的绑定信息
- [ ] `set_user_gamemode(context, gamemode)` 工作正常
- [ ] `get_user_gamemode(context)` 返回正确的游戏模式
- [ ] `backend/user_qq.py` 已删除
- [ ] 所有对 `backend/user_qq.py` 的引用已更新

## 服务层检查

- [ ] `services/__init__.py` 已创建
- [ ] `services/user_service.py` 已创建
- [ ] `UserService.bind_user(context, username)` 工作正常
- [ ] `UserService.unbind_user(context)` 工作正常
- [ ] `UserService.get_user_info(username)` 工作正常
- [ ] `UserService.set_gamemode(context, mode)` 工作正常
- [ ] `UserService.get_gamemode(context)` 工作正常
- [ ] `services/score_service.py` 已创建
- [ ] `ScoreService.get_beatmap_scores(context, beatmap_id)` 工作正常
- [ ] `ScoreService.get_recent_scores(context, include_fails)` 工作正常
- [ ] `ScoreService.get_best_scores(context, limit)` 工作正常
- [ ] `ScoreService.get_today_bp(context)` 工作正常
- [ ] `services/beatmap_service.py` 已创建
- [ ] `BeatmapService.get_beatmap_info(beatmap_id)` 工作正常

## Discord Cogs 重构检查

- [ ] `frontend/discord/cogs/user.py` 使用 `DiscordAdapter`
- [ ] `frontend/discord/cogs/user.py` 使用 `UserService`
- [ ] `frontend/discord/cogs/scores.py` 使用 `DiscordAdapter`
- [ ] `frontend/discord/cogs/scores.py` 使用 `ScoreService`
- [ ] Discord 翻页视图功能保留
- [ ] `frontend/discord/cogs/beatmap.py` 使用 `DiscordAdapter`
- [ ] `frontend/discord/cogs/beatmap.py` 使用 `BeatmapService`

## QQ Plugins 重构检查

- [ ] `frontend/qq/plugins/user.py` 使用 `QQAdapter`
- [ ] `frontend/qq/plugins/user.py` 使用 `UserService`
- [ ] `frontend/qq/plugins/scores.py` 使用 `QQAdapter`
- [ ] `frontend/qq/plugins/scores.py` 使用 `ScoreService`
- [ ] `frontend/qq/plugins/beatmap.py` 使用 `QQAdapter`
- [ ] `frontend/qq/plugins/beatmap.py` 使用 `BeatmapService`

## 代码质量检查

- [ ] `uv run ruff check` 无错误
- [ ] `uv run pyright` 无类型错误
- [ ] 所有新代码遵循项目代码风格
- [ ] 所有新函数有类型注解

## 功能验证检查

- [ ] Discord Bot 可以正常启动
- [ ] Discord `!bind` 命令工作正常
- [ ] Discord `!info` 命令工作正常
- [ ] Discord `!ps` 命令工作正常
- [ ] Discord `!p` 命令工作正常
- [ ] Discord 翻页功能工作正常
- [ ] QQ Bot 可以正常启动
- [ ] QQ `bind` 命令工作正常
- [ ] QQ `info` 命令工作正常
- [ ] QQ `ps` 命令工作正常
- [ ] QQ `p` 命令工作正常
