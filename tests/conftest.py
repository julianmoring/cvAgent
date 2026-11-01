import asyncio
from collections.abc import AsyncIterator, Iterator
from types import SimpleNamespace

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
from src.api.main import app
from src.db import get_session
from tests.helpers import drop_database, recreate_database, url_for


def alembic_config(url: str) -> Config:
    cfg = Config("alembic.ini")
    cfg.cmd_opts = SimpleNamespace(x=[f"url={url}"])  # type: ignore[assignment]
    return cfg


@pytest.fixture(scope="session")
def test_db_url() -> Iterator[str]:
    """Base de Postgres de pruebas, creada desde cero y migrada con Alembic."""
    url = url_for("test")
    recreate_database(url)
    command.upgrade(alembic_config(url), "head")
    yield url
    drop_database(url)


@pytest.fixture
def client(test_db_url: str) -> Iterator[TestClient]:
    engine = create_async_engine(test_db_url, poolclass=NullPool)
    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async def override_session() -> AsyncIterator[AsyncSession]:
        async with factory() as session:
            yield session

    async def truncate_all() -> None:
        tables = ", ".join(f'"{name}"' for name in SQLModel.metadata.tables)
        async with engine.begin() as conn:
            await conn.execute(text(f"TRUNCATE {tables} RESTART IDENTITY CASCADE"))
        await engine.dispose()

    app.dependency_overrides[get_session] = override_session
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
    asyncio.run(truncate_all())
