"""Orchestrates: video → frames → Kafka → worker → Qdrant."""

import uuid
from pathlib import Path

from ..config import get_settings
from ..logging_config import get_logger
from .kafka_producer import FrameProducer
from .scene_detector import SceneDetector
from .video_reader import VideoReader

logger = get_logger(__name__)


class IngestionPipeline:
    def __init__(self, producer: FrameProducer | None = None) -> None:
        self.settings = get_settings()
        self.producer = producer or FrameProducer()
        self.detector = (
            SceneDetector(threshold=self.settings.scene_threshold)
            if self.settings.scene_detection_enabled
            else None
        )

    def ingest_video(self, video_path: str | Path) -> dict:
        video_path = Path(video_path)
        if not video_path.exists():
            raise FileNotFoundError(video_path)

        video_id = str(uuid.uuid4())
        reader = VideoReader(video_path, interval_sec=self.settings.frame_interval_sec)
        sent = 0
        skipped = 0

        for frame in reader:
            if self.detector is not None and not self.detector.is_new_scene(frame):
                skipped += 1
                continue
            self.producer.send_frame(
                video_id=video_id,
                video_path=str(video_path),
                frame_index=frame.index,
                timestamp_sec=frame.timestamp_sec,
                bgr_image=frame.image,
            )
            sent += 1

        self.producer.flush()
        logger.info("Ingested video_id=%s sent=%d skipped=%d", video_id, sent, skipped)
        return {"video_id": video_id, "frames_sent": sent, "frames_skipped": skipped}
