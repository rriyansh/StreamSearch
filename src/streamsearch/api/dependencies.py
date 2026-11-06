"""API dependencies."""

from functools import lru_cache

from src.streamsearch.config import load_config
from src.streamsearch.models.clip_encoder import CLIPEncoder
from src.streamsearch.storage.qdrant_store import QdrantStore


@lru_cache
def get_config():
    return load_config()


@lru_cache
def get_store() -> QdrantStore:
    config = get_config()
    storage = config["storage"]
    return QdrantStore(
        host=storage["qdrant_host"],
        port=int(storage["qdrant_port"]),
        collection=storage["qdrant_collection"],
        api_key=storage.get("qdrant_api_key"),
        vector_size=int(config["models"]["embedding_dim"]),
    )


@lru_cache
def get_encoder() -> CLIPEncoder:
    config = get_config()
    models = config["models"]
    return CLIPEncoder(
        model_name=models["clip_model_name"],
        device=models["clip_device"],
    )
