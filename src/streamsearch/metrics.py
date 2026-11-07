"""Prometheus metrics."""

from prometheus_client import Counter, Histogram, Gauge

# Ingestion
FRAMES_PROCESSED = Counter(
    "streamsearch_frames_processed_total",
    "Total frames processed",
    ["status"],
)
INGESTION_LATENCY = Histogram(
    "streamsearch_ingestion_latency_seconds",
    "Per-frame ingestion latency",
)

# Search
SEARCH_REQUESTS = Counter(
    "streamsearch_search_requests_total",
    "Total search requests",
)
SEARCH_LATENCY = Histogram(
    "streamsearch_search_latency_seconds",
    "Search request latency",
)

# Vector store
VECTOR_COUNT = Gauge(
    "streamsearch_vector_count",
    "Number of vectors in the collection",
)

# Kafka
KAFKA_MESSAGES = Counter(
    "streamsearch_kafka_messages_total",
    "Kafka messages processed",
    ["topic", "status"],
)
