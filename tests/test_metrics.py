from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_metrics_summary_endpoint():
    # hit ask to generate some metrics
    client.post("/api/v1/ask", json={"question": "What is the password expiry policy?"})

    res = client.get("/api/v1/metrics/summary")
    assert res.status_code == 200
    body = res.json()

    assert "count" in body
    assert "avg_latency_ms" in body
    assert "avg_tokens" in body