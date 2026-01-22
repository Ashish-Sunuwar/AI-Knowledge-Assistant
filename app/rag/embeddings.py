import hashlib
import numpy as np
from typing import List

class Embedder:

    def embed_texts(self, texts: List[str]) -> np.ndarray:
        raise NotImplementedError

    def embed_query(self, text: str) -> np.ndarray:
        return self.embed_texts([text])[0]
    
class HashingEmbedder(Embedder):
    def __init__(self, dim: int = 256):
        self.dim = dim
    
    def _hash_to_vec(self, text: str) -> np.ndarray:
        vec = np.zeros(self.dim, dtype=np.float32)

        #simple tokenization
        tokens = text.lower().split()
        for tok in tokens:
            h = hashlib.md5(tok.encode("utf-8")).hexdigest()
            idx = int(h,16) % self.dim
            vec[idx] += 1.0

        #normalize
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec /= norm
        return vec
    
    def embed_texts(self, texts: List[str]) -> np.ndarray:
        return np.stack([self._hash_to_vec(t) for t in texts], axis=0).astype(np.float32)