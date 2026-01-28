import json
from pathlib import Path
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)
EVAL_FILE = Path("tests/evals/qa_regression_set.json")


def test_rag_regression_suite():
    cases = json.loads(EVAL_FILE.read_text())

    for case in cases:
        res = client.post("/api/v1/ask", json={"question": case["question"]})
        assert res.status_code == 200

        body = res.json()
        assert body["success"] is True

        answer = body["data"]["answer"]
        used_sources = body["data"].get("used_sources", [])
        sources = body["data"].get("sources", [])

        if case["expect_idk"]:
            assert answer == "I don't know."
            assert used_sources == []
            continue

        # Non-IDK assertions
        assert isinstance(answer, str)
        assert len(answer.strip()) > 0
        assert answer != "I don't know."

        # Must cite sources
        assert len(used_sources) > 0

        valid_chunk_ids = {s["chunk_id"] for s in sources}
        assert all(u in valid_chunk_ids for u in used_sources)

        # Expected facts must appear
        for keyword in case["expected_answer_contains"]:
            assert keyword.lower() in answer.lower()

        # Expected sources must be cited
        for expected in case["expected_used_sources"]:
            assert expected in used_sources