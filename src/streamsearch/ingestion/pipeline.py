"""End-to-end video ingestion pipeline."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

from src.streamsearch.ingestion.scene_detector import SceneDetector
from src.streamsearch.ingestion.video_reader import Frame, VideoReader
from src.streamsearch.models.clip_encoder import CLIPEncoder
from src.streamsearch.storage.qdrant_store import QdrantStore


@dataclass
class IngestResult:
    stream_id: str
    video_path: str
    scenes: int
    vectors: int


class IngestionPipeline:
    """Read a video, detect scenes, encode frames, and store embeddings."""

    def __init__(
        self,
        encoder: Optional[CLIPEncoder] = None,
        store: Optional[QdrantStore] = None,
        scene_threshold: float = 0.3,
        min_scene_duration: float = 2.0,
        sample_rate: float = 1.0,
    ) -> None:
        self.encoder = encoder or CLIPEncoder()
        self.store = store or QdrantStore()
        self.scene_detector = SceneDetector(
            threshold=scene_threshold,
            min_duration=min_scene_duration,
        )
        self.sample_rate = sample_rate

    def ingest_video(self, video_path: str | Path, stream_id: Optional[str] = None) -> IngestResult:
        video_path = Path(video_path)
        stream_id = stream_id or video_path.stem

        with VideoReader(str(video_path), sample_rate=self.sample_rate) as reader:
            frames = list(reader)

        scenes = self.scene_detector.detect(frames)

        points = []
        vector_count = 0
        for scene in scenes:
            mid = (scene["start"] + scene["end"]) / 2
            image = self._frame_at(frames, mid)
            if image is None:
                continue
            embedding = self.encoder.encode(image)
            point = {
                "id": f"{stream_id}:{scene['start']:.3f}",
                "vector": embedding.tolist(),
                "payload": {
                    "stream_id": stream_id,
                    "video": str(video_path),
                    "start": scene["start"],
                    "end": scene["end"],
                },
            }
            points.append(point)
            vector_count += 1

        if points:
            self.store.upsert(points)

        return IngestResult(
            stream_id=stream_id,
            video_path=str(video_path),
            scenes=len(scenes),
            vectors=vector_count,
        )

    @staticmethod
    def _frame_at(frames: List[Frame], timestamp: float) -> Frame | None:
        if not frames:
            return None
        return min(frames, key=lambda f: abs(f.timestamp - timestamp))


def ingest_video(video_path: str | Path, stream_id: Optional[str] = None) -> IngestResult:
    """Module-level helper to ingest a single video."""
    pipeline = IngestionPipeline()
    return pipeline.ingest_video(video_path, stream_id=stream_id)
