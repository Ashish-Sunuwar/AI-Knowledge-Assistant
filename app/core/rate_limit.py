import os
import time
from collections import deque
from threading import Lock
from fastapi import Request, HTTPException
from app.core.config import settings

class RateLimiter:
    def __init__(self, max_requests: int, window_seconds: int):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._events = {}
        self._lock = Lock()

    def check(self, key: str) -> None:
        now = time.time()
        with self._lock:
            q = self._events.get(key)
            if q is None:
                q = deque()
                self._events[key] = q

            # drop old
            while q and (now - q[0]) > self.window_seconds:
                q.popleft()

            if len(q) >= self.max_requests:
                raise HTTPException(status_code=429, detail="Rate limit exceeded")

            q.append(now)

# global limiter: 30 requests/min per key
LIMITER = RateLimiter(max_requests=30, window_seconds=60)

def rate_limit_dependency(request: Request):
    # Disable rate limiting during tests or local dev if configured
    if settings.disable_rate_limit:
        return
    # prefer API key if present; else fall back to client IP
    api_key = request.headers.get("X-API-Key")
    client_ip = request.client.host if request.client else "unknown"
    key = api_key or client_ip
    LIMITER.check(key)