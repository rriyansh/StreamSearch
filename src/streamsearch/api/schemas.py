"""API request/response schemas."""

from pydantic import BaseModel, Field


class IngestRequest(BaseModel):
    video_path: str = Field(..., description="Path to the video file")
    stream_id: str | None = Field(None, description="Optional stream identifier")


class IngestResponse(BaseModel):
    stream_id: str
    video_path: str
    scenes: int
    vectors: int


class SearchRequest(BaseModel):
    query: str = Field(..., description="Text or image query")
    stream_id: str | None = Field(None, description="Optional stream filter")
    limit: int = Field(10, ge=1, le=100)


class SearchResult(BaseModel):
    id: str
    score: float
    payload: dict


class SearchResponse(BaseModel):
    results: list[SearchResult]


class HealthResponse(BaseModel):
    status: str
    version: str = "0.1.0"
