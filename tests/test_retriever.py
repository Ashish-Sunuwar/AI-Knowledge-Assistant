from app.rag.index_builder import build_retriever_from_folder

def test_retriever_returns_results():
    retriever = build_retriever_from_folder(
        folder_path="data/docs",
        chunk_size = 300,
        overlap = 50,
        dim = 256,
    )
    results = retriever.retrieve("passwords expire", k=3)
    assert len(results) > 0

def test_retriever_finds_password_policy():
    retriever = build_retriever_from_folder(
        folder_path="data/docs",
        chunk_size=300,
        overlap=50,
        dim=256,  
    )
    results = retriever.retrieve("password expiration 90 days", k=3)

    # At least one chunk should mention passwords
    joined = " ".join([r.chunk.text.lower() for r in results])
    assert "password" in joined
