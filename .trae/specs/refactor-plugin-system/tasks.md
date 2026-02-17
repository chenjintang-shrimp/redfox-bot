# 插件系统重构任务列表

## Task 1: 创建核心抽象层 (Foundation)

创建适配器抽象、用户上下文模型和消息类型定义

- [ ] SubTask 1.1: 创建 `models/context.py` 定义 `UserContext` 数据类
- [ ] SubTask 1.2: 创建 `adapters/base.py` 定义 `PlatformAdapter` 抽象基类
- [ ] SubTask 1.3: 创建 `adapters/message_types.py` 定义统一的消息类型 (`TextMessage`, `ImageMessage`, `EmbedMessage`)
- [ ] SubTask 1.4: 更新 `backend/database.py` 添加通过 `(platform, user_id)` 查询的接口

## Task 2: 实现 Discord 适配器

实现 Discord 平台的适配器

- [ ] SubTask 2.1: 创建 `adapters/discord_adapter.py` 实现 `DiscordAdapter` 类
  - 实现 `get_user_context(ctx)` 方法
  - 实现 `send(ctx, message)` 方法
  - 实现 `resolve_username(ctx, username_arg)` 方法
- [ ] SubTask 2.2: 实现 Discord 特定的分页视图封装 (保留 Discord 翻页特性)

## Task 3: 实现 QQ 适配器

实现 QQ 平台的适配器

- [ ] SubTask 3.1: 创建 `adapters/qq_adapter.py` 实现 `QQAdapter` 类
  - 实现 `get_user_context(event)` 方法
  - 实现 `send(event, message)` 方法
  - 实现 `resolve_username_qq(event, username_arg)` 方法

## Task 4: 重构 Backend 用户管理

将平台特定的用户管理合并为平台无关的接口

- [ ] SubTask 4.1: 重构 `backend/user.py`
  - 修改 `bind_user()` 接收 `UserContext` 参数
  - 修改 `unbind_user()` 接收 `UserContext` 参数
  - 修改 `set_user_gamemode()` 接收 `UserContext` 参数
  - 修改 `get_user_gamemode()` 接收 `UserContext` 参数
  - 添加 `get_user_binding(context)` 统一查询接口
- [ ] SubTask 4.2: 删除 `backend/user_qq.py`
- [ ] SubTask 4.3: 更新所有导入 `backend/user_qq.py` 的引用

## Task 5: 创建统一服务层

创建平台无关的业务逻辑服务

- [ ] SubTask 5.1: 创建 `services/__init__.py`
- [ ] SubTask 5.2: 创建 `services/user_service.py` 实现 `UserService` 类
  - `bind_user(context, username)`
  - `unbind_user(context)`
  - `get_user_info(username)`
  - `set_gamemode(context, mode)`
  - `get_gamemode(context)`
- [ ] SubTask 5.3: 创建 `services/score_service.py` 实现 `ScoreService` 类
  - `get_beatmap_scores(context, beatmap_id)`
  - `get_recent_scores(context, include_fails)`
  - `get_best_scores(context, limit)`
  - `get_today_bp(context)`
- [ ] SubTask 5.4: 创建 `services/beatmap_service.py` 实现 `BeatmapService` 类
  - `get_beatmap_info(beatmap_id)`

## Task 6: 重构 Discord Cogs

将 Discord Cogs 改为使用新的适配器和服务层

- [ ] SubTask 6.1: 重构 `frontend/discord/cogs/user.py`
  - 使用 `DiscordAdapter` 获取用户上下文
  - 使用 `UserService` 处理业务逻辑
  - 使用适配器发送消息
- [ ] SubTask 6.2: 重构 `frontend/discord/cogs/scores.py`
  - 使用 `DiscordAdapter` 和 `ScoreService`
  - 保留 Discord 特有的翻页视图功能
- [ ] SubTask 6.3: 重构 `frontend/discord/cogs/beatmap.py`
  - 使用 `DiscordAdapter` 和 `BeatmapService`

## Task 7: 重构 QQ Plugins

将 QQ Plugins 改为使用新的适配器和服务层

- [ ] SubTask 7.1: 重构 `frontend/qq/plugins/user.py`
  - 使用 `QQAdapter` 获取用户上下文
  - 使用 `UserService` 处理业务逻辑
  - 使用适配器发送消息
- [ ] SubTask 7.2: 重构 `frontend/qq/plugins/scores.py`
  - 使用 `QQAdapter` 和 `ScoreService`
- [ ] SubTask 7.3: 重构 `frontend/qq/plugins/beatmap.py`
  - 使用 `QQAdapter` 和 `BeatmapService`

## Task 8: 代码清理和验证

清理旧代码并验证重构结果

- [ ] SubTask 8.1: 运行 `uv run ruff check` 检查代码风格
- [ ] SubTask 8.2: 运行 `uv run pyright` 检查类型错误
- [ ] SubTask 8.3: 验证 Discord Bot 可以正常启动和响应命令
- [ ] SubTask 8.4: 验证 QQ Bot 可以正常启动和响应命令

# Task Dependencies

- Task 2 依赖 Task 1
- Task 3 依赖 Task 1
- Task 4 依赖 Task 1
- Task 5 依赖 Task 4
- Task 6 依赖 Task 2 和 Task 5
- Task 7 依赖 Task 3 和 Task 5
- Task 8 依赖 Task 6 和 Task 7
