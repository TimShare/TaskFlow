from uuid import UUID
from typing import List, Optional
from fastapi import APIRouter, Depends, status, HTTPException
from interface.schemas.task_schema import TaskCreate, TaskRead, TaskUpdate
from interface.dependencies import get_task_service, get_project_service
from core.services.task_service import TaskService
from core.entites.core_entities import TaskStatus

router = APIRouter(
    prefix="/tasks",
    tags=["tasks"],
)


@router.post(
    "/",
    response_model=TaskRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_task(
    task: TaskCreate,
    task_service: TaskService = Depends(get_task_service),
) -> TaskRead:
    """Создание новой задачи."""
    try:
        created = await task_service.create_task(
            project_id=task.project_id,
            title=task.title,
            description=task.description,
            status=task.status,
            assignee_id=task.assignee_id,
        )
        return created
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "/{task_id}",
    response_model=TaskRead,
    status_code=status.HTTP_200_OK,
)
async def get_task(
    task_id: UUID,
    task_service: TaskService = Depends(get_task_service),
) -> TaskRead:
    """Получение задачи по ID."""
    found = await task_service.get_task(task_id)
    if not found:
        raise HTTPException(status_code=404, detail="Task not found")
    return found


@router.get(
    "/",
    response_model=List[TaskRead],
    status_code=status.HTTP_200_OK,
)
async def list_tasks(
    project_id: UUID,
    status: Optional[TaskStatus] = None,
    limit: Optional[int] = None,
    offset: Optional[int] = None,
    order_by: Optional[str] = None,
    task_service: TaskService = Depends(get_task_service),
) -> List[TaskRead]:
    """Список задач с фильтрацией и пагинацией."""
    return await task_service.list_tasks_by_project(
        project_id=project_id,
        status=status,
        limit=limit,
        offset=offset,
        order_by=order_by,
    )


@router.put(
    "/{task_id}",
    response_model=TaskRead,
    status_code=status.HTTP_200_OK,
)
async def update_task(
    task_id: UUID,
    task_update: TaskUpdate,
    task_service: TaskService = Depends(get_task_service),
) -> TaskRead:
    """Обновление задачи по ID."""
    updated = await task_service.update_task(
        task_id=task_id,
        update_data=task_update.model_dump(exclude_unset=True),
    )
    if not updated:
        raise HTTPException(status_code=404, detail="Task not found")
    return updated


@router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_task(
    task_id: UUID,
    task_service: TaskService = Depends(get_task_service),
) -> None:
    """Удаление задачи по ID."""
    await task_service.delete_task(task_id)
