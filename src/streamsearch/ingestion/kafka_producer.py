"""Kafka producer that fans out frame messages."""

import base64
import json
import uuid
from datetime import datetime, timezone

import cv2
from kafka import KafkaProducer

from ..config import get_settings
from ..logging_config import get_logger
from ..metrics import KAFKA_MESSAGES

logger = get_logger(__name__)


class FrameProducer:
    def __init__(self) -> None:
        settings = get_settings()
        self.topic = settings.kafka_frames_topic
        self._producer = KafkaProducer(
            bootstrap_servers=settings.kafka_bootstrap_servers.split(","),
            acks="all",
            retries=5,
            linger_ms=20,
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        )
        logger.info("Kafka producer connected: %s", settings.kafka_bootstrap_servers)

    def send_frame(
        self,
        video_id: str,
        video_path: str,
        frame_index: int,
        timestamp_sec: float,
        bgr_image,
    ) -> None:
        ok, buf = cv2.imencode(".jpg", bgr_image, [cv2.IMWRITE_JPEG_QUALITY, 85])
        if not ok:
            logger.error("JPEG encode failed for frame %s", frame_index)
            KAFKA_MESSAGES.labels(topic=self.topic, status="encode_error").inc()
            return

        payload = {
            "message_id": str(uuid.uuid4()),
            "video_id": video_id,
            "video_path": video_path,
            "frame_index": frame_index,
            "timestamp_sec": round(timestamp_sec, 3),
            "jpeg_b64": base64.b64encode(buf.tobytes()).decode("ascii"),
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        self._producer.send(self.topic, payload)
        KAFKA_MESSAGES.labels(topic=self.topic, status="sent").inc()

    def flush(self) -> None:
        self._producer.flush()

    def close(self) -> None:
        self._producer.flush(timeout=10)
        self._producer.close(timeout=10)
