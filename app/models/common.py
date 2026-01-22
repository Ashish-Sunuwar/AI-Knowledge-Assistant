from pydantic import BaseModel
from typing import Optional

class ResponseMeta(BaseModel):
    request_id: Optional[str]
    latency_ms: Optional[float] = None
    model: Optional[str] = None
    tokens_used: Optional[int] = None

class ApiResponse(BaseModel):
    success: bool
    data: Optional[dict] = None
    error: Optional[str] = None
    meta: ResponseMeta



