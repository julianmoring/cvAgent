from pathlib import Path

import pytest
import src.models  # noqa: F401
from alembic import command
from alembic.autogenerate import compare_metadata
from alembic.config import Config
from alembic.migration import MigrationContext
from sqlalchemy import create_engine, inspect
from sqlmodel import SQLModel
from src.db import Settings

TABLES = {
    "skill",
    "experience",
    "project",
    "projectrequest",
    "experienceskilllink",
    "projectskilllink",
}


@pytest.fixture
def alembic_cfg(tmp_path: Path) -> Config:
    db = tmp_path / "migrated.db"
    cfg = Config("alembic.ini")
    cfg.cmd_opts = type("Opts", (), {"x": [f"url=sqlite+aiosqlite:///{db.as_posix()}"]})()  # type: ignore[assignment]
    return cfg


def sync_url(cfg: Config) -> str:
    x = cfg.cmd_opts.x[0]  # type: ignore[union-attr]
    return str(x).removeprefix("url=").replace("+aiosqlite", "")


def test_upgrade_creates_all_tables(alembic_cfg: Config) -> None:
    command.upgrade(alembic_cfg, "head")

    engine = create_engine(sync_url(alembic_cfg))
    assert TABLES <= set(inspect(engine).get_table_names())


def test_models_match_migrations(alembic_cfg: Config) -> None:
    command.upgrade(alembic_cfg, "head")

    engine = create_engine(sync_url(alembic_cfg))
    with engine.connect() as conn:
        context = MigrationContext.configure(conn, opts={"compare_type": True})
        diff = compare_metadata(context, SQLModel.metadata)

    assert diff == [], "Hay cambios en los modelos sin migración: alembic revision --autogenerate"


def test_downgrade_removes_tables(alembic_cfg: Config) -> None:
    command.upgrade(alembic_cfg, "head")
    command.downgrade(alembic_cfg, "base")

    engine = create_engine(sync_url(alembic_cfg))
    assert TABLES.isdisjoint(inspect(engine).get_table_names())


def test_database_url_prefers_database_url_variable() -> None:
    settings = Settings(_env_file=None, DATABASE_URL="postgresql://u:p@h:5432/d")  # type: ignore[call-arg]

    assert settings.database_url == "postgresql+asyncpg://u:p@h:5432/d"


def test_database_url_encodes_special_characters() -> None:
    settings = Settings(
        _env_file=None, postgres_user="u", postgres_password="p@ss/1", postgres_db="d"
    )

    assert settings.database_url == "postgresql+asyncpg://u:p%40ss%2F1@localhost:5432/d"
