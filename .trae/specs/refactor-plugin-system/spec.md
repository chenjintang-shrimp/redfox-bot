# 插件系统重构规范 (Plugin System Refactor Spec)

## Why

当前插件系统存在严重的代码重复问题：

1. backend 层被平台污染，需要为每个平台单独实现 (`user.py` vs `user_qq.py`)
2. frontend 层重复编写相同的业务逻辑流程
3. 没有统一的用户上下文抽象，导致每个层都要处理平台差异

通过引入平台适配器模式和统一服务层，将业务逻辑与平台特定代码分离，实现"一次编写，多处使用"。

## What Changes

- **ADDED**: 新增 `adapters/` 目录，包含平台适配器抽象和实现
- **ADDED**: 新增 `services/` 目录，包含平台无关的业务逻辑服务
- **ADDED**: 新增 `models/context.py`，定义统一的用户上下文 `UserContext`
- **MODIFIED**: 重构 `backend/user.py` 和 `backend/user_qq.py` 合并为平台无关的接口
- **MODIFIED**: 重构 `frontend/discord/cogs/` 使用新的适配器模式
- **MODIFIED**: 重构 `frontend/qq/plugins/` 使用新的适配器模式
- **REMOVED**: 删除重复的 `backend/user_qq.py` 文件

## Impact

- Affected specs: 用户绑定、成绩查询、谱面查询、渲染系统
- Affected code:
  - `backend/user.py`, `backend/user_qq.py`
  - `frontend/discord/cogs/*.py`
  - `frontend/qq/plugins/*.py`
  - `backend/database.py` (可能需要调整查询接口)

## ADDED Requirements

### Requirement: 平台适配器抽象

The system SHALL provide a platform-agnostic adapter interface for Discord and QQ platforms.

#### Scenario: 统一用户上下文获取

- **GIVEN** 用户在 Discord 或 QQ 平台发送命令
- **WHEN** 适配器接收到平台特定的事件/上下文
- **THEN** 适配器 SHALL 返回统一的 `UserContext` 对象，包含:
  - `platform`: 平台类型标识符 (str, 如 "discord", "qq", "telegram" 等)
  - `platform_user_id`: 平台用户ID
  - `osu_username`: 绑定的 osu! 用户名 (如果已绑定)
  - `osu_user_id`: 绑定的 osu! 用户ID
  - `current_gamemode`: 用户设置的默认游戏模式

**Note**: platform 使用字符串而非枚举，便于用户随时接入新平台适配器，每个平台自行定义其标识符。

#### Scenario: 消息发送适配

- **GIVEN** 服务层返回可发送的消息对象 (文字或图片)
- **WHEN** 适配器发送消息
- **THEN** 适配器 SHALL 根据平台特性选择正确的发送方式:
  - Discord: 支持 `discord.File`, `discord.Embed`, 文字
  - QQ: 支持 `MessageSegment.image`, `MessageSegment.text`

### Requirement: 统一业务服务层

The system SHALL provide platform-agnostic service layer for all business logic.

#### Scenario: 用户服务

- **GIVEN** 统一的 `UserContext`
- **WHEN** 调用 `UserService.bind_user(context, osu_username)`
- **THEN** 服务 SHALL 处理绑定逻辑，不感知具体平台

#### Scenario: 成绩服务  

- **GIVEN** 统一的 `UserContext`
- **WHEN** 调用 `ScoreService.get_recent_scores(context, include_fails=True)`
- **THEN** 服务 SHALL 返回成绩数据，不感知具体平台

### Requirement: 用户上下文数据模型

The system SHALL define a `UserContext` dataclass for passing user information across layers.

```python
@dataclass
class UserContext:
    platform: str                   # 平台标识符，如 "discord", "qq"
    platform_user_id: str           # 平台原生用户ID
    osu_username: Optional[str] = None
    osu_user_id: Optional[int] = None
    current_gamemode: Optional[str] = None
    
    @property
    def is_bound(self) -> bool:
        return self.osu_username is not None
```

**平台标识符约定**:

- Discord 适配器使用 `"discord"`
- QQ 适配器使用 `"qq"`
- 新增平台可自由选择标识符，如 `"telegram"`, `"kook"` 等

## MODIFIED Requirements

### Requirement: Backend 用户管理

**Current**: `backend/user.py` 处理 Discord，`backend/user_qq.py` 处理 QQ

**Modified**: 统一使用 `backend/user.py`，接口接收 `UserContext` 或 `(platform, user_id)` 参数

```python
# 修改前
async def bind_user(discord_id: int, username: str)  # 只能处理 Discord
async def bind_user_qq(qq_id: int, username: str)    # 只能处理 QQ

# 修改后
async def bind_user(context: UserContext, username: str)  # 平台无关
async def get_user_binding(context: UserContext) -> Optional[UserBinding]
async def unbind_user(context: UserContext) -> bool
async def set_user_gamemode(context: UserContext, gamemode: Optional[str]) -> bool
async def get_user_gamemode(context: UserContext) -> Optional[str]
```

### Requirement: Frontend Discord Cogs

**Current**: Cog 直接调用 backend 和 renderer

**Modified**: Cog 通过适配器调用统一服务层

```python
class UserCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.adapter = DiscordAdapter(bot)
        self.user_service = UserService()
    
    @commands.hybrid_command(name="bind")
    async def bind(self, ctx: commands.Context, username: str):
        user_ctx = await self.adapter.get_user_context(ctx)
        result = await self.user_service.bind_user(user_ctx, username)
        message = await self.adapter.format_result(result)
        await self.adapter.send(ctx, message)
```

### Requirement: Frontend QQ Plugins

**Current**: 插件直接调用 backend 和 renderer

**Modified**: 插件通过适配器调用统一服务层

```python
bind_cmd = on_command("bind", priority=5)

@bind_cmd.handle()
async def handle_bind(event: MessageEvent, args=CommandArg()):
    adapter = QQAdapter()
    user_ctx = await adapter.get_user_context(event)
    
    user_service = UserService()
    result = await user_service.bind_user(user_ctx, username)
    
    message = await adapter.format_result(result)
    await adapter.send(event, message)
```

## REMOVED Requirements

### Requirement: backend/user_qq.py

**Reason**: 与 backend/user.py 功能完全重复，只是硬编码了 Platform.QQ
**Migration**: 所有调用方改用新的 UserContext 接口

### Requirement: backend/user_qq.py 中的所有函数

**Reason**: 被统一的服务层接口替代
**Migration**:

- `bind_user_qq()` → `UserService.bind_user(context, username)`
- `unbind_user_qq()` → `UserService.unbind_user(context)`
- `get_user_gamemode_qq()` → `UserService.get_gamemode(context)`
- `set_user_gamemode_qq()` → `UserService.set_gamemode(context, mode)`
