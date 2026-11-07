"""Frame iteration from a video file or stream."""

from dataclasses import dataclass
from pathlib import Path
from typing import Iterator

import cv2
import numpy as np

from ..logging_config import get_logger

logger = get_logger(__name__)


@dataclass
class Frame:
    index: int
    timestamp_sec: float
    image: np.ndarray  # BGR, as returned by OpenCV


class VideoReader:
    """Iterate frames of a video at a configurable interval."""

    def __init__(self, source: str | Path, interval_sec: float = 2.0) -> None:
        self.source = str(source)
        self.interval_sec = interval_sec

    def __iter__(self) -> Iterator[Frame]:
        cap = cv2.VideoCapture(self.source)
        if not cap.isOpened():
            raise RuntimeError(f"Cannot open video source: {self.source}")

        try:
            fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
            skip = max(1, int(round(fps * self.interval_sec)))
            idx = 0
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                if idx % skip == 0:
                    yield Frame(index=idx, timestamp_sec=idx / fps, image=frame)
                idx += 1
        finally:
            cap.release()
