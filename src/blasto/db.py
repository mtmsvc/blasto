from collections.abc import (
    AsyncIterator,  # type for a function that yields asynchronously
)

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from blasto.config import settings

engine = create_async_engine(
    settings.database_url
)  # holds a pool of connections; connects on first use
SessionLocal = async_sessionmaker(
    engine, expire_on_commit=False
)  # creates sessions; objects stay readable after commit


async def get_session() -> AsyncIterator[AsyncSession]:  # one session per request
    async with (
        SessionLocal() as session
    ):  # open a session; closed automatically at the end
        yield session  # hand it to the endpoint
