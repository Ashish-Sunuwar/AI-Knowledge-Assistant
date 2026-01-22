from dataclasses import dataclass
from typing import List, Tuple

import numpy as np
import faiss # type: ignore

from app.models.documents import Chunk

@dataclass
class SearchResult:
    chunk: Chunk
    score: float # higer = more similar

class FaissVectorStore:
    """In-memory FAISS index (cosine similarity via product on normalized vectors)"""

    def __init__(self, dim: int):
        self.dim = dim
        self.index = faiss.IndexFlatIP(dim)
        self._chunks: List[Chunk] = []

    @staticmethod
    def _normalize(vectors: np.ndarray) -> np.ndarray:
        norms = np.linalg.norm(vectors, axis=1, keepdims=True)
        norms[norms == 0] =1.0
        return vectors / norms
    
    def add(self, vectors: np.ndarray, chunks: List[Chunk]) -> None:
        if vectors.ndim != 2 or vectors.shape[1] != self.dim:
            raise ValueError(f"vectors must be shape (n, {self.dim})")
        if len(chunks) != vectors.shape[0]:
            raise ValueError("chunks length must match vectors rows")
        
        vectors = vectors.astype(np.float32)
        vectors = self._normalize(vectors)

        self.index.add(vectors)
        self._chunks.extend(chunks)

    def search(self, query_vector: np.ndarray, k: int = 5) -> List[SearchResult]:
        if k <= 0:
            return []
        q = query_vector.astype(np.float32).reshape(1, -1)
        q = self._normalize(q)

        scores, idxs = self.index.search(q, k)
        results: List[SearchResult] = []
        
        for score, idx in zip(scores[0].tolist(), idxs[0].tolist()):
            if idx == -1:
                continue

            results.append(SearchResult(chunk=self._chunks[idx], score = float(score)))

        return results
