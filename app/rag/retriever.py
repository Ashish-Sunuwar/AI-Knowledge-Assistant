from typing import List

from app.models.documents import Chunk
from app.rag.embeddings import Embedder, HashingEmbedder
from app.rag.vector_store import FaissVectorStore, SearchResult

class Retriever:
    def __init__(self, embedder: Embedder, store: FaissVectorStore):
        self.embedder = embedder
        self.store = store

    @classmethod
    def from_chunks(cls, chunks: List[Chunk], dim: int = 256) -> "Retriever":
        embedder = HashingEmbedder(dim=dim)
        store = FaissVectorStore(dim=dim)
        
        vectors = embedder.embed_texts([c.text for c in chunks])
        store.add(vectors, chunks)
        return cls(embedder=embedder, store=store)
    
    def retrieve(self, query: str, k: int = 5) -> List[SearchResult]:
        qv = self.embedder.embed_query(query)
        return self.store.search(qv, k=k)
    