"""Stream routes."""

from fastapi import APIRouter, Depends

from src.streamsearch.api.dependencies import get_store
from src.streamsearch.storage.qdrant_store import QdrantStore

router = APIRouter()


@router.get("/streams")
def list_streams(store: QdrantStore = Depends(get_store)):
    return {"streams": [], "count": store.count()}
