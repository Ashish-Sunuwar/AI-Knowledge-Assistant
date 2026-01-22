import logging
import sys
import time 
import uuid
from typing import Callable

from fastapi import Request, Response

def configure_logging(log_level: str = "INFO") -> None:
    """
    Basic, production-friendly logging setup.
    Keeps formatting consistent across the app.
    """
    level = getattr(logging, log_level.upper(), logging.INFO)

    root = logging.getLogger()
    root.setLevel(level)

    # prevent duplicate handlers in reload mode
    if root.handlers:
        return
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )
    handler.setFormatter(formatter)
    root.addHandler(handler)

async def request_logging_middleware(request: Request, call_next: Callable) -> Response:
    logger = logging.getLogger("app.request")

    request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
    request.state.request_id = request_id  # store for later use

    start = time.perf_counter()

    try:
        response: Response = await call_next(request)
    except Exception:
        duration_ms = (time.perf_counter() - start) * 1000
        logger.exception(
            f"request_id={request_id} method={request.method} path={request.url.path} "
            f"status=500 duration_ms={duration_ms:.2f}"
        )
        raise

    duration_ms = (time.perf_counter() - start) * 1000
    logger.info(
        f"request_id={request_id} method={request.method} path={request.url.path} "
        f"status={response.status_code} duration_ms={duration_ms:.2f}"
    )

    response.headers["X-Request-ID"] = request_id
    return response



