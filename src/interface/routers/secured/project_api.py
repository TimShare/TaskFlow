from uuid import UUID
from fastapi import APIRouter, Depends, status, HTTPException
from interface.schemas.project_schema import ProjectCreate, ProjectRead, ProjectUpdate
from interface.dependencies import get_project_service
from core.entites.core_entities import Project
from core.services.project_service import ProjectService


router = APIRouter(
    prefix="/projects",
    tags=["projects"],
)


@router.post(
    "/",
    response_model=ProjectRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_project(
    project: ProjectCreate,
    project_service: ProjectService = Depends(get_project_service),
) -> ProjectRead:
    """Создание нового проекта."""
    created_project = await project_service.create_project(
        name=project.name, description=project.description
    )
    return created_project


@router.get("/{project_id}", response_model=ProjectRead, status_code=status.HTTP_200_OK)
async def get_project(
    project_id: UUID,
    project_service: ProjectService = Depends(get_project_service),
) -> ProjectRead:
    """Получение проекта по ID."""
    project = await project_service.get_project(project_id)
    return project


@router.get("/", response_model=list[ProjectRead], status_code=status.HTTP_200_OK)
async def get_all_projects(
    project_service: ProjectService = Depends(get_project_service),
) -> list[ProjectRead]:
    """Получение всех проектов."""
    projects = await project_service.list_projects()
    return projects


@router.put(
    "/{project_id}",
    response_model=ProjectRead,
    status_code=status.HTTP_200_OK,
)
async def update_project(
    project_id: UUID,
    project_update: ProjectUpdate,
    project_service: ProjectService = Depends(get_project_service),
) -> ProjectRead:
    """Обновление проекта по ID."""
    updated_project = await project_service.update_project(
        project_id=project_id, update_data=project_update.model_dump(exclude_unset=True)
    )
    return updated_project


@router.delete(
    "/{project_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_project(
    project_id: UUID,
    project_service: ProjectService = Depends(get_project_service),
) -> None:
    """Удаление проекта по ID."""
    return await project_service.delete_project(project_id)
