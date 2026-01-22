import time
from dataclasses import dataclass
from tracemalloc import start
from typing import List, Optional


from app import llm
from app.models.ask import SourceItem
from app.rag.index_builder import build_retriever_from_folder
from app.rag.vector_store import SearchResult

from app.llm.client import get_llm_client
from app.rag.prompting import build_prompt

@dataclass
class AskResult:
    answer: str
    confidence: float | None = None
    sources: list[str] | None = None
    latency_ms: float | None = None
    model: str | None = None
    tokens_used: int | None= None

def _preview(text: str, max_len: int = 180) -> str:
    text = text.replace("\n", " ").strip()
    return text[:max_len] + ("..." if len (text) > max_len else "")

def _confidence_from_score(score: List[float]) -> Optional[float]:
    """
    Simple heuristic:
    - if no scores: None
    - confidence = clamp(top_score, 0..1)
    FAISS IP on normalized vectors ~ cosine similarity, typically 0..1.
    """
    if not score:
        return None
    top = max(score)
    if top < 0:
        return 0.0
    return float(min(1.0, top))

_RETRIEVER = build_retriever_from_folder(
    folder_path="data/docs",
    chunk_size=300,
    overlap=50,
    dim=256,
)

_MIN_SCORE = 0.05  # similarity threshold; tune as needed

class AskService:

    def answer(self, question: str, k: int = 3) -> AskResult:
        start = time.perf_counter()

        results: List[SearchResult] = _RETRIEVER.retrieve(question, k=k)

        sources: List[SourceItem] = []
        scores: List[float] = []

        for r in results:
            if r.score < _MIN_SCORE:
                continue  # ignore weak matches
            scores.append(r.score)
            sources.append(
            SourceItem(
                    chunk_id=r.chunk.chunk_id,
                    source_file=r.chunk.metadata.get("source_file"),
                    score=r.score,
                    preview=_preview(r.chunk.text),
                )
            )


        confidence = _confidence_from_score(scores)

        # EARLY EXIT: no grounded sources -> do NOT call LLM
        if not sources:
            latency_ms = (time.perf_counter() - start) * 1000
            return AskResult(
                answer="I don't know.",
                confidence=None,
                sources=[],
                latency_ms=latency_ms,
                model="rag-retrieval-only",
                tokens_used=0,
            )

        llm = get_llm_client()
        prompt = build_prompt(question, sources)
        llm_result = llm.generate(prompt)

        answer = (llm_result.text or "").strip()

        # Guardrails (VERY important)
        if not sources:
            answer = "I don't know."

        if not answer:
            answer = "I don't know."


        latency_ms = (time.perf_counter() - start) * 1000

        return AskResult(
            answer=answer,
            confidence=confidence,
            sources=sources,
            latency_ms=latency_ms,
            model=llm_result.model,
            tokens_used=llm_result.tokens_used or 0,
        )
    

