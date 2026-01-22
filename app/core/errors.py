from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from app.models.common import ApiResponse, ResponseMeta


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    # Use the correct header name
    request_id = getattr(request.state, "request_id", None)

    response = ApiResponse(
        success=False,
        error="Validation error",
        meta=ResponseMeta(request_id=request_id),
    )

    # JSONResponse expects keyword: content
    return JSONResponse(status_code=422, content=response.model_dump())