from core.services.project_service import ProjectService
from infrastructure.postgres_db import database
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from infrastructure.repositories.project_repository import ProjectRepository
from infrastructure.event_publisher_singleton import event_publisher

from infrastructure.repositories.task_repository import TaskRepository
from core.services.task_service import TaskService
from infrastructure.repositories.auth_repository import (
    UserRepository,
    RefreshTokenRepository,
)
from core.services.auth_service import AuthService


async def get_project_service(
    session: AsyncSession = Depends(database.get_db_session),
) -> ProjectService:
    """Создание экземпляра сервиса проекта с зависимостями."""

    project_repo = ProjectRepository(session)
    return ProjectService(project_repo, event_publisher)


async def get_task_service(
    session: AsyncSession = Depends(database.get_db_session),
) -> TaskService:
    """Создание экземпляра сервиса задачи с зависимостями."""
    task_repo = TaskRepository(session)
    project_repo = ProjectRepository(session)
    return TaskService(task_repo, project_repo, event_publisher)


async def get_auth_service(
    session: AsyncSession = Depends(database.get_db_session),
) -> AuthService:
    """Создает AuthService с репозиториями пользователя и refresh-токена"""
    user_repo = UserRepository(session)
    refresh_repo = RefreshTokenRepository(session)
    return AuthService(user_repo, refresh_repo)
