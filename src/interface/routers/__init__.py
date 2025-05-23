from fastapi import APIRouter
from interface.routers.public import router as public_router
from interface.routers.secured import router as secured_router

router = APIRouter()
router.include_router(public_router)
router.include_router(secured_router)
