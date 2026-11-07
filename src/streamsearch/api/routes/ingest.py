"""Trigger ingestion of an offline video file."""

from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, HTTPException

from ...ingestion import IngestionPipeline
from ...logging_config import get_logger
from ..schemas import IngestRequest, IngestResponse

logger = get_logger(__name__)
router = APIRouter()


def _run_ingest(video_path: str) -> None:
    try:
        IngestionPipeline().ingest_video(video_path)
    except Exception as exc:
        logger.exception("Background ingestion failed: %s", exc)


@router.post("/video", response_model=IngestResponse)
def ingest_video(req: IngestRequest, background: BackgroundTasks) -> IngestResponse:
    if not Path(req.video_path).exists():
        raise HTTPException(status_code=404, detail=f"Video not found: {req.video_path}")
    try:
        result = IngestionPipeline().ingest_video(req.video_path)
    except Exception as exc:
        logger.exception("Ingestion failed")
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    return IngestResponse(**result)
