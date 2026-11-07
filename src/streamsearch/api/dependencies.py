"""Shared FastAPI dependencies (singletons)."""

from functools import lru_cache

from ..models import CLIPEncoder
from ..storage import QdrantStore, QueryCache


@lru_cache
def get_encoder() -> CLIPEncoder:
    from ..config import get_settings
    s = get_settings()
    return CLIPEncoder(model_name=s.clip_model, device=s.device)


@lru_cache
def get_store() -> QdrantStore:
    return QdrantStore(vector_size=get_encoder().vector_size)


@lru_cache
def get_cache() -> QueryCache:
    return QueryCache()
    
