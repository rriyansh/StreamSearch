"""Search endpoint."""

import time

from fastapi import APIRouter, Depends, HTTPException

from ...logging_config import get_logger
from ...metrics import SEARCH_LATENCY, SEARCH_REQUESTS
from ...storage import QdrantStore, QueryCache
from ..dependencies import get_cache, get_encoder, get_store
from ..schemas import SearchHit, SearchRequest, SearchResponse

logger = get_logger(__name__)

router = APIRouter()


@router.post("", response_model=SearchResponse)
def search(
    req: SearchRequest,
    encoder=Depends(get_encoder),
    store: QdrantStore = Depends(get_store),
    cache: QueryCache = Depends(get_cache),
) -> SearchResponse:
    SEARCH_REQUESTS.inc()
    cache_key = {
        "q": req.query,
        "limit": req.limit,
        "vid": req.video_id,
        "min": req.min_timestamp,
        "max": req.max_timestamp,
    }

    cached = cache.get("search", cache_key)
    if cached is not None:
        return SearchResponse(**cached, cached=True)

    with SEARCH_LATENCY.time():
        try:
            vector = encoder.encode_text(req.query)
            hits = store.search(
                query_vector=vector,
                limit=req.limit,
                video_id=req.video_id,
                min_timestamp=req.min_timestamp,
                max_timestamp=req.max_timestamp,
            )
        except Exception as exc:
            logger.exception("Search failed")
            raise HTTPException(status_code=500, detail=str(exc)) from exc

    results = [
        SearchHit(
            id=h["id"],
            score=round(h["score"], 6),
            video_id=h["payload"].get("video_id"),
            video_path=h["payload"].get("video_path"),
            timestamp_sec=h["payload"].get("timestamp_sec"),
            frame_index=h["payload"].get("frame_index"),
        )
        for h in hits
    ]
    response = SearchResponse(query=req.query, count=len(results), results=results)
    cache.set("search", cache_key, response.model_dump())
    return response
