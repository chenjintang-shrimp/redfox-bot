"""用户服务 - 平台无关的用户业务逻辑"""

from dataclasses import dataclass
from typing import Optional

from backend.user import (
    get_user_info as _get_user_info,
    bind_user as _bind_user,
    unbind_user as _unbind_user,
    set_user_gamemode as _set_user_gamemode,
    get_user_gamemode as _get_user_gamemode,
    get_user_binding_by_context,
)
from backend.exceptions.user import UserNotBindError
from models.context import UserContext


@dataclass(frozen=True, slots=True)
class UserInfo:
    """用户信息数据对象"""

    id: int
    username: str
    avatar_url: str
    playmode: str
    statistics: dict
    country: dict
    pp: float
    global_rank: int | None
    rank_history: list[int]
    rank_history_mode: str | None

    @classmethod
    def from_api_response(cls, data: dict) -> "UserInfo":
        """从API响应创建UserInfo"""
        stats = data.get("statistics") or {}
        raw_rank_history = data.get("rank_history", {})
        history_data = (
            raw_rank_history.get("data", [])
            if isinstance(raw_rank_history, dict)
            else []
        )
        return cls(
            id=data["id"],
            username=data["username"],
            avatar_url=data.get("avatar_url", ""),
            playmode=data.get("playmode", "osu"),
            statistics=stats,
            country=data.get("country", {}),
            pp=stats.get("pp", 0.0),
            global_rank=stats.get("global_rank"),
            rank_history=[
                rank
                for rank in history_data
                if isinstance(rank, int) and not isinstance(rank, bool) and rank > 0
            ],
            rank_history_mode=(
                raw_rank_history.get("mode")
                if isinstance(raw_rank_history, dict)
                else None
            ),
        )


class UserService:
    """用户服务类

    提供平台无关的用户相关业务逻辑
    """

    @staticmethod
    async def get_user_info(
        username: str, mode: str | None = None
    ) -> UserInfo:
        """获取用户信息（通过用户名）

        Args:
            username: osu! 用户名
            mode: 指定的游戏模式，省略时使用 API 默认模式

        Returns:
            UserInfo: 用户信息对象
        """
        data = await _get_user_info(username, mode=mode)
        return UserInfo.from_api_response(data)

    @staticmethod
    async def get_user_info_by_id(
        user_id: int, mode: str | None = None
    ) -> UserInfo:
        """获取用户信息（通过用户ID）

        Args:
            user_id: osu! 用户ID
            mode: 指定的游戏模式，省略时使用 API 默认模式

        Returns:
            UserInfo: 用户信息对象
        """
        data = await _get_user_info(user_id, mode=mode)
        return UserInfo.from_api_response(data)

    @staticmethod
    async def bind_user(context: UserContext, username: str) -> UserInfo:
        """绑定用户

        Args:
            context: 用户上下文
            username: osu! 用户名

        Returns:
            UserInfo: 绑定的用户信息
        """
        await _bind_user(context, username)
        return await UserService.get_user_info(username)

    @staticmethod
    async def unbind_user(context: UserContext) -> bool:
        """解绑用户

        Args:
            context: 用户上下文

        Returns:
            bool: 是否成功解绑
        """
        return await _unbind_user(context)

    @staticmethod
    async def set_gamemode(context: UserContext, gamemode: str | None) -> bool:
        """设置默认游戏模式

        Args:
            context: 用户上下文
            gamemode: 游戏模式或 None 清除设置

        Returns:
            bool: 是否设置成功
        """
        return await _set_user_gamemode(context, gamemode)

    @staticmethod
    async def get_gamemode(context: UserContext) -> str | None:
        """获取默认游戏模式

        Args:
            context: 用户上下文

        Returns:
            str | None: 游戏模式或 None
        """
        return await _get_user_gamemode(context)

    @staticmethod
    async def resolve_username(
        context: UserContext, username_arg: Optional[str]
    ) -> str:
        """解析用户名

        如果 username_arg 为 None，返回已绑定用户的用户名
        如果 username_arg 不为 None，直接返回

        Args:
            context: 用户上下文
            username_arg: 用户提供的用户名参数

        Returns:
            str: 解析后的用户名

        Raises:
            UserNotBindError: 用户未绑定且未提供用户名
        """
        if username_arg is not None:
            return username_arg.strip()

        if not context.is_bound or context.osu_username is None:
            raise UserNotBindError(context.platform_user_id)

        return context.osu_username

    @staticmethod
    async def get_binding(context: UserContext) -> Optional[dict]:
        """获取绑定信息

        Args:
            context: 用户上下文

        Returns:
            dict | None: 绑定信息或 None
        """
        binding = await get_user_binding_by_context(context)
        if binding is None:
            return None
        return {
            "osu_id": binding.osu_id,
            "osu_username": binding.osu_username,
            "current_gamemode": binding.current_gamemode,
        }
