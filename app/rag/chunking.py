import re
from typing import List

from app.models.documents import Document, Chunk


def clean_text(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def chunk_text(
    text: str,
    chunk_size: int = 400,
    overlap: int = 80,
) -> List[str]:
    """
    Simple character-based chunking with overlap.
    - chunk_size: max characters per chunk
    - overlap: repeated characters between chunks
    """
    if chunk_size <= 0:
        raise ValueError("chunk_size must be > 0")
    if overlap < 0:
        raise ValueError("overlap must be >= 0")
    if overlap >= chunk_size:
        raise ValueError("overlap must be < chunk_size")

    text = clean_text(text)
    if not text:
        return []

    chunks: List[str] = []
    start = 0
    n = len(text)

    while start < n:
        end = min(start + chunk_size, n)
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)

        if end == n:
            break
        start = max(0, end - overlap)

    return chunks


def chunk_documents(
    docs: List[Document],
    chunk_size: int = 400,
    overlap: int = 80,
) -> List[Chunk]:
    all_chunks: List[Chunk] = []
    for doc in docs:
        pieces = chunk_text(doc.text, chunk_size=chunk_size, overlap=overlap)
        for i, piece in enumerate(pieces):
            all_chunks.append(
                Chunk(
                    doc_id=doc.doc_id,
                    chunk_id=f"{doc.doc_id}::chunk_{i}",
                    text=piece,
                    metadata={**doc.metadata, "chunk_index": str(i)},
                )
            )
    return all_chunks