from datetime import datetime
from typing import Optional
from enum import Enum

from sqlmodel import Field, SQLModel, select
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession as SQLModelAsyncSession
from utils.variable import SQL_DB_FILE


class Platform(str, Enum):
    """平台类型"""

    DISCORD = "discord"
    QQ = "qq"


class UserBinding(SQLModel, table=True):
    """统一的用户绑定表，支持多平台"""

    id: int = Field(primary_key=True, description="平台用户ID (discord_id 或 qq_id)")
    platform: str = Field(primary_key=True, description="平台类型: discord/qq")
    osu_id: int
    osu_username: str
    current_gamemode: str | None = Field(
        default=None, description="用户自定义的查询游戏模式: osu/taiko/fruits/mania"
    )
    access_token: str | None = None
    refresh_token: str | None = None
    expires_at: datetime | None = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


# 异步引擎：注意是 sqlite+aiosqlite
sqlite_url = f"sqlite+aiosqlite:///{SQL_DB_FILE}"
engine = create_async_engine(sqlite_url)


async def create_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


async def get_session() -> SQLModelAsyncSession:
    return SQLModelAsyncSession(engine)


async def get_user_binding(platform: str, user_id: int) -> Optional[UserBinding]:
    """根据平台和用户ID获取绑定信息"""
    async with SQLModelAsyncSession(engine) as session:
        statement = select(UserBinding).where(
            UserBinding.platform == platform, UserBinding.id == user_id
        )
        results = await session.exec(statement)
        return results.first()


async def save_user_binding(binding: UserBinding):
    """保存用户绑定信息"""
    async with SQLModelAsyncSession(engine) as session:
        binding.updated_at = datetime.now()
        await session.merge(binding)
        await session.commit()


async def delete_user_binding(platform: str, user_id: int) -> bool:
    """删除用户绑定"""
    async with SQLModelAsyncSession(engine) as session:
        statement = select(UserBinding).where(
            UserBinding.platform == platform, UserBinding.id == user_id
        )
        results = await session.exec(statement)
        binding = results.first()

        if binding is None:
            return False

        await session.delete(binding)
        await session.commit()
        return True


# 兼容旧接口 - Discord
async def get_osu_user_by_discord_id(discord_id: int) -> Optional[UserBinding]:
    """兼容旧接口：通过 Discord ID 获取用户绑定"""
    return await get_user_binding(Platform.DISCORD, discord_id)


async def save_osu_user(user: UserBinding):
    """兼容旧接口：保存 Discord 用户绑定"""
    user.platform = Platform.DISCORD
    await save_user_binding(user)


async def delete_osu_user_by_discord_id(discord_id: int) -> bool:
    """兼容旧接口：删除 Discord 用户绑定"""
    return await delete_user_binding(Platform.DISCORD, discord_id)


# 兼容旧接口 - QQ
async def get_osu_user_by_qq_id(qq_id: int) -> Optional[UserBinding]:
    """兼容旧接口：通过 QQ ID 获取用户绑定"""
    return await get_user_binding(Platform.QQ, qq_id)


async def save_osu_user_qq(user: UserBinding):
    """兼容旧接口：保存 QQ 用户绑定"""
    user.platform = Platform.QQ
    await save_user_binding(user)


async def delete_osu_user_by_qq_id(qq_id: int) -> bool:
    """兼容旧接口：删除 QQ 用户绑定"""
    return await delete_user_binding(Platform.QQ, qq_id)
