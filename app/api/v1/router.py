from fastapi import APIRouter
from app.api.v1.routes.ask import router as ask_router

api_router = APIRouter()
api_router.include_router(ask_router, tags=["ask"])