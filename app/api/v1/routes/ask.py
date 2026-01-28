from fastapi import APIRouter, Request, Depends

from app.models.ask import QuestionRequest, AnswerData
from app.models.common import ApiResponse, ResponseMeta
from app.services.ask_service import AskService
from app.services.dependencies import get_ask_service

router = APIRouter(prefix="/api/v1")


@router.post("/ask", response_model=ApiResponse)
async def ask(
    request: Request,
    payload: QuestionRequest,
    service: AskService = Depends(get_ask_service),
):
    result = service.answer(payload.question)

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

    return ApiResponse(
        success=True,
        data=data.model_dump(),
        meta=meta,
    )