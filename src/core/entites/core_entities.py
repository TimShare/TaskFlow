from uuid import uuid4, UUID
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional
from core.entites.base_entity import BaseEntity


class TaskStatus(str, Enum):
    """Enum для статусов задач."""

    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    CLOSED = "closed"


@dataclass(kw_only=True)
class Project(BaseEntity):
    """Сущность Проект."""

    name: str
    description: Optional[str] = None


@dataclass(kw_only=True)
class Task(BaseEntity):
    """Сущность Задача."""

    project_id: UUID
    title: str
    description: Optional[str] = None
    status: TaskStatus = TaskStatus.TODO
    assignee_id: Optional[UUID] = None
