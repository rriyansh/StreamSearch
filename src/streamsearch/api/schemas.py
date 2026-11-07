"""Pydantic request/response schemas."""

from typing import Any

from pydantic import BaseModel, Field


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=500)
    limit: int = Field(default=10, ge=1, le=100)
    video_id: str | None = None
    min_timestamp: float | None = None
    max_timestamp: float | None = None


class SearchHit(BaseModel):
    id: str
    score: float
    video_id: str | None = None
    video_path: str | None = None
    timestamp_sec: float | None = None
    frame_index: int | None = None


class SearchResponse(BaseModel):
    query: str
    count: int
    cached: bool = False
    results: list[SearchHit]


class IngestRequest(BaseModel):
    video_path: str = Field(..., description="Absolute or container-relative path to a video file")


class IngestResponse(BaseModel):
    video_id: str
    frames_sent: int
    frames_skipped: int


class StreamRegisterRequest(BaseModel):
    stream_url: str = Field(..., description="RTSP/HLS URL of live feed")
    label: str | None = None


class StreamInfo(BaseModel):
    id: str
    stream_url: str
    label: str | None
    status: str
    created_at: str


class HealthResponse(BaseModel):
    status: str
    components: dict[str, Any]
