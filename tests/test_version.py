from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_version_endpoint():
    res = client.get("/api/v1/version")
    assert res.status_code == 200
    body = res.json()
    assert "app_name" in body
    assert "environment" in body