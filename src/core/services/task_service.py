from typing import List, Optional, Dict, Any
from uuid import UUID
from core.entites.core_entities import Task, TaskStatus
from core.entites.core_events import (
    TaskCreatedEvent,
    TaskStatusChangedEvent,
    TaskDeletedEvent,
)
from core.interfaceRepositories.task_irepository import ITaskRepository

from core.interfaceRepositories import IProjectRepository
from core.interfaceRepositories.event_ipublisher import IEventPublisher
from datetime import datetime


class TaskService:
    """Сервис для управления задачами."""

    def __init__(
        self,
        task_repo: ITaskRepository,
        project_repo: IProjectRepository,
        event_publisher: IEventPublisher,
    ):
        """Инициализация сервиса с зависимостями."""
        self._task_repo: ITaskRepository = task_repo
        self._project_repo: IProjectRepository = project_repo
        self._event_publisher: IEventPublisher = event_publisher

    async def create_task(
        self,
        project_id: UUID,
        title: str,
        description: Optional[str] = None,
        status: TaskStatus = TaskStatus.TODO,
        assignee_id: Optional[UUID] = None,
    ) -> Task:
        """
        Создать новую задачу в проекте.

        :param project_id: ID проекта, к которому относится задача.
        :param title: Заголовок задачи.
        :param description: Описание задачи (опционально).
        :param status: Начальный статус задачи (по умолчанию TODO).
        :param assignee_id: ID назначенного пользователя (опционально).
        :return: Созданный объект Task.
        """
        project = await self._project_repo.get_project(project_id)
        if not project:
            raise ValueError(f"Project with ID {project_id} not found")

        new_task_data = Task(
            project_id=project_id,
            title=title,
            description=description,
            status=status,
            assignee_id=assignee_id,
        )

        task = await self._task_repo.create_task(new_task_data)

        event = TaskCreatedEvent(
            task_id=task.id,
            project_id=task.project_id,
            title=task.title,
            status=task.status,
            timestamp=datetime.utcnow(),
        )
        await self._event_publisher.publish_event(event, topic="task_events")

        return task

    async def get_task(self, task_id: UUID) -> Optional[Task]:
        """
        Получить задачу по ID.

        :param task_id: ID задачи.
        :return: Объект Task или None, если не найден.
        """
        return await self._task_repo.get_task(task_id)

    async def list_tasks_by_project(
        self,
        project_id: UUID,
        status: Optional[TaskStatus] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        order_by: Optional[str] = None,
    ) -> List[Task]:
        """
        Список задач по проекту (с опциональной фильтрацией, пагинацией и сортировкой).

        :param project_id: ID проекта.
        :param status: Фильтр по статусу (опционально).
        :param limit: Максимальное количество задач.
        :param offset: Смещение.
        :param order_by: Поле для сортировки (например, "created_at", "status").
        :return: Список объектов Task.
        """
        return await self._task_repo.list_tasks(
            project_id=project_id,
            status=status,
            limit=limit,
            offset=offset,
            order_by=order_by,
        )

    async def update_task(
        self, task_id: UUID, update_data: Dict[str, Any]
    ) -> Optional[Task]:
        """
        Обновить задачу по ID с частичными данными.

        Этот метод обрабатывает общие обновления, но для смены статуса лучше использовать change_task_status.

        :param task_id: ID задачи.
        :param update_data: Словарь с данными для обновления (например, {"description": "New description"}).
        :return: Обновленный объект Task или None, если задача не найдена.
        """
        # TODO: Добавить логику валидации update_data
        # TODO: Добавить проверку прав пользователя на редактирование задачи

        # Получаем текущее состояние для сравнения, если это нужно для определения события
        current_task = await self._task_repo.get_task(task_id)
        if not current_task:
            return None

        # Обновляем в БД
        updated_task = await self._task_repo.update_task(task_id, update_data)

        if updated_task:
            # TODO: Определить, какие поля изменились, и публиковать TaskUpdatedEvent, если нужно
            # Например:
            # changed_fields = {k: v for k, v in update_data.items() if getattr(current_task, k, None) != v}
            # if changed_fields:
            #    event = TaskUpdatedEvent(...) # Создать TaskUpdatedEvent
            #    await self._event_publisher.publish(event, topic="task_events")
            pass  # Пока не публикуем общий TaskUpdatedEvent для простоты

        return updated_task

    async def change_task_status(
        self, task_id: UUID, new_status: TaskStatus
    ) -> Optional[Task]:
        """
        Изменить статус задачи.

        Это специфическая операция обновления, которая гарантированно публикует событие.

        :param task_id: ID задачи.
        :param new_status: Новый статус задачи.
        :return: Обновленный объект Task или None, если задача не найдена.
        :raises ValueError: Если статус переход недопустим.
        """

        task = await self._task_repo.get_task(task_id)
        if not task:
            raise ValueError(f"Task with ID {task_id} not found")

        old_status = task.status
        if old_status == new_status:
            return task

        updated_task = await self._task_repo.update_task(
            task_id, {"status": new_status}
        )

        if updated_task:
            event = TaskStatusChangedEvent(
                project_id=updated_task.project_id,
                old_status=old_status,
                new_status=updated_task.status,
                timestamp=datetime.utcnow(),
                # TODO: Добавить user_id, который выполнил действие
            )
            await self._event_publisher.publish_event(event, topic="task_events")

        return updated_task

    async def delete_task(self, task_id: UUID) -> None:
        """
        Удалить задачу по ID.

        :param task_id: ID задачи.
        """
        # TODO: Добавить проверку прав пользователя на удаление задачи
        # TODO: Возможно, сначала получить задачу, чтобы получить project_id для события

        task_to_delete = await self._task_repo.get_task(task_id)
        if not task_to_delete:
            raise ValueError(f"Task with ID {task_id} not found")

        await self._task_repo.delete_task(task_id)

        event = TaskDeletedEvent(
            task_id=task_to_delete.uuid,
            project_id=task_to_delete.project_id,
            timestamp=datetime.utcnow(),
        )
        await self._event_publisher.publish_event(event, topic="task_events")

        # TODO: Возможно, потребуется дополнительная логика в потребителе для обработки удаления связанных комментариев и кэша
