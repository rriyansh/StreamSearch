"""Prometheus metrics for the StreamSearch API."""

from prometheus_client import Counter, Histogram, Gauge

INGEST_REQUESTS = Counter("streamsearch_ingest_requests_total", "Total ingest requests", ["status"])
SEARCH_REQUESTS = Counter("streamsearch_search_requests_total", "Total search requests", ["status"])
EMBEDDING_ENCODE_DURATION = Histogram(
    "streamsearch_embedding_encode_seconds",
    "Time spent encoding embeddings",
)
ACTIVE_STREAMS = Gauge("streamsearch_active_streams", "Number of active video streams")
VECTOR_COUNT = Gauge("streamsearch_vector_count", "Number of vectors in Qdrant", ["collection"])
