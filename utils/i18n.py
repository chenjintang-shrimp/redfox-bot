"""国际化 (i18n) 管理模块

支持多平台、多语言的字符串管理
"""

from pathlib import Path
from typing import Any

import yaml

from utils.logger import get_logger

logger = get_logger("utils.i18n")

# 默认配置
DEFAULT_LANGUAGE = "zh"
I18N_DIR = Path(__file__).parent.parent / "config" / "i18n"


class I18nManager:
    """i18n 管理器

    每个平台独立管理自己的语言配置
    """

    _instances: dict[str, "I18nManager"] = {}

    def __new__(cls, platform: str, language: str | None = None):
        """单例模式：每个平台只有一个实例"""
        key = f"{platform}:{language or 'default'}"
        if key not in cls._instances:
            cls._instances[key] = super().__new__(cls)
            cls._instances[key]._initialized = False
        return cls._instances[key]

    def __init__(self, platform: str, language: str | None = None):
        if self._initialized:
            return

        self.platform = platform
        self.language = language or DEFAULT_LANGUAGE
        self._strings: dict[str, Any] = {}

        self._load_strings()
        self._initialized = True

        logger.debug(f"I18nManager initialized: platform={platform}, language={self.language}")

    def _load_strings(self):
        """加载语言文件"""
        # 加载平台特定的语言文件
        platform_file = I18N_DIR / self.platform / f"{self.language}.yaml"
        if platform_file.exists():
            try:
                with open(platform_file, "r", encoding="utf-8") as f:
                    self._strings = yaml.safe_load(f) or {}
                logger.debug(f"Loaded i18n file: {platform_file}")
            except Exception as e:
                logger.error(f"Failed to load i18n file {platform_file}: {e}")
                self._strings = {}
        else:
            logger.warning(f"i18n file not found: {platform_file}")
            self._strings = {}

    def get(self, key: str, default: str | None = None, **kwargs) -> str:
        """获取翻译字符串

        Args:
            key: 键值，使用点号分隔，如 "user.bind_success"
            default: 默认返回值
            **kwargs: 格式化参数

        Returns:
            翻译后的字符串
        """
        # 按层级查找
        keys = key.split(".")
        value = self._strings

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                # 找不到，返回默认值或键名
                result = default if default is not None else f"[{key}]"
                logger.debug(f"i18n key not found: {key}")
                return result

        # 格式化字符串
        if isinstance(value, str):
            try:
                return value.format(**kwargs)
            except KeyError as e:
                logger.warning(f"Missing format arg {e} for key: {key}")
                return value

        # 如果不是字符串，返回默认值
        return default if default is not None else f"[{key}]"

    def reload(self):
        """重新加载语言文件"""
        self._load_strings()
        logger.info(f"Reloaded i18n: platform={self.platform}, language={self.language}")


def get_i18n(platform: str, language: str | None = None) -> I18nManager:
    """获取 i18n 管理器实例

    Args:
        platform: 平台名称，如 "qq", "discord"
        language: 语言代码，如 "zh", "en"

    Returns:
        I18nManager 实例
    """
    return I18nManager(platform, language)
