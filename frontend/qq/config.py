"""QQ 侧专属配置加载

从 config/qq.yaml 读取群白名单等 QQ 专属配置。
与共享的 utils/variable.py 隔离，仅 QQ 前端使用。
"""

from pathlib import Path
from typing import Any

import yaml

from utils.logger import get_logger

_logger = get_logger("qq.config")

_config_path = Path(__file__).resolve().parent.parent.parent / "config" / "qq.yaml"


def _load_qq_config() -> dict[str, Any]:
    """加载 config/qq.yaml，文件不存在时返回空 dict（向后兼容）"""
    if not _config_path.exists():
        _logger.warning(
            f"配置文件不存在: {_config_path}，QQ 群白名单未配置（允许所有群）"
        )
        return {}
    with open(_config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


_QQ_CONFIG = _load_qq_config()

# 群聊白名单：空列表表示允许所有群（向后兼容）
group_whitelist: set[int] = set(_QQ_CONFIG.get("group_whitelist", []))

# 是否允许私聊使用命令
private_enabled: bool = bool(_QQ_CONFIG.get("private_enabled", True))


def is_group_allowed(group_id: int) -> bool:
    """检查指定群是否在白名单中（白名单为空时允许所有群）"""
    if not group_whitelist:
        return True
    return group_id in group_whitelist
