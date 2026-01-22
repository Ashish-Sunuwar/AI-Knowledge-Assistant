from app.rag.loaders import load_documents_from_folder
from app.rag.chunking import chunk_documents
from app.rag.retriever import Retriever

def build_retriever_from_folder(
        folder_path: str = "data/docs",
        chunk_size: int = 400,
        overlap: int = 80,
        dim: int = 256,
) -> Retriever:
    docs = load_documents_from_folder(folder_path)
    chunks = chunk_documents(docs, chunk_size=chunk_size, overlap=overlap)
    return Retriever.from_chunks(chunks, dim=dim)

