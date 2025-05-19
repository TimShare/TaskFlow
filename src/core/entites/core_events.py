from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from uuid import UUID


class TaskStatus(str, Enum):
    """Enum для статусов задач."""

    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    CLOSED = "closed"


@dataclass
class ProjectCreatedEvent:
    """Событие: Проект создан."""

    project_id: UUID
    name: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    event_type: str = "ProjectCreatedEvent"


@dataclass
class ProjectUpdatedEvent:
    """Событие: Проект обновлен."""

    project_id: UUID
    name: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    event_type: str = "ProjectUpdatedEvent"


@dataclass
class ProjectDeletedEvent:
    """Событие: Проект удален."""

    project_id: UUID
    timestamp: datetime = field(default_factory=datetime.utcnow)
    event_type: str = "ProjectDeletedEvent"


@dataclass
class TaskCreatedEvent:
    """Событие: Задача создана."""

    task_id: UUID
    project_id: UUID
    title: str
    status: TaskStatus
    timestamp: datetime = field(default_factory=datetime.utcnow)
    event_type: str = "TaskCreatedEvent"


@dataclass
class TaskStatusChangedEvent:
    """Событие: Статус задачи изменен."""

    task_id: UUID
    project_id: UUID
    old_status: TaskStatus
    new_status: TaskStatus
    timestamp: datetime = field(default_factory=datetime.utcnow)
    event_type: str = "TaskStatusChangedEvent"


@dataclass
class TaskUpdatedEvent:
    """Событие: Задача обновлена."""

    task_id: UUID
    project_id: UUID
    title: str
    status: TaskStatus
    timestamp: datetime = field(default_factory=datetime.utcnow)
    event_type: str = "TaskUpdatedEvent"


@dataclass
class TaskDeletedEvent:
    """Событие: Задача удалена."""

    task_id: UUID
    project_id: UUID
    timestamp: datetime = field(default_factory=datetime.utcnow)
    event_type: str = "TaskDeletedEvent"


# TODO: Добавить другие события по мере необходимости (TaskUpdated, CommentAdded и т.д.)
