"""Ingest routes."""

from fastapi import APIRouter, Depends, BackgroundTasks

from src.streamsearch.api.dependencies import get_store
from src.streamsearch.api.schemas import IngestRequest, IngestResponse
from src.streamsearch.ingestion.pipeline import IngestionPipeline
from src.streamsearch.storage.qdrant_store import QdrantStore

router = APIRouter()


@router.post("/ingest", response_model=IngestResponse)
def ingest(
    request: IngestRequest,
    background_tasks: BackgroundTasks,
    store: QdrantStore = Depends(get_store),
):
    pipeline = IngestionPipeline(store=store)
    result = pipeline.ingest_video(request.video_path, stream_id=request.stream_id)
    return IngestResponse(
        stream_id=result.stream_id,
        video_path=result.video_path,
        scenes=result.scenes,
        vectors=result.vectors,
    )
