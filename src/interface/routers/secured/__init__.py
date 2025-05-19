from fastapi import APIRouter, Depends
from interface.routers.secured.project_api import router as project_router

router = APIRouter(prefix="/secured")
router.include_router(project_router)
