from fastapi import APIRouter

from app.api.v1.routes.ask import router as ask_router
from app.api.v1.routes.metrics import router as metrics_router
from app.api.v1.routes.version import router as version_router

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(ask_router)
api_router.include_router(metrics_router)
api_router.include_router(version_router)