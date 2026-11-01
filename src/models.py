from enum import StrEnum

from sqlmodel import Field, SQLModel


class SkillCategory(StrEnum):
    LANGUAGE = "language"
    FRAMEWORK = "framework"
    TOOL = "tool"
    SOFT = "soft"
    OTHER = "other"


class SkillBase(SQLModel):
    name: str = Field(index=True, unique=True, min_length=1)
    category: SkillCategory = SkillCategory.OTHER
    level: int | None = Field(default=None, ge=1, le=5)


class Skill(SkillBase, table=True):
    id: int | None = Field(default=None, primary_key=True)


class SkillCreate(SkillBase):
    pass


class SkillRead(SkillBase):
    id: int
