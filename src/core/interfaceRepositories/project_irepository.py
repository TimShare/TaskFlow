from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from uuid import UUID
from core.entites.core_entities import Project


class IProjectRepository(ABC):
    """Интерфейс репозитория проектов."""

    @abstractmethod
    async def create_project(self, project: Project) -> Project:
        """Создать проект.
        :param project: Объект проекта.
        :return: Созданный объект проекта."""
        pass

    @abstractmethod
    async def get_project(self, project_id: UUID) -> Optional[Project]:
        """Получить проект по ID.
        :param project_id: ID проекта.
        :return: Объект проекта или None, если не найден.
        """
        pass

    @abstractmethod
    async def update_project(
        self, project_id: UUID, update_data: Dict[str, Any]
    ) -> Optional[Project]:
        """Обновить проект по ID с частичными данными.
        :param project_id: ID проекта.
        :param update_data: Словарь с обновляемыми данными.
        :return: Объект проекта или None, если не найден.
        """
        pass

    @abstractmethod
    async def delete_project(self, project_id: UUID) -> None:
        """Удалить проект по ID.
        :param project_id: ID проекта.
        :return: None.
        """
        pass

    @abstractmethod
    async def list_projects(
        self, limit: Optional[int] = None, offset: Optional[int] = None
    ) -> List[Project]:
        """Список проектов (с опциональной пагинацией).
        :param limit: Максимальное количество проектов.
        :param offset: Смещение для пагинации.
        :return: Список объектов проектов.
        """
        pass

    @abstractmethod
    async def get_project_by_filter(self, filters: Dict[str, Any]) -> Optional[Project]:
        """
        Получить проект по фильтру.
        :param filters: Словарь вида {"id": 123} или {"name": "абв"}
        :return: Объект проекта или None, если не найден.
        """
        pass
