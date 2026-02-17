"""用户上下文模型 - 用于跨层传递用户信息"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class UserContext:
    """
    统一的用户上下文，用于在各层之间传递用户信息

    Attributes:
        platform: 平台标识符，如 "discord", "qq", "telegram" 等
        platform_user_id: 平台原生用户 ID（字符串形式）
        osu_username: 绑定的 osu! 用户名（如果已绑定）
        osu_user_id: 绑定的 osu! 用户 ID（如果已绑定）
        current_gamemode: 用户设置的默认游戏模式
    """

    platform: str
    platform_user_id: str
    osu_username: Optional[str] = None
    osu_user_id: Optional[int] = None
    current_gamemode: Optional[str] = None

    @property
    def is_bound(self) -> bool:
        """检查用户是否已绑定 osu! 账号"""
        return self.osu_username is not None

    def __str__(self) -> str:
        return f"UserContext(platform={self.platform}, user_id={self.platform_user_id}, osu={self.osu_username})"
