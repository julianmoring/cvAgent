from collections.abc import AsyncIterator
from unittest.mock import AsyncMock

from fastapi.testclient import TestClient
from sqlmodel.ext.asyncio.session import AsyncSession
from src.api.main import app
from src.db import Settings, get_session


def test_health_ok(client: TestClient) -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "db": True}


def test_health_returns_503_when_db_fails() -> None:
    async def broken_session() -> AsyncIterator[AsyncSession]:
        session = AsyncMock(spec=AsyncSession)
        session.exec.side_effect = ConnectionError("down")
        yield session

    app.dependency_overrides[get_session] = broken_session
    try:
        response = TestClient(app).get("/health")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 503


def test_database_url_built_from_postgres_vars() -> None:
    settings = Settings(postgres_user="u", postgres_password="p", postgres_db="d", _env_file=None)  # type: ignore[call-arg]

    assert settings.database_url == "postgresql+asyncpg://u:p@localhost:5432/d"
