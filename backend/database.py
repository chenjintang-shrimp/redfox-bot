from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel, select
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession as SQLModelAsyncSession
from utils.variable import SQL_DB_FILE


class OsuUser(SQLModel, table=True):
    discord_id: int = Field(primary_key=True)
    osu_id: int
    osu_username: str
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


async def get_osu_user_by_discord_id(discord_id: int) -> Optional[OsuUser]:
    async with SQLModelAsyncSession(engine) as session:
        statement = select(OsuUser).where(OsuUser.discord_id == discord_id)
        results = await session.exec(statement)
        return results.first()


async def save_osu_user(user: OsuUser):
    async with SQLModelAsyncSession(engine) as session:
        user.updated_at = datetime.now()
        await session.merge(user)
        await session.commit()


async def delete_osu_user_by_discord_id(discord_id: int) -> bool:
    """Delete osu user by Discord ID"""
    async with SQLModelAsyncSession(engine) as session:
        statement = select(OsuUser).where(OsuUser.discord_id == discord_id)
        results = await session.exec(statement)
        user = results.first()

        if user is None:
            return False

        await session.delete(user)
        await session.commit()
        return True
