from fastapi import APIRouter
from app.core.metrics import STORE

router = APIRouter(prefix="/metrics", tags=["metrics"])


@router.get("")
def get_metrics():
    items = [m.__dict__ for m in STORE.list()]
    return {"count": len(items), "items": items}


@router.get("/summary")
def get_metrics_summary():
    return STORE.summary()