from fastapi import APIRouter

from app.api.v1.routes.ask import router as ask_router
from app.api.v1.routes.metrics import router as metrics_router

api_router = APIRouter()
api_router.include_router(ask_router)
api_router.include_router(metrics_router)