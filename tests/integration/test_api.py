import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client(monkeypatch):
    # Avoid touching real Qdrant/CLIP
    from streamsearch.api import main as api_main
    from streamsearch.api import dependencies as deps

    class FakeEncoder:
        vector_size = 4

        def encode_text(self, _text):
            import numpy as np
            v = np.ones(4, dtype="float32")
            return v / np.linalg.norm(v)

    class FakeStore:
        def count(self):
            return 0

        def search(self, **_kwargs):
            return []

    deps.get_encoder.cache_clear()
    deps.get_store.cache_clear()
    deps.get_cache.cache_clear()

    api_main.app.dependency_overrides[deps.get_encoder] = lambda: FakeEncoder()
    api_main.app.dependency_overrides[deps.get_store] = lambda: FakeStore()
    from streamsearch.storage import QueryCache
    api_main.app.dependency_overrides[deps.get_cache] = lambda: QueryCache()

    return TestClient(api_main.app)


def test_health_live(client):
    r = client.get("/health/live")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_search_empty_results(client):
    r = client.post("/search", json={"query": "cat", "limit": 3})
    assert r.status_code == 200
    body = r.json()
    assert body["query"] == "cat"
    assert body["count"] == 0
