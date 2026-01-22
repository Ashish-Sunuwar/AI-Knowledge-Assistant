from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_ask_returns_sources_for_relevant_query():
    res = client.post("/api/v1/ask", json={"question": "least privilege access approval"})
    assert res.status_code == 200
    body = res.json()

    assert body["success"] is True
    assert "data" in body

    sources = body["data"]["sources"]
    assert isinstance(sources, list)
    assert len(sources) >= 1

    # We expect the access policy to be one of the sources
    joined = " ".join([s["chunk_id"] for s in sources])
    assert "policy_access" in joined


def test_ask_returns_idk_when_no_sources():
    res = client.post("/api/v1/ask", json={"question": "quantum banana spaceship policy"})
    assert res.status_code == 200
    body = res.json()

    assert body["success"] is True
    assert "I don't know" in body["data"]["answer"]