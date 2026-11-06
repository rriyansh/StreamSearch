"""Unit tests for API schemas."""

from pydantic import ValidationError
from src.streamsearch.api.schemas import SearchRequest, IngestRequest


def test_search_request_defaults():
    req = SearchRequest(query="a person walking")
    assert req.query == "a person walking"
    assert req.limit == 10


def test_search_request_limit_bounds():
    req = SearchRequest(query="x", limit=50)
    assert req.limit == 50


def test_ingest_request_optional_stream():
    req = IngestRequest(video_path="/tmp/video.mp4")
    assert req.stream_id is None
