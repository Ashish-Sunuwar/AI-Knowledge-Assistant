import os
from fastapi import APIRouter
from app.core.config import settings

router = APIRouter(tags=["meta"])

@router.get("/version")
def version():
    return {
        "app_name": settings.app_name,
        "environment": settings.environment,
        "llm_provider": settings.llm_provider,
        "git_sha": os.getenv("GIT_SHA"),
    }