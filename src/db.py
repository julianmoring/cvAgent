from collections.abc import AsyncIterator
from functools import lru_cache
from urllib.parse import quote_plus

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    postgres_user: str = ""
    postgres_password: str = ""
    postgres_db: str = ""
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    url_override: str | None = Field(default=None, validation_alias="DATABASE_URL")

    @property
    def database_url(self) -> str:
        """`DATABASE_URL` si existe; si no, se construye con las variables `POSTGRES_*`."""
        if self.url_override:
            return self.url_override.replace("postgresql://", "postgresql+asyncpg://", 1)
        user = quote_plus(self.postgres_user)
        password = quote_plus(self.postgres_password)
        return (
            f"postgresql+asyncpg://{user}:{password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )


@lru_cache
def get_engine() -> AsyncEngine:
    return create_async_engine(Settings().database_url)


async def get_session() -> AsyncIterator[AsyncSession]:
    factory = async_sessionmaker(get_engine(), class_=AsyncSession, expire_on_commit=False)
    async with factory() as session:
        yield session
