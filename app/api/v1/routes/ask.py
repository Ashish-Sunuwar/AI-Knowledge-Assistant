from fastapi import APIRouter, Request, Depends

from app.models.ask import QuestionRequest, AnswerData
from app.models.common import ApiResponse, ResponseMeta
from app.services.ask_service import AskService
from app.services.dependencies import get_ask_service
from app.core.metrics import STORE, RequestMetrics
import time
from app.core.rate_limit import rate_limit_dependency


router = APIRouter(tags=["ask"])


@router.post("/ask", response_model=ApiResponse, dependencies=[Depends(rate_limit_dependency)],)
async def ask(
    request: Request,
    payload: QuestionRequest,
    service: AskService = Depends(get_ask_service),
):
    result = await service.answer(payload.question)

    meta = ResponseMeta(
        request_id=getattr(request.state, "request_id", None),
        latency_ms=result.latency_ms,
        model=result.model,
        tokens_used=result.tokens_used,
    )

    data = AnswerData(
        answer=result.answer,
        confidence=result.confidence,
        sources=result.sources or [],
        used_sources=result.used_sources or [],
    )

    req_id = getattr(request.state, "request_id", None)

    STORE.add(
        RequestMetrics(
            ts=time.time(),
            request_id=req_id,
            path=str(request.url.path),
            method=request.method,
            status_code=200,
            latency_ms=meta.latency_ms,
            model=meta.model,
            tokens_used=meta.tokens_used,
            retrieved_k=len(result.sources or []),
            sources_returned=len(result.sources or []),
            confidence=result.confidence,
            answered=(result.answer != "I don't know."),
        )
    )
    return ApiResponse(
        success=True,
        data=data.model_dump(),
        meta=meta,
    )