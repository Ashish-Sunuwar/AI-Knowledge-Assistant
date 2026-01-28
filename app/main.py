from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError


from app.api.v1.router import api_router
from app.core.config import settings
from app.core.logging import configure_logging, request_logging_middleware
from app.core.errors import validation_exception_handler

def create_app() -> FastAPI:
    configure_logging(settings.log_level)

    app = FastAPI(
        title=settings.app_name,
        version="1.0.0",
        description="RAG-based AI system with guardrails and testing"
    )

    # Middleware: request logs + request id
    app.middleware("http")(request_logging_middleware)

    app.add_exception_handler(
        RequestValidationError, validation_exception_handler
    )
    # Health stays simple (non-versioned is fine)
    @app.get("/health")
    async def health_check():
        return {"status": "ok"}
    
    # Versioned API
    app.include_router(api_router, prefix="/api/v1")
    
    return app
app = create_app()
