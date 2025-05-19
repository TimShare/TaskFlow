from sqlalchemy import UUID, ForeignKey, Enum as SQLEnum, String
from infrastructure.models.base_model import BaseModelMixin
from infrastructure.postgres_db import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING, Optional
from uuid import UUID as PY_UUID
from core.entites.core_entities import TaskStatus


class Task(Base, BaseModelMixin):
    """Модель задачи."""

    __tablename__ = "tasks"

    project_id: Mapped[PY_UUID] = mapped_column(
        ForeignKey("projects.id"), nullable=False
    )

    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    status: Mapped[TaskStatus] = mapped_column(
        SQLEnum(TaskStatus, name="task_status_enum", create_type=False),
        nullable=False,
        default=TaskStatus.TODO,
    )

    assignee_id: Mapped[Optional[PY_UUID]] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )
    project: Mapped["Project"] = relationship(back_populates="tasks")


class Project(Base, BaseModelMixin):
    """Модель проекта."""

    __tablename__ = "projects"

    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    tasks: Mapped[list["Task"]] = relationship(
        back_populates="project", cascade="all, delete-orphan"
    )
