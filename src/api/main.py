from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlmodel import SQLModel, select, text
from sqlmodel.ext.asyncio.session import AsyncSession

from src.db import get_engine, get_session
from src.models import Skill, SkillCreate, SkillRead


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    async with get_engine().begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    yield


app = FastAPI(lifespan=lifespan)

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


@app.post("/skills", status_code=201, response_model=SkillRead)
async def create_skill(data: SkillCreate, session: SessionDep) -> Skill:
    skill = Skill.model_validate(data)
    session.add(skill)
    try:
        await session.commit()
    except IntegrityError as exc:
        await session.rollback()
        raise HTTPException(status_code=409, detail="skill already exists") from exc
    await session.refresh(skill)
    return skill


@app.get("/skills", response_model=list[SkillRead])
async def list_skills(session: SessionDep) -> list[Skill]:
    result = await session.exec(select(Skill).order_by(Skill.name))
    return list(result.all())
