"""Kafka consumer that persists frame embeddings into Qdrant."""

import base64
import json
from typing import Iterator

import cv2
import numpy as np
from kafka import KafkaConsumer
from PIL import Image

from ..config import get_settings
from ..logging_config import get_logger
from ..metrics import FRAMES_PROCESSED, INGESTION_LATENCY, KAFKA_MESSAGES
from ..models import BaseEncoder, CLIPEncoder, TensorRTEncoder
from ..storage import QdrantStore

logger = get_logger(__name__)


def _build_encoder() -> BaseEncoder:
    settings = get_settings()
    if settings.tensorrt_enabled:
        return TensorRTEncoder(
            engine_path=settings.tensorrt_engine_path,
            model_name=settings.clip_model,
            device=settings.device,
        )
    return CLIPEncoder(model_name=settings.clip_model, device=settings.device)


class FrameConsumer:
    def __init__(self, encoder: BaseEncoder | None = None, store: QdrantStore | None = None) -> None:
        settings = get_settings()
        self.settings = settings
        self.topic = settings.kafka_frames_topic
        self.encoder = encoder or _build_encoder()
        self.store = store or QdrantStore(vector_size=self.encoder.vector_size)
        self._consumer = KafkaConsumer(
            self.topic,
            bootstrap_servers=settings.kafka_bootstrap_servers.split(","),
            group_id=settings.kafka_consumer_group,
            auto_offset_reset="earliest",
            enable_auto_commit=False,
            max_poll_records=settings.batch_size,
            value_deserializer=lambda v: json.loads(v.decode("utf-8")),
        )
        logger.info("Kafka consumer ready on topic=%s group=%s", self.topic, settings.kafka_consumer_group)

    def _decode(self, msg: dict) -> Image.Image:
        raw = base64.b64decode(msg["jpeg_b64"])
        arr = np.frombuffer(raw, dtype=np.uint8)
        bgr = cv2.imdecode(arr, cv2.IMREAD_COLOR)
        return Image.fromarray(cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB))

    def process_message(self, msg: dict) -> None:
        with INGESTION_LATENCY.time():
            try:
                image = self._decode(msg)
                vector = self.encoder.encode_image(image)
                self.store.upsert(
                    vector=vector,
                    payload={
                        "video_id": msg["video_id"],
                        "video_path": msg["video_path"],
                        "frame_index": msg["frame_index"],
                        "timestamp_sec": msg["timestamp_sec"],
                        "created_at": msg["created_at"],
                    },
                )
                FRAMES_PROCESSED.labels(status="ok").inc()
                KAFKA_MESSAGES.labels(topic=self.topic, status="processed").inc()
            except Exception as exc:
                logger.exception("Failed to process message: %s", exc)
                FRAMES_PROCESSED.labels(status="error").inc()
                KAFKA_MESSAGES.labels(topic=self.topic, status="error").inc()

    def run_forever(self) -> None:
        logger.info("Consumer loop started")
        while True:
            records = self._consumer.poll(timeout_ms=1000, max_records=self.settings.batch_size)
            if not records:
                continue
            for _, batch in records.items():
                for record in batch:
                    self.process_message(record.value)
                self._consumer.commit()
        # unreachable; consumer.close() is intentionally skipped for clean shutdown

    def messages(self) -> Iterator[dict]:  # pragma: no cover
        for record in self._consumer:
            yield record.value
