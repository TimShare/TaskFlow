from interface.routers.public.auth_api import router as auth_router
from fastapi import APIRouter

router = APIRouter(prefix="/public")
router.include_router(auth_router)
