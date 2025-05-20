from core.interfaceRepositories.task_irepository import ITaskRepository
from core.entites.core_entities import Task, TaskStatus
from infrastructure.models.project_task_model import Task as TaskModel

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from uuid import UUID
from typing import Any, Dict, List, Optional


class TaskRepository(ITaskRepository):
    """Репозиторий для работы с задачами в базе данных."""

    def __init__(self, session: AsyncSession):
        """Инициализация репозитория с сессией базы данных."""
        self._session = session

    @staticmethod
    def _map_to_entity(model: TaskModel) -> Task:
        """Преобразовать модель базы данных в сущность."""
        return Task(
            id=UUID(str(model.id)),
            project_id=UUID(str(model.project_id)),
            title=model.title,
            description=model.description,
            status=model.status,
            assignee_id=UUID(str(model.assignee_id)) if model.assignee_id else None,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    @staticmethod
    def _map_to_model(entity: Task) -> TaskModel:
        """Преобразовать сущность в модель базы данных."""
        return TaskModel(
            id=entity.id,
            project_id=entity.project_id,
            title=entity.title,
            description=entity.description,
            status=entity.status,
            assignee_id=entity.assignee_id,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    async def create_task(self, task: Task) -> Task:
        """Создать новую задачу.
        :param task: Объект задачи.
        :return: Созданный объект задачи.
        """
        task_model = self._map_to_model(task)
        self._session.add(task_model)
        await self._session.commit()
        await self._session.refresh(task_model)
        return self._map_to_entity(task_model)

    async def get_task(self, task_id: UUID) -> Optional[Task]:
        """Получить задачу по ID.
        :param task_id: ID задачи.
        :return: Объект задачи или None, если не найден.
        """
        result = await self._session.execute(
            select(TaskModel).where(TaskModel.id == task_id)
        )
        task_model = result.scalars().first()
        return self._map_to_entity(task_model) if task_model else None

    async def update_task(
        self, task_id: UUID, update_data: Dict[str, Any]
    ) -> Optional[Task]:
        """Обновить задачу по ID с частичными данными.
        :param task_id: ID задачи.
        :param update_data: Словарь с обновляемыми данными.
        :return: Объект задачи или None, если не найден.
        """
        stmt = (
            update(TaskModel)
            .where(TaskModel.id == task_id)
            .values(**update_data)
            .execution_options(synchronize_session="fetch")
        )
        result = await self._session.execute(stmt)
        await self._session.commit()

        if result.rowcount == 0:
            return None

        return await self.get_task(task_id)

    async def delete_task(self, task_id: UUID) -> None:
        """Удалить задачу по ID.
        :param task_id: ID задачи.
        """
        stmt = delete(TaskModel).where(TaskModel.id == task_id)
        await self._session.execute(stmt)
        await self._session.commit()

    async def list_tasks(
        self,
        project_id: UUID,
        status: Optional[TaskStatus] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        order_by: Optional[str] = None,
    ) -> List[Task]:
        """Список задач по проекту (с фильтрацией и пагинацией).
        :param project_id: ID проекта.
        :param status: Фильтр по статусу (опционально).
        :param limit: Максимальное количество задач.
        :param offset: Смещение.
        :param order_by: Поле для сортировки (например, "created_at", "status").
        :return: Список объектов Task.
        """
        query = select(TaskModel).where(TaskModel.project_id == project_id)

        if status:
            query = query.where(TaskModel.status == status)

        if order_by:
            query = query.order_by(getattr(TaskModel, order_by))

        if limit:
            query = query.limit(limit)

        if offset:
            query = query.offset(offset)

        result = await self._session.execute(query)
        task_models = result.scalars().all()

        return [self._map_to_entity(task_model) for task_model in task_models]
