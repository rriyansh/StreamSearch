from streamsearch.config import Settings


def test_defaults():
    s = Settings()
    assert s.qdrant_port == 6333
    assert s.qdrant_vector_size == 512
    assert s.clip_model == "ViT-B/32"


def test_override_via_env(monkeypatch):
    monkeypatch.setenv("SS_QDRANT_PORT", "9999")
    s = Settings()
    assert s.qdrant_port == 9999
