from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_answer_with_sources_must_cite_sources():
    res = client.post("/api/v1/ask", json={"question": "What is the password expiry policy?"})
    assert res.status_code == 200
    body = res.json()

    answer = body["data"]["answer"]
    sources = body["data"].get("sources", [])
    used_sources = body["data"].get("used_sources", [])

    if answer != "I don't know.":
        assert len(sources) >= 1
        assert len(used_sources) >= 1
        valid_chunk_ids = {s["chunk_id"] for s in sources}
        assert all(u in valid_chunk_ids for u in used_sources)

def test_idk_has_no_used_sources():
    res = client.post("/api/v1/ask", json={"question": "quantum banana spaceship policy"})
    assert res.status_code == 200
    body = res.json()

    assert body["data"]["answer"] == "I don't know."
    assert body["data"].get("used_sources", []) == []