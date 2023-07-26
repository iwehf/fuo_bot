from fastapi import APIRouter

from .user import router as UserRouter

router = APIRouter(prefix="/v1")

router.include_router(UserRouter)
