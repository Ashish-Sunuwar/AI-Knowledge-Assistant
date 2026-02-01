from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError


from app.api.v1.router import api_router
from app.core.config import settings
from app.core.logging import configure_logging, request_logging_middleware
from app.core.errors import validation_exception_handler
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware

from app.core.config import settings

def create_app() -> FastAPI:
    configure_logging(settings.log_level)

    app = FastAPI(
        title=settings.app_name,
        version="1.0.0",
        description="RAG-based AI system with guardrails and testing"
    )

    def _split_csv(value: str) -> list[str]:
        return [x.strip() for x in value.split(",") if x.strip()]

    # Trusted hosts (Host header protection)
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=_split_csv(settings.trusted_hosts),
    )

    # CORS (frontend calling your API)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=_split_csv(settings.cors_origins),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Middleware: request logs + request id
    app.middleware("http")(request_logging_middleware)

    app.add_exception_handler(
        RequestValidationError, validation_exception_handler
    )
    
    @app.get("/health")
    def health():
        return {
            "status": "ok",
            "app_name": settings.app_name,
            "environment": settings.environment,
        }
    
    # Versioned API
    app.include_router(api_router)
    
    return app
app = create_app()
