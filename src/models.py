from datetime import UTC, date, datetime
from enum import StrEnum
from typing import Self

from pydantic import model_validator
from sqlmodel import Field, Relationship, SQLModel


class SkillCategory(StrEnum):
    LANGUAGE = "language"
    FRAMEWORK = "framework"
    TOOL = "tool"
    SOFT = "soft"
    OTHER = "other"


class ExperienceSkillLink(SQLModel, table=True):
    experience_id: int = Field(foreign_key="experience.id", primary_key=True)
    skill_id: int = Field(foreign_key="skill.id", primary_key=True)


class ProjectSkillLink(SQLModel, table=True):
    project_id: int = Field(foreign_key="project.id", primary_key=True)
    skill_id: int = Field(foreign_key="skill.id", primary_key=True)


class SkillBase(SQLModel):
    name: str = Field(index=True, unique=True, min_length=1)
    category: SkillCategory = SkillCategory.OTHER
    level: int | None = Field(default=None, ge=1, le=5)


class Skill(SkillBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    experiences: list[Experience] = Relationship(
        back_populates="skills", link_model=ExperienceSkillLink
    )
    projects: list[Project] = Relationship(back_populates="skills", link_model=ProjectSkillLink)


class SkillCreate(SkillBase):
    pass


class SkillRead(SkillBase):
    id: int


class ExperienceBase(SQLModel):
    company: str = Field(min_length=1)
    role: str = Field(min_length=1)
    description: str
    location: str | None = None
    start_date: date
    end_date: date | None = None


class Experience(ExperienceBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    skills: list[Skill] = Relationship(back_populates="experiences", link_model=ExperienceSkillLink)


class ExperienceCreate(ExperienceBase):
    skills: list[str] = []

    @model_validator(mode="after")
    def check_dates(self) -> Self:
        if self.end_date is not None and self.end_date < self.start_date:
            raise ValueError("end_date must not be before start_date")
        return self


class ExperienceRead(ExperienceBase):
    id: int
    skills: list[SkillRead] = []


class ExperienceBrief(SQLModel):
    id: int
    company: str
    role: str


class ProjectBase(SQLModel):
    name: str = Field(min_length=1)
    description: str
    role: str | None = None
    start_date: date | None = None
    end_date: date | None = None


class Project(ProjectBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    experience_id: int | None = Field(default=None, foreign_key="experience.id")
    experience: Experience | None = Relationship()
    skills: list[Skill] = Relationship(back_populates="projects", link_model=ProjectSkillLink)


class ProjectCreate(ProjectBase):
    experience_id: int | None = None
    skills: list[str] = []

    @model_validator(mode="after")
    def check_dates(self) -> Self:
        if self.start_date and self.end_date and self.end_date < self.start_date:
            raise ValueError("end_date must not be before start_date")
        return self


class ProjectRead(ProjectBase):
    id: int
    experience: ExperienceBrief | None = None
    skills: list[SkillRead] = []


class RequestStatus(StrEnum):
    PENDING = "pending"
    PROCESSING = "processing"
    DONE = "done"
    FAILED = "failed"


class ProjectRequestBase(SQLModel):
    title: str = Field(min_length=1)
    description: str


class ProjectRequest(ProjectRequestBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    status: RequestStatus = RequestStatus.PENDING
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class ProjectRequestCreate(ProjectRequestBase):
    pass


class ProjectRequestRead(ProjectRequestBase):
    id: int
    status: RequestStatus
    created_at: datetime
