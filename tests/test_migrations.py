import asyncio
from collections.abc import Iterator

import pytest
import src.models  # noqa: F401
from alembic import command
from alembic.autogenerate import compare_metadata
from alembic.migration import MigrationContext
from sqlalchemy import inspect
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.pool import NullPool
from sqlmodel import SQLModel
from src.db import Settings
from tests.conftest import alembic_config
from tests.helpers import drop_database, recreate_database, url_for

TABLES = {
    "skill",
    "experience",
    "project",
    "projectrequest",
    "experienceskilllink",
    "projectskilllink",
}


@pytest.fixture
def migration_db() -> Iterator[str]:
    """Base de Postgres vacía para probar las migraciones por separado."""
    url = url_for("migrations_test")
    recreate_database(url)
    yield url
    drop_database(url)


async def inspect_db(url: str, fn):  # type: ignore[no-untyped-def]
    engine = create_async_engine(url, poolclass=NullPool)
    try:
        async with engine.connect() as conn:
            return await conn.run_sync(fn)
    finally:
        await engine.dispose()


def table_names(conn: Connection) -> set[str]:
    return set(inspect(conn).get_table_names())


def enum_names(conn: Connection) -> set[str]:
    return {e["name"] for e in inspect(conn).get_enums()}


def schema_diff(conn: Connection) -> list[object]:
    context = MigrationContext.configure(conn, opts={"compare_type": True})
    return list(compare_metadata(context, SQLModel.metadata))


async def test_upgrade_creates_all_tables(migration_db: str) -> None:
    await asyncio.to_thread(command.upgrade, alembic_config(migration_db), "head")

    assert TABLES <= await inspect_db(migration_db, table_names)


async def test_models_match_migrations(migration_db: str) -> None:
    await asyncio.to_thread(command.upgrade, alembic_config(migration_db), "head")

    diff = await inspect_db(migration_db, schema_diff)

    assert diff == [], "Hay cambios en los modelos sin migración: alembic revision --autogenerate"


async def test_downgrade_removes_tables_and_enums(migration_db: str) -> None:
    cfg = alembic_config(migration_db)
    await asyncio.to_thread(command.upgrade, cfg, "head")
    await asyncio.to_thread(command.downgrade, cfg, "base")

    assert TABLES.isdisjoint(await inspect_db(migration_db, table_names))
    assert await inspect_db(migration_db, enum_names) == set()


def test_database_url_prefers_database_url_variable() -> None:
    settings = Settings(_env_file=None, DATABASE_URL="postgresql://u:p@h:5432/d")  # type: ignore[call-arg]

    assert settings.database_url == "postgresql+asyncpg://u:p@h:5432/d"


def test_database_url_encodes_special_characters() -> None:
    settings = Settings(
        _env_file=None, postgres_user="u", postgres_password="p@ss/1", postgres_db="d"
    )

    assert settings.database_url == "postgresql+asyncpg://u:p%40ss%2F1@localhost:5432/d"
