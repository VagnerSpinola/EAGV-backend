from fastapi import APIRouter

from app.api.routes.academy import router as academy_router
from app.api.routes.auth import router as auth_router
from app.api.routes.system_settings import router as system_settings_router


api_router = APIRouter()
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(academy_router, prefix="/academy", tags=["academy"])
api_router.include_router(system_settings_router, prefix="/system", tags=["system"])