from loguru import logger
import os

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

# 移除默认 handler
logger.remove()


def _escape_message(message: str) -> str:
    """转义消息中的花括号，防止被误解析为格式字符串"""
    return message.replace("{", "{{").replace("}", "}}")


def _format_record(record):
    """自定义格式化函数，兼容没有 module 字段的日志"""
    module = (
        record["extra"].get("module", "unknown") if "extra" in record else "unknown"
    )
    message = _escape_message(str(record["message"]))
    return (
        f"<green>{record['time']:YYYY-MM-DD HH:mm:ss}</green> "
        f"<level>{record['level'].name}</level> "
        f"<cyan>{module}</cyan>.<cyan>{record['function']}</cyan>:<cyan>{record['line']}</cyan> "
        f"- <level>{message}</level>\n"
    )


def _format_file_record(record):
    """文件格式化函数"""
    module = (
        record["extra"].get("module", "unknown") if "extra" in record else "unknown"
    )
    message = _escape_message(str(record["message"]))
    return (
        f"{record['time']:YYYY-MM-DD HH:mm:ss} | "
        f"{record['level'].name} | "
        f"{module}.{record['function']}.{record['line']} - "
        f"{message}\n"
    )


# 控制台输出（彩色）
logger.add(
    sink=lambda msg: print(msg, end=""),
    colorize=True,
    format=_format_record,
)

# 文件输出（自动轮转）
logger.add(
    f"{LOG_DIR}/bot.log",
    rotation="5 MB",
    retention="7 days",
    encoding="utf-8",
    enqueue=True,
    format=_format_file_record,
)


def get_logger(name: str):
    return logger.bind(module=name)
