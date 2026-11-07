"""Configuration management using pydantic-settings."""

from functools import lru_cache
from typing import List, Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="SS_",
        extra="ignore",
        case_sensitive=False,
    )

    # App
    app_name: str = "StreamSearch"
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"
    debug: bool = False

    # Qdrant
    qdrant_host: str = "localhost"
    qdrant_port: int = 6333
    qdrant_collection: str = "video_frames"
    qdrant_vector_size: int = 512
    qdrant_api_key: str | None = None

    # Kafka
    kafka_bootstrap_servers: str = "localhost:9092"
    kafka_frames_topic: str = "video-frames"
    kafka_consumer_group: str = "streamsearch-worker"

    # CLIP
    clip_model: str = "ViT-B/32"
    device: Literal["auto", "cuda", "cpu"] = "auto"

    # Ingestion
    frame_interval_sec: float = 2.0
    scene_detection_enabled: bool = True
    scene_threshold: float = 30.0
    batch_size: int = 32

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    cors_origins: List[str] = Field(default_factory=lambda: ["*"])

    # Redis cache
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    cache_ttl: int = 300

    # TensorRT
    tensorrt_enabled: bool = False
    tensorrt_engine_path: str = "/models/clip.engine"

    def resolved_device(self) -> str:
        if self.device == "auto":
            try:
                import torch
                return "cuda" if torch.cuda.is_available() else "cpu"
            except ImportError:
                return "cpu"
        return self.device


@lru_cache
def get_settings() -> Settings:
    return Settings()
