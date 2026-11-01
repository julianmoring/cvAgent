from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException
from sqlmodel import text
from sqlmodel.ext.asyncio.session import AsyncSession

from src.db import get_session

app = FastAPI()

SessionDep = Annotated[AsyncSession, Depends(get_session)]


@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "Hello World"}


@app.get("/health")
async def health(session: SessionDep) -> dict[str, str | bool]:
    try:
        await session.exec(text("SELECT 1"))  # type: ignore[call-overload]
    except Exception as exc:
        raise HTTPException(status_code=503, detail="database unavailable") from exc
    return {"status": "ok", "db": True}
