# Redfox osu! bot
<img width="1448" height="623" alt="Bot-banner" src="https://github.com/user-attachments/assets/ee1bab70-e7f1-465b-892a-99182bdf61af" />

## 🎯 功能特性

为了保障用户体验，命令参考 [yumu-bot](https://github.com/yumu-bot/yumu-bot) 进行设计，基本保持功能特性高度一致

### 多平台支持

- **Discord** - 完整的 Discord 机器人支持
- **QQ** - QQ 机器人支持（开发中）
- **统一API** - 基于相同的后端 API 服务

## 🚀 快速开始

### 环境要求

- Python 3.14+
- Discord Bot Token
- osu! API 访问权限

### 安装步骤

1. **克隆项目**

```bash
git clone https://github.com/your-username/g0v0bot-discord.git
cd g0v0bot-discord
```

1. **安装依赖**

```bash
uv sync
```

1. **配置环境变量**
复制 `.env.example` 为 `.env` 并填写相应配置：

```bash
cp .env.example .env
```

编辑 `.env` 文件：

```env
BOT_TOKEN=your_discord_bot_token
OAUTH_APP_ID=your_oauth_app_id
OAUTH_APP_TOKEN=your_app_token
SQL_DB_FILE=./database.db
API_URL=https://lazer-api.g0v0.top
STRINGS_FILE=config/strings.json
OAUTH_REDIRECT_URI=http://localhost:8000/callback
WEB_SERVER_PORT=8000
WEB_SERVER_HOST=0.0.0.0
```

1. **运行机器人**

```bash
# 运行 Discord 机器人
uv run discord-bot

# 或者运行 QQ 机器人
uv run qq-bot
```
## 🏗️ 技术架构

### 项目结构

```
g0v0bot-discord/
├── backend/           # 后端核心逻辑
│   ├── api_client.py  # API 客户端
│   ├── database.py    # 数据库操作
│   ├── user.py       # 用户相关逻辑
│   ├── beatmap.py    # 谱面相关逻辑
│   └── scores.py     # 成绩相关逻辑
├── frontend/          # 前端机器人实现
│   ├── discord/      # Discord 机器人
│   └── qq/           # QQ 机器人
├── renderer/          # 消息渲染模块
├── utils/            # 工具函数
├── config/           # 配置文件
└── 项目配置文件
```

### 核心特性

- **异步架构** - 基于 async/await 的高性能处理
- **模块化设计** - 清晰的代码组织和职责分离
- **OAuth2 认证** - 安全的 API 访问机制
- **模板化消息** - 可配置的消息格式化系统
- **多平台支持** - 易于扩展新的聊天平台

### 技术栈

- **Python 3.14+** - 编程语言
- **FastAPI** - Web 框架
- **discord.py** - Discord 机器人库
- **SQLModel** - 数据库 ORM
- **httpx** - HTTP 客户端
- **loguru** - 日志记录

## 🔧 开发指南

### 添加新功能

1. **后端逻辑** - 在 `backend/` 目录添加业务逻辑
2. **前端命令** - 在 `frontend/` 对应平台添加命令处理
3. **消息渲染** - 在 `renderer/` 添加消息格式化逻辑
4. **字符串模板** - 在 `config/strings.json` 配置消息模板

### 代码规范

- 使用类型注解
- 遵循 PEP 8 代码风格
- 使用异步编程模式
- 添加适当的错误处理

## 🤝 贡献指南

我们欢迎任何形式的贡献！

### 如何贡献

1. Fork 本项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

### 报告问题

请使用 GitHub Issues 报告 bug 或提出功能请求。

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

---

⭐ 如果这个项目对你有帮助，请给个 Star 支持一下！
