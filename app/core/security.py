import os
from fastapi import Security, HTTPException
from fastapi.security.api_key import APIKeyHeader

API_KEY_HEADER = APIKeyHeader(name="X-API-Key", auto_error=False)

def require_api_key(api_key: str = Security(API_KEY_HEADER)) -> str:
    expected = os.getenv("API_KEY") # set in env for prod
    # if no API_KEY configured, allow all
    if not expected:
        return "dev-mode"
    
    if not api_key or api_key != expected:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")
    return api_key