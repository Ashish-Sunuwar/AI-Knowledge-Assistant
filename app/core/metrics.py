from __future__ import annotations

from dataclasses import dataclass, field
from threading import Lock
from typing import Optional, Dict, Any, List
import time


@dataclass
class RequestMetrics:
    ts: float
    request_id: Optional[str]
    path: str
    method: str
    status_code: int

    latency_ms: Optional[float] = None
    model: Optional[str] = None
    tokens_used: Optional[int] = None

    # RAG-specific
    retrieved_k: Optional[int] = None
    sources_returned: Optional[int] = None
    confidence: Optional[float] = None
    answered: Optional[bool] = None   # True if not "I don't know."


class MetricsStore:
    """
    Simple in-memory ring buffer for recent request metrics.
    """
    def __init__(self, max_items: int = 500):
        self.max_items = max_items
        self._items: List[RequestMetrics] = []
        self._lock = Lock()

    def add(self, m: RequestMetrics) -> None:
        with self._lock:
            self._items.append(m)
            if len(self._items) > self.max_items:
                self._items = self._items[-self.max_items:]

    def list(self) -> List[RequestMetrics]:
        with self._lock:
            return list(self._items)

    def summary(self) -> Dict[str, Any]:
        items = self.list()
        if not items:
            return {
                "count": 0,
                "avg_latency_ms": None,
                "avg_tokens": None,
                "answered_rate": None,
            }

        latencies = [x.latency_ms for x in items if x.latency_ms is not None]
        tokens = [x.tokens_used for x in items if x.tokens_used is not None]
        answered = [x.answered for x in items if x.answered is not None]

        def avg(vals):
            return (sum(vals) / len(vals)) if vals else None

        answered_rate = None
        if answered:
            answered_rate = sum(1 for a in answered if a) / len(answered)

        return {
            "count": len(items),
            "avg_latency_ms": avg(latencies),
            "avg_tokens": avg(tokens),
            "answered_rate": answered_rate,
        }


# Global singleton store
STORE = MetricsStore(max_items=500)