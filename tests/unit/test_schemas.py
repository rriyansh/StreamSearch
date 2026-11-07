import pytest
from pydantic import ValidationError

from streamsearch.api.schemas import SearchRequest


def test_search_request_valid():
    req = SearchRequest(query="cat", limit=3)
    assert req.limit == 3


def test_search_request_rejects_empty_query():
    with pytest.raises(ValidationError):
        SearchRequest(query="")


def test_search_request_rejects_huge_limit():
    with pytest.raises(ValidationError):
        SearchRequest(query="x", limit=1000)
