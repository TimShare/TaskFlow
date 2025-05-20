from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime
from core.entites.core_entities import TaskStatus


class TaskBase(BaseModel):
    project_id: UUID = Field(..., example="123e4567-e89b-12d3-a456-426614174000")
    title: str = Field(..., example="Новая задача")
    description: Optional[str] = Field(None, example="Описание задачи")
    status: TaskStatus = Field(TaskStatus.TODO)
    assignee_id: Optional[UUID] = Field(
        None, example="123e4567-e89b-12d3-a456-426614174000"
    )


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, example="Обновленное название")
    description: Optional[str] = Field(None, example="Обновленное описание")
    status: Optional[TaskStatus] = Field(None)
    assignee_id: Optional[UUID] = Field(None)


class TaskRead(TaskBase):
    id: UUID
    status: TaskStatus
    assignee_id: Optional[UUID]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
