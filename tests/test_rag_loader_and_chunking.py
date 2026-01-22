from app.rag.loaders import load_documents_from_folder
from app.rag.chunking import chunk_text, chunk_documents
from app.models.documents import Document


def test_chunk_text_basic():
    text = "A" * 1000
    chunks = chunk_text(text, chunk_size=400, overlap=80)
    assert len(chunks) >= 3
    assert all(len(c) <= 400 for c in chunks)


def test_chunk_text_overlap_rules():
    text = "Hello world " * 50
    chunks = chunk_text(text, chunk_size=100, overlap=20)
    assert len(chunks) > 1


def test_chunk_text_invalid_overlap():
    try:
        chunk_text("test", chunk_size=10, overlap=10)
        assert False, "Expected ValueError"
    except ValueError:
        assert True


def test_chunk_documents_metadata():
    docs = [Document(doc_id="d1", text="A" * 500, metadata={"source_file": "d1.txt"})]
    chunks = chunk_documents(docs, chunk_size=200, overlap=50)
    assert len(chunks) >= 3
    assert chunks[0].doc_id == "d1"
    assert "source_file" in chunks[0].metadata


def test_load_documents_from_folder():
    docs = load_documents_from_folder("data/docs")
    assert len(docs) >= 1
    assert all(d.text for d in docs)