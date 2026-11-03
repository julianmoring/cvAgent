import asyncio

import asyncpg
from sqlalchemy.engine import URL, make_url
from src.db import Settings


def _base_url() -> URL:
    return make_url(Settings().database_url)


def url_for(suffix: str) -> str:
    """URL SQLAlchemy de una base de pruebas: `<POSTGRES_DB>_<suffix>`."""
    base = _base_url()
    return base.set(database=f"{base.database}_{suffix}").render_as_string(hide_password=False)


async def _admin(sql: str) -> None:
    admin = _base_url().set(drivername="postgresql", database="postgres")
    conn = await asyncpg.connect(admin.render_as_string(hide_password=False))
    try:
        await conn.execute(sql)
    finally:
        await conn.close()


def database_name(url: str) -> str:
    name = make_url(url).database
    assert name is not None
    return name


def recreate_database(url: str) -> None:
    name = database_name(url)
    asyncio.run(_admin(f'DROP DATABASE IF EXISTS "{name}" WITH (FORCE)'))
    asyncio.run(_admin(f'CREATE DATABASE "{name}"'))


def drop_database(url: str) -> None:
    asyncio.run(_admin(f'DROP DATABASE IF EXISTS "{database_name(url)}" WITH (FORCE)'))
