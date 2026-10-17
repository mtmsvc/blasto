import asyncio

from blasto.db import engine  # reuse the app's engine instead of creating a second one
from blasto.models import Base


async def main() -> None:
    async with (
        engine.begin() as conn
    ):  # an async connection with a transaction, committed at the end
        await conn.run_sync(
            Base.metadata.create_all
        )  # runs the sync create_all on that async connection
    await engine.dispose()  # close the pool so the script exits cleanly


asyncio.run(main())  # an event loop to run the async code
