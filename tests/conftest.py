import os

def pytest_configure():
    os.environ.setdefault("LLM_PROVIDER", "stub")
    os.environ.setdefault("RAG_MIN_SCORE", "0.12")