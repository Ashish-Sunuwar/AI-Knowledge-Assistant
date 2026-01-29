from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_cors_preflight_contains_headers():
    res = client.options(
        "/api/v1/ask",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "POST",
        },
    )
    # CORSMiddleware usually returns 200 on OPTIONS with proper headers
    assert res.status_code in (200, 204)
    assert "access-control-allow-origin" in {k.lower(): v for k, v in res.headers.items()}