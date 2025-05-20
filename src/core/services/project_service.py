from typing import List, Optional, Dict, Any
from uuid import UUID
from core.entites.core_entities import Project
from core.entites.core_events import (
    ProjectCreatedEvent,
    ProjectDeletedEvent,
    ProjectUpdatedEvent,
)
from core.interfaceRepositories.project_irepository import IProjectRepository
from core.interfaceRepositories.event_ipublisher import IEventPublisher
from core.exceptions import NotFoundError, AlreadyExistsError, DuplicateEntryError
from datetime import datetime


class ProjectService:
    """Сервис для управления проектами."""

    def __init__(
        self, project_repo: IProjectRepository, event_publisher: IEventPublisher
    ):
        """Инициализация сервиса с зависимостями."""
        self._project_repo: IProjectRepository = project_repo
        self._event_publisher: IEventPublisher = event_publisher

    async def create_project(
        self, name: str, description: Optional[str] = None
    ) -> Project:
        """
        Создать новый проект.

        :param name: Название проекта.
        :param description: Описание проекта (опционально).
        :return: Созданный объект Project.
        """
        # TODO: Добавить логику валидации данных перед созданием
        existing_project = await self._project_repo.get_project_by_filter(
            filters={"name": name}
        )
        if existing_project:
            raise AlreadyExistsError(f"Project with name '{name}' already exists.")

        new_project_data = Project(name=name, description=description)

        project = await self._project_repo.create_project(new_project_data)

        event = ProjectCreatedEvent(
            project_id=project.id,
            name=project.name,
            timestamp=datetime.utcnow(),
        )

        # Выбираем топик для публикации. Можно использовать один общий или выделить для проектов.
        await self._event_publisher.publish_event(event, topic="task_events")

        return project

    async def get_project(self, project_id: UUID) -> Optional[Project]:
        """
        Получить проект по ID.

        :param project_id: ID проекта.
        :return: Объект Project или None, если не найден.
        """

        project = await self._project_repo.get_project(project_id)
        if not project:
            raise NotFoundError(f"Project with ID {project_id} not found.")
        return project

    async def list_projects(
        self, limit: Optional[int] = None, offset: Optional[int] = None
    ) -> List[Project]:
        """
        Список всех проектов (с опциональной пагинацией).

        :param limit: Максимальное количество проектов.
        :param offset: Смещение для пагинации.
        :return: Список объектов Project.
        """
        # TODO: Добавить фильтрацию по пользователю (например, только проекты, где пользователь участник/владелец)
        return await self._project_repo.list_projects(limit=limit, offset=offset)

    async def update_project(
        self, project_id: UUID, update_data: Dict[str, Any]
    ) -> Optional[Project]:
        """
        Обновить проект по ID с частичными данными.

        :param project_id: ID проекта.
        :param update_data: Словарь с данными для обновления (например, {"name": "New Name"}).
        :return: Обновленный объект Project или None, если проект не найден.
        """
        # Опционально: можно получить текущее состояние, если нужно сравнить или применить сложную логику
        # current_project = await self._project_repo.get_project(project_id)
        # if not current_project:
        #     return None
        # TODO: Если нужно публиковать ProjectUpdatedEvent, создать его здесь
        if update_data.get("id") is not None:
            raise DuplicateEntryError("ID cannot be updated.")
        if update_data.get("name") is not None:
            existing_project = await self._project_repo.get_project_by_filter(
                filters={"name": update_data["name"]}
            )
            if existing_project and existing_project.id != project_id:
                raise AlreadyExistsError(
                    f"Project with name '{update_data['name']}' already exists."
                )

        updated_project = await self._project_repo.update_project(
            project_id, update_data
        )

        event = ProjectUpdatedEvent(
            project_id=updated_project.id,
            name=updated_project.name,
        )
        await self._event_publisher.publish_event(event, topic="task_events")

        return updated_project

    async def delete_project(self, project_id: UUID) -> None:
        """
        Удалить проект по ID.

        :param project_id: ID проекта.
        """
        # TODO: Возможно, добавить проверку, что нет связанных задач
        project = await self._project_repo.get_project(project_id)
        if not project:
            raise NotFoundError(f"Project with ID {project_id} not found.")

        await self._project_repo.delete_project(project_id)

        event = ProjectDeletedEvent(project_id=project_id, timestamp=datetime.utcnow())
        await self._event_publisher.publish_event(event, topic="task_events")

        # TODO: Возможно, потребуется дополнительная логика в потребителе для обработки удаления связанных задач и кэша
