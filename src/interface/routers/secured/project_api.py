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
