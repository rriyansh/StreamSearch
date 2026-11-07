"""FastAPI application entrypoint."""

from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import make_asgi_app

from ..config import get_settings
from ..logging_config import setup_logging
from .middleware import RequestLoggingMiddleware
from .routes import health, ingest, search, streams


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    setup_logging()
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title=settings.app_name,
        version="1.0.0",
        description="Real-time multimodal video search engine",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(RequestLoggingMiddleware)

    app.include_router(health.router)
    app.include_router(search.router, prefix="/search", tags=["search"])
    app.include_router(ingest.router, prefix="/ingest", tags=["ingest"])
    app.include_router(streams.router, prefix="/streams", tags=["streams"])

    # Mount /metrics as a sub-app (not a normal router)
    app.mount("/metrics", make_asgi_app())

    return app


app = create_app()
