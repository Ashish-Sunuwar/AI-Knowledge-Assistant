from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_ask_success():
    res = client.post("/api/v1/ask", json={"question": "What is RAG?"})
    assert res.status_code == 200

    body = res.json()
    assert body["success"] is True
    assert "data" in body
    assert "meta" in body

    assert "answer" in body["data"]
    assert isinstance(body["data"]["answer"], str)
    assert len(body["data"]["answer"].strip()) > 0

def test_ask_validation_error():
    res = client.post("/api/v1/ask", json={"question": "hi"})
    assert res.status_code == 422

    body = res.json()
    assert body["success"] is False
    assert body["error"] == "Validation error"