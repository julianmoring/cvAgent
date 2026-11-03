from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload
from sqlmodel import col, select, text
from sqlmodel.ext.asyncio.session import AsyncSession

from src.db import get_session
from src.models import (
    Experience,
    ExperienceCreate,
    ExperienceRead,
    Project,
    ProjectCreate,
    ProjectRead,
    ProjectRequest,
    ProjectRequestCreate,
    ProjectRequestRead,
    Skill,
    SkillCreate,
    SkillRead,
)

app = FastAPI()

SessionDep = Annotated[AsyncSession, Depends(get_session)]


async def find_skills(session: AsyncSession, names: list[str]) -> list[Skill]:
    wanted = set(names)
    found = list((await session.exec(select(Skill).where(col(Skill.name).in_(wanted)))).all())
    missing = wanted - {skill.name for skill in found}
    if missing:
        raise HTTPException(status_code=422, detail=f"unknown skills: {sorted(missing)}")
    return found


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


@app.post("/experiences", status_code=201, response_model=ExperienceRead)
async def create_experience(data: ExperienceCreate, session: SessionDep) -> Experience:
    skills = await find_skills(session, data.skills)
    experience = Experience(**data.model_dump(exclude={"skills"}), skills=skills)
    session.add(experience)
    await session.commit()
    return experience


@app.get("/experiences", response_model=list[ExperienceRead])
async def list_experiences(session: SessionDep) -> list[Experience]:
    query = (
        select(Experience)
        .options(selectinload(Experience.skills))  # type: ignore[arg-type]
        .order_by(col(Experience.start_date).desc())
    )
    return list((await session.exec(query)).all())


async def load_projects(session: AsyncSession, project_id: int | None = None) -> list[Project]:
    query = (
        select(Project)
        .options(selectinload(Project.skills), selectinload(Project.experience))  # type: ignore[arg-type]
        .order_by(col(Project.id))
        .execution_options(populate_existing=True)
    )
    if project_id is not None:
        query = query.where(Project.id == project_id)
    return list((await session.exec(query)).all())


@app.post("/projects", status_code=201, response_model=ProjectRead)
async def create_project(data: ProjectCreate, session: SessionDep) -> Project:
    if data.experience_id is not None and await session.get(Experience, data.experience_id) is None:
        raise HTTPException(status_code=422, detail="unknown experience_id")
    skills = await find_skills(session, data.skills)
    project = Project(**data.model_dump(exclude={"skills"}), skills=skills)
    session.add(project)
    await session.commit()
    assert project.id is not None
    return (await load_projects(session, project.id))[0]


@app.get("/projects", response_model=list[ProjectRead])
async def list_projects(session: SessionDep) -> list[Project]:
    return await load_projects(session)


@app.post("/project-requests", status_code=201, response_model=ProjectRequestRead)
async def create_project_request(data: ProjectRequestCreate, session: SessionDep) -> ProjectRequest:
    request = ProjectRequest.model_validate(data)
    session.add(request)
    await session.commit()
    await session.refresh(request)
    return request


@app.get("/project-requests/{request_id}", response_model=ProjectRequestRead)
async def get_project_request(request_id: int, session: SessionDep) -> ProjectRequest:
    request = await session.get(ProjectRequest, request_id)
    if request is None:
        raise HTTPException(status_code=404, detail="project request not found")
    return request
