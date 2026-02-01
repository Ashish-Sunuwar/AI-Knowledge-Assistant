from fastapi import APIRouter, Depends
from app.core.metrics import STORE
from app.core.security import require_api_key

router = APIRouter(prefix="/metrics", tags=["metrics"], dependencies=[Depends(require_api_key)],)


@router.get("", dependencies=[Depends(require_api_key)])
def get_metrics():
    items = [m.__dict__ for m in STORE.list()]
    return {"count": len(items), "items": items}

@router.get("/summary", dependencies=[Depends(require_api_key)])
def get_metrics_summary():
    return STORE.summary()