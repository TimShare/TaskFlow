from core.interfaceRepositories.project_irepository import IProjectRepository
from core.entites.core_entities import Project, TaskStatus
from infrastructure.models.project_task_model import Project as ProjectModel

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from uuid import UUID
from typing import Any, Dict, List, Optional


class ProjectRepository(IProjectRepository):
    """Репозиторий для работы с проектами в базе данных."""

    def __init__(self, session: AsyncSession):
        """Инициализация репозитория с сессией базы данных."""
        self._session = session

    @staticmethod
    def _map_to_entity(model: ProjectModel) -> Project:
        """Преобразовать модель базы данных в сущность."""
        return Project(
            id=UUID(str(model.id)),
            name=model.name,
            description=model.description,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    @staticmethod
    def _map_to_model(entity: Project) -> ProjectModel:
        """Преобразовать сущность в модель базы данных."""
        return ProjectModel(
            id=entity.id,
            name=entity.name,
            description=entity.description,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    async def create_project(self, project: Project) -> Project:
        """Создать новый проект.
        :param project: Объект проекта.
        :return: Созданный объект проекта.
        """

        project_model = self._map_to_model(project)
        self._session.add(project_model)
        await self._session.commit()
        await self._session.refresh(project_model)
        return self._map_to_entity(project_model)

    async def get_project(self, project_id: UUID) -> Optional[Project]:
        """Получить проект по ID.
        :param project_id: ID проекта.
        :return: Объект проекта или None, если не найден.
        """
        result = await self._session.execute(
            select(ProjectModel).where(ProjectModel.id == project_id)
        )
        project_model = result.scalars().first()
        return self._map_to_entity(project_model) if project_model else None

    async def update_project(
        self, project_id: UUID, update_data: dict
    ) -> Optional[Project]:
        """Обновить проект по ID с частичными данными.
        :param project_id: ID проекта.
        :param update_data: Словарь с обновляемыми данными.
        :return: Объект проекта или None, если не найден.
        """
        stmt = (
            update(ProjectModel)
            .where(ProjectModel.id == project_id)
            .values(**update_data)
            .execution_options(synchronize_session="fetch")
        )
        result = await self._session.execute(stmt)
        await self._session.commit()
        return await self.get_project(project_id) if result.rowcount > 0 else None

    async def delete_project(self, project_id: UUID) -> bool:
        """Удалить проект по ID.
        :param project_id: ID проекта.
        :return: True, если проект удален, иначе False.
        """
        stmt = delete(ProjectModel).where(ProjectModel.id == project_id)
        result = await self._session.execute(stmt)
        await self._session.commit()
        return result.rowcount > 0

    async def list_projects(
        self, limit: Optional[int] = None, offset: Optional[int] = None
    ) -> List[Project]:
        """Получить список всех проектов с опциональной пагинацией.
        :param limit: Максимальное количество проектов.
        :param offset: Смещение для пагинации.
        :return: Список объектов проектов.
        """
        stmt = select(ProjectModel)
        if limit is not None:
            stmt = stmt.limit(limit)
        if offset is not None:
            stmt = stmt.offset(offset)
        result = await self._session.execute(stmt)
        return [self._map_to_entity(project) for project in result.scalars().all()]

    async def get_project_by_filter(self, filters: Dict[str, Any]) -> Optional[Project]:
        """
        Получить проект по фильтру.
        :param filters: Словарь вида {"id": ..., "name": ...}
        :return: Объект Project или None, если не найден.
        """
        stmt = select(ProjectModel)
        for field, value in filters.items():
            stmt = stmt.where(getattr(ProjectModel, field) == value)
        result = await self._session.execute(stmt)
        project_model = result.scalars().first()
        return self._map_to_entity(project_model) if project_model else None
