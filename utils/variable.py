import os
from dotenv import load_dotenv
from pathlib import Path

from utils.logger import get_logger

working_dir: Path = Path(__file__).parent.parent

# Load environment variables from .env file
load_dotenv(working_dir / ".env")

# Discord Bot Token
BOT_TOKEN = os.getenv("BOT_TOKEN", "")

if BOT_TOKEN == "":
    get_logger("envs").error("Must Specify env BOT_TOKEN")

# OAuth App ID
OAUTH_APP_ID = os.getenv("OAUTH_APP_ID", "")

if OAUTH_APP_ID == "":
    get_logger("envs").error("Must Specify env OAUTH_APP_ID")

# SQLite Database File path
SQL_DB_FILE = os.getenv("SQL_DB_FILE", "./database.db")

# API URL
API_URL = os.getenv("API_URL", "https://lazer-api.g0v0.top")

# Strings JSON configuration file path
STRINGS_FILE = os.getenv("STRINGS_FILE", "config/strings.json")

# API JSON configuration file path
API_FILE = os.getenv("API_FILE", "config/api.json")

# Validated variable
if OAUTH_APP_ID.isdigit():
    OAUTH_APP_ID = OAUTH_APP_ID

# OAuth Redirect URI
OAUTH_REDIRECT_URI = os.getenv("OAUTH_REDIRECT_URI", "http://localhost:8080/callback")

# OAuth Secret
OAUTH_SECRET = os.getenv("OAUTH_SECRET", "")
if OAUTH_SECRET == "":
    get_logger("envs").warning("OAUTH_SECRET is not set, some features may not work")

# OAuth Token TTL (seconds), default 86400 (24 hours)
OAUTH_TOKEN_TTL = int(os.getenv("OAUTH_TOKEN_TTL", "86400"))

# Automatically validate on import if desired, or call explicitly
# Variable.validate()
