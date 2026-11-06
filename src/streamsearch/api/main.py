"""FastAPI application entrypoint."""

from fastapi import FastAPI

from src.streamsearch.api.dependencies import get_store, get_encoder
from src.streamsearch.api.middleware import RequestLoggingMiddleware
from src.streamsearch.api.routes import health, ingest, search, streams
from src.streamsearch.logging_config import configure_logging
from src.streamsearch.metrics import INGEST_REQUESTS, SEARCH_REQUESTS

configure_logging()

app = FastAPI(title="StreamSearch", version="0.1.0")

app.add_middleware(RequestLoggingMiddleware)

app.include_router(health.router, tags=["health"])
app.include_router(ingest.router, tags=["ingest"])
app.include_router(search.router, tags=["search"])
app.include_router(streams.router, tags=["streams"])

# Expose metrics for prometheus scraping via middleware if desired
app.state.ingest_requests = INGEST_REQUESTS
app.state.search_requests = SEARCH_REQUESTS
