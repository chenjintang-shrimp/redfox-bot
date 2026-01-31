import yaml
from pathlib import Path

from utils.logger import get_logger

working_dir: Path = Path(__file__).parent.parent


def _load_config() -> dict:
    """加载 YAML 配置文件"""
    config_path = working_dir / "config" / "config.yaml"

    if not config_path.exists():
        get_logger("config").error(f"配置文件不存在: {config_path}")
        get_logger("config").error(
            "请复制 config/config.example.yaml 为 config/config.yaml 并填写配置"
        )
        return {}

    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


# 加载配置
_CONFIG = _load_config()

# Bot 配置
_BOT_CONFIG = _CONFIG.get("bot", {})
BOT_TOKEN = _BOT_CONFIG.get("token", "")
if not BOT_TOKEN:
    get_logger("config").error("必须配置 bot.token")

_WEB_SERVER_CONFIG = _BOT_CONFIG.get("web_server", {})
WEB_SERVER_HOST = _WEB_SERVER_CONFIG.get("host", "0.0.0.0")
WEB_SERVER_PORT = _WEB_SERVER_CONFIG.get("port", 8000)

# OAuth 配置
_OAUTH_CONFIG = _CONFIG.get("oauth", {})
OAUTH_APP_ID = _OAUTH_CONFIG.get("app_id", "")
if not OAUTH_APP_ID:
    get_logger("config").error("必须配置 oauth.app_id")

OAUTH_SECRET = _OAUTH_CONFIG.get("secret", "")
if not OAUTH_SECRET:
    get_logger("config").warning("oauth.secret 未设置，部分功能可能无法使用")

OAUTH_REDIRECT_URI = _OAUTH_CONFIG.get("redirect_uri", "http://localhost:8000/callback")
OAUTH_TOKEN_TTL = _OAUTH_CONFIG.get("token_ttl", 86400)

# 数据库配置
_DATABASE_CONFIG = _CONFIG.get("database", {})
SQL_DB_FILE = _DATABASE_CONFIG.get("file", "./database.db")

# API 配置
_API_CONFIG = _CONFIG.get("api", {})
API_URL = _API_CONFIG.get("url", "https://lazer-api.g0v0.top")

# 配置文件路径
_CONFIG_FILES = _CONFIG.get("config_files", {})
STRINGS_FILE = _CONFIG_FILES.get("strings", "config/strings.yaml")
API_FILE = _CONFIG_FILES.get("api", "config/api.yaml")
