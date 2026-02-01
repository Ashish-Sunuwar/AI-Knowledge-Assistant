import os
from fastapi import Security, HTTPException, status
from fastapi.security.api_key import APIKeyHeader

API_KEY_HEADER = APIKeyHeader(name="X-API-Key", auto_error=False)

def _truthy(value: str | None) -> bool:
    return (value or "").strip().lower() in {"1", "true", "yes", "y", "on"}

def require_api_key(api_key: str = Security(API_KEY_HEADER)) -> str:
    """
    Enforce API key only when REQUIRE_API_KEY=true.
    Read env at runtime so tests that monkeypatch env vars work.
    """
    require = _truthy(os.getenv("REQUIRE_API_KEY"))
    if not require:
        return "auth-disabled"

    expected = os.getenv("API_KEY")

    if not expected:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server API key is not configured",
        )

    if not api_key or api_key != expected:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key",
        )

    return api_key