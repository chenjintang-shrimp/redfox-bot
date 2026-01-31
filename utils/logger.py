from loguru import logger
import os

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

# 移除默认 handler
logger.remove()

# 控制台输出（彩色）
logger.add(
    sink=lambda msg: print(msg, end=""),
    colorize=True,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> "
    "<level>{level}</level> "
    "<cyan>{extra[module]}</cyan>.<cyan>{function}</cyan>:<cyan>{line}</cyan> "
    "- <level>{message}</level>",
)

# 文件输出（自动轮转）
logger.add(
    f"{LOG_DIR}/bot.log",
    rotation="5 MB",
    retention="7 days",
    encoding="utf-8",
    enqueue=True,
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {extra[module]}.{function}.{line} - {message}",
)


def get_logger(name: str):
    return logger.bind(module=name)
