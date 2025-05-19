from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime


class ProjectBase(BaseModel):
    name: str = Field(..., example="My Project")
    description: Optional[str] = Field(None, example="Описание проекта")


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    name: Optional[str] = Field(None, example="Новое имя проекта")
    description: Optional[str] = Field(None, example="Новое описание")


class ProjectRead(ProjectBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
