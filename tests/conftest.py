from collections.abc import Iterator

import pytest
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text

from alembic import command
from blasto.config import settings
from blasto.main import app


@pytest.fixture(scope="session", autouse=True)  # once per test run, automatically
def migrated_database() -> None:
    command.upgrade(
        Config("alembic.ini"), "head"
    )  # like `alembic upgrade head`, on the test database


@pytest.fixture(scope="session")  # one client for the whole run: one event loop
def client() -> Iterator[TestClient]:
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(autouse=True)  # around every test, automatically
def clean_tables() -> Iterator[None]:
    yield  # the test runs here
    engine = create_engine(
        settings.database_url.replace("+asyncpg", "+psycopg")
    )  # short-lived sync connection
    with engine.begin() as conn:
        conn.execute(
            text("TRUNCATE applications RESTART IDENTITY")
        )  # empty the table; IDs restart at 1
    engine.dispose()
