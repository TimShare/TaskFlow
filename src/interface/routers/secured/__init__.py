from fastapi import APIRouter, Depends
from interface.routers.secured.project_api import router as project_router
from interface.routers.secured.task_api import router as task_router

router = APIRouter(prefix="/secured")
router.include_router(project_router)
router.include_router(task_router)
