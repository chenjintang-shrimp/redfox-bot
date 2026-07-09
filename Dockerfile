# 使用官方带有 uv 的 Python 3.14 镜像
FROM ghcr.io/astral-sh/uv:python3.14-trixie

# 设置工作目录
WORKDIR /app

# 启用 uv 的字节码编译，加快启动速度
ENV UV_COMPILE_BYTECODE=1

# 复制项目虚拟环境配置文件
COPY pyproject.toml uv.lock ./

# 只安装依赖（利用 Docker 缓存层，只要依赖不变这一步就不会重复执行）
RUN uv sync --frozen --no-install-project

# 复制项目其余所有代码
COPY . .

# 再次同步以安装当前项目本身
RUN uv sync --frozen

# ----------------- 新增：安装 Playwright 浏览器及系统依赖 -----------------
# 1. 更新 apt 并安装 playwright 依赖安装脚本所需的必要工具（如 curl/ca-certificates）
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# 2. 核心：通过 uv 环境安装 chromium 浏览器，并自动安装运行它所需的 Debian 系统底层依赖（如 libgbm 等）
RUN uv run playwright install chromium --with-deps
# ------------------------------------------------------------------------

# 默认暴露 8000 端口（用于 OAuth2 回调等 Web 服务）
EXPOSE 8080

# 默认启动命令（可以在 docker-compose 中被覆盖）
CMD ["uv", "run", "qq-bot"]