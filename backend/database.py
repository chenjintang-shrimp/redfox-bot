from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel, create_engine, Session, select
from utils.variable import SQL_DB_FILE


class User(SQLModel, table=True):
    discord_id: str = Field(primary_key=True)
    osu_id: int
    osu_username: str
    access_token: str
    refresh_token: str
    expires_at: datetime
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


# Create the database engine
sqlite_url = f"sqlite:///{SQL_DB_FILE}"
engine = create_engine(sqlite_url)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    return Session(engine)


def get_user_by_discord_id(discord_id: str) -> Optional[User]:
    with get_session() as session:
        statement = select(User).where(User.discord_id == discord_id)
        results = session.exec(statement)
        return results.first()


def save_user(user: User):
    with get_session() as session:
        # Check if user exists to update or insert
        statement = select(User).where(User.discord_id == user.discord_id)
        existing_user = session.exec(statement).first()

        if existing_user:
            existing_user.osu_id = user.osu_id
            existing_user.osu_username = user.osu_username
            existing_user.access_token = user.access_token
            existing_user.refresh_token = user.refresh_token
            existing_user.expires_at = user.expires_at
            existing_user.updated_at = datetime.now()
            session.add(existing_user)
        else:
            session.add(user)
        session.commit()
        session.refresh(user if not existing_user else existing_user)
