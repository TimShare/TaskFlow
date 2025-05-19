from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from uuid import UUID
from core.entites.core_entities import Task, TaskStatus


class ITaskRepository(ABC):
    """Интерфейс репозитория задач."""

    @abstractmethod
    async def create_task(self, task: Task) -> Task:
        """Создать задачу."""
        pass

    @abstractmethod
    async def get_task(self, task_id: UUID) -> Optional[Task]:
        """Получить задачу по ID."""
        pass

    @abstractmethod
    async def update_task(
        self, task_id: UUID, update_data: Dict[str, Any]
    ) -> Optional[Task]:
        """Обновить задачу по ID с частичными данными."""
        pass

    @abstractmethod
    async def delete_task(self, task_id: UUID) -> None:
        """Удалить задачу по ID."""
        pass

    @abstractmethod
    async def list_tasks(
        self,
        project_id: UUID,
        status: Optional[TaskStatus] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        order_by: Optional[str] = None,
    ) -> List[Task]:
        """Список задач по проекту (с фильтрацией и пагинацией)."""
        pass
